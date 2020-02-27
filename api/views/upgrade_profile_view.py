import re
import traceback
from _decimal import Decimal
from datetime import datetime

from authorizenet import apicontractsv1
from authorizenet.apicontrollers import ARBCreateSubscriptionController
from rest_framework import viewsets
from rest_framework.decorators import action
from authorizenet.constants import constants
from authorization.views.checkSubscription import CheckSubscription
from api.serializers import *
from rest_framework.response import Response
from houzes_api import settings as AUTHORIZE_DOT_NET_CONFIG

AUTHORIZE_DOT_NET_MERCHANT_AUTH_NAME = getattr(AUTHORIZE_DOT_NET_CONFIG, 'AUTHORIZE_DOT_NET_MERCHANT_AUTH_NAME', None)
AUTHORIZE_DOT_NET_MERCHANT_AUTH_TRANSACTION_KEY = getattr(AUTHORIZE_DOT_NET_CONFIG, "AUTHORIZE_DOT_NET_MERCHANT_AUTH_TRANSACTION_KEY", None)


class UpgradeProfileViewSet(viewsets.ModelViewSet):
    queryset = UpgradeProfile.objects.all()
    serializer_class = UpgradeProfileSerializer

    def create(self, request, *args, **kwargs):
        response_data = {'status': False, 'data': {}, 'message' :''}
        try:
            plan_id = request.data['plan']
            card_number = request.data['card_number']
            expiration_date = request.data['expiration_date']
            card_code = request.data['card_code']
            is_save = request.data['is_save']
            card_name = request.data['card_name']

        except:
            plan_id = request.body['plan']
            card_number = request.body['card_number']
            expiration_date = request.body['expiration_date']
            card_code = request.body['card_code']
            is_save = request.body['is_save']
            card_name = request.body['card_name']

        try:
            plan = Plans.objects.get(id = plan_id)
        except Exception as e:
            traceback.print_exc()
            response_data['status'] = False
            response_data['message'] = 'This package is currently not available'
            return Response(response_data)
        user = User.objects.get(id = request.user.id)
        if user.is_admin == False :
            response_data['status'] = False
            response_data['message'] = 'This feature is only available for team leader'
            return Response(response_data)

        upgrade_profile = UpgradeProfile.objects.filter(user = user).first()
        # MONTHLY SUBSCRIPTION GOES HERE
        subscription_response = UpgradeProfileViewSet.create_subscription(self,upgrade_profile,plan_id,card_number,expiration_date)
        try:
            subscriptionId = subscription_response["subscriptionId"]
            if not CheckSubscription.get_subscription_status(self,subscriptionId):
                response_data['status'] = False
                response_data['data'] = {}
                response_data['message'] = 'This transaction is not approved'
                return Response(response_data)

        except Exception as exc:
            response_data['status'] = False
            response_data['data'] = {}
            response_data['message'] = 'This transaction is not approved. '+str(exc)
            return Response(response_data)


        if subscription_response['messages']['resultCode'] == 'Error':
            response_data['status'] = False
            response_data['data'] = {}
            response_data['message'] = subscription_response['messages']['message']['text']
            return Response(response_data)

        if upgrade_profile:
            upgrade_profile.coin = float(upgrade_profile.coin)+0
            upgrade_profile.plan = plan
            print(':::::::::::::::::::::::::::::::::::::')
            print(type(subscription_response["subscriptionId"]))
            upgrade_profile.subscriptionId = subscription_response["subscriptionId"]
            # upgrade_profile.refId = subscription_response["refId"]
            upgrade_profile.save()
            upgrade_profile_serializer = UpgradeProfileSerializer(upgrade_profile)

            user.upgrade = True
            user.save()

            #IF UPGRADE PROFILE TO "TEAM" THEN REACTIVATE HIS TEAM MEMBERS
            if upgrade_profile.plan.id == 2:
                User.objects.filter(invited_by=user.id).update(is_active = True)

            upgrade_history = UpgradeHistory()
            upgrade_history.upgrade_profile = upgrade_profile
            upgrade_history.plan = plan
            upgrade_history.transaction_coin = plan.plan_coin
            upgrade_history.save()

            # billing_card_info = BillingCardInfo()
            # billing_card_info.user = user
            # billing_card_info.card_name = None
            # billing_card_info.card_number = card_number
            # billing_card_info.card_code = card_code
            # billing_card_info.exp_date = expiration_date
            # billing_card_info.is_save = is_save
            # billing_card_info.card_name = card_name
            # billing_card_info.save()

            if BillingCardInfo.objects.filter(user__id=user.id, card_number=card_number).first():
                if is_save:
                    BillingCardInfo.objects.filter(user=user, card_number=card_number).update(card_name=card_name,
                                                                                                 card_code=card_code,
                                                                                                 exp_date=expiration_date,
                                                                                                 is_save=is_save)
                else:
                    BillingCardInfo.objects.filter(user=user, card_number=card_number).update(card_name=card_name,
                                                                                                    card_code=card_code,
                                                                                                    exp_date=expiration_date)
            else:
                billing_card_info = BillingCardInfo()
                billing_card_info.user = user
                billing_card_info.card_number = card_number
                billing_card_info.card_code = card_code
                billing_card_info.exp_date = expiration_date
                billing_card_info.card_name = card_name
                billing_card_info.is_save = is_save
                billing_card_info.save()

            response_data['status'] = True
            response_data['data'] = upgrade_profile_serializer.data
            response_data['message'] = '“Congratulations” Profile is upgraded. Start driving & adding HouZes'
        else:
            upgrade_profile = UpgradeProfile()
            upgrade_profile.user = user
            upgrade_profile.coin = 0.0
            upgrade_profile.subscriptionId = subscription_response["subscriptionId"]
            # upgrade_profile.refId = subscription_response["refId"]
            upgrade_profile.plan = plan
            upgrade_profile.save()
            upgrade_profile_serializer = UpgradeProfileSerializer(upgrade_profile)

            user.upgrade = True
            user.save()

            upgrade_history = UpgradeHistory()
            upgrade_history.upgrade_profile = upgrade_profile
            upgrade_history.plan = plan
            upgrade_history.transaction_coin = plan.plan_coin
            upgrade_history.save()

            response_data['status'] = True
            response_data['data'] = upgrade_profile_serializer.data
            response_data['message'] = '“Congratulations” Profile is upgraded. Start driving & adding HouZes'

        return Response(response_data)


    @action(detail=False, methods=['GET'], url_path='user-details')
    def get_profile_upgrade_status_by_user(self, request, *args, **kwargs):
        response_data = {'status': False, 'data': {}, 'message' :''}
        user = User.objects.get(id=request.user.id)
        if user.upgrade == False :
            response_data['status'] = False
            response_data['message'] = 'The user profile in not upgraded'
            return Response(response_data)

        upgrade_profile = UpgradeProfile.objects.filter(user = user).first()

        if upgrade_profile:
            upgrade_profile_serializer = UpgradeProfileSerializer(upgrade_profile)

        else:
            response_data['status'] = False
            response_data['message'] = 'The user profile in not upgraded'
            return Response(response_data)

        return Response(upgrade_profile_serializer.data)

    def create_subscription(self,upgrade_profile,plan_id,card_number,expiration_date):
        plan = Plans.objects.get(id = plan_id)
        firstName = User.objects.get(id=upgrade_profile.user.id).first_name
        lastName = User.objects.get(id=upgrade_profile.user.id).last_name
        cardNumber = card_number
        expirationDate = expiration_date
        subscriptionName = plan.plan_name

        # amount = float(plan.plan_coin)
        amount = 0.15
        totalOccurrences =1
        days = 30
        startDate = datetime.now()
        # Setting the merchant details
        merchantAuth = apicontractsv1.merchantAuthenticationType()
        merchantAuth.name = AUTHORIZE_DOT_NET_MERCHANT_AUTH_NAME
        merchantAuth.transactionKey = AUTHORIZE_DOT_NET_MERCHANT_AUTH_TRANSACTION_KEY
        # Setting payment schedule
        paymentschedule = apicontractsv1.paymentScheduleType()
        paymentschedule.interval = apicontractsv1.paymentScheduleTypeInterval()  # apicontractsv1.CTD_ANON() #modified by krgupta
        paymentschedule.interval.length = days
        paymentschedule.interval.unit = apicontractsv1.ARBSubscriptionUnitEnum.days
        paymentschedule.startDate = startDate
        paymentschedule.totalOccurrences = totalOccurrences
        paymentschedule.trialOccurrences = 0
        # Giving the credit card info
        creditcard = apicontractsv1.creditCardType()
        creditcard.cardNumber = cardNumber
        creditcard.expirationDate = expirationDate
        payment = apicontractsv1.paymentType()
        payment.creditCard = creditcard
        # Setting billing information
        billto = apicontractsv1.nameAndAddressType()
        billto.firstName = firstName
        billto.lastName = lastName
        # Setting subscription details
        subscription = apicontractsv1.ARBSubscriptionType()
        subscription.name = subscriptionName
        subscription.paymentSchedule = paymentschedule
        TWOPLACES = Decimal(10) ** -2
        subscription.amount = Decimal(amount).quantize(TWOPLACES)
        subscription.trialAmount = Decimal('0.00')
        subscription.billTo = billto
        subscription.payment = payment

        # Creating the request
        request = apicontractsv1.ARBCreateSubscriptionRequest()
        request.merchantAuthentication = merchantAuth
        request.subscription = subscription
        # Creating and executing the controller
        controller = ARBCreateSubscriptionController(request)
        controller.setenvironment(constants.PRODUCTION)
        controller.execute()
        # Getting the response
        response = controller.getresponse()
        json_response = to_dict(response)
        print(json_response)
        return (json_response)

def to_dict(element):
    ret = {}
    if element.getchildren() == []:
        return element.text
    else:
        for elem in element.getchildren():
            subdict = to_dict(elem)
            ret[re.sub('{.*}', '', elem.tag)] = subdict
    return ret