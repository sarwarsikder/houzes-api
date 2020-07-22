import re
import traceback
from _decimal import Decimal
from datetime import datetime, timedelta
import calendar

from authorizenet import apicontractsv1
from authorizenet.apicontrollers import ARBCreateSubscriptionController, ARBCancelSubscriptionController, \
    createTransactionController, ARBUpdateSubscriptionController
from notifications.signals import notify
from rest_framework import viewsets
from rest_framework.decorators import action
from authorizenet.constants import constants
from authorization.views.checkSubscription import CheckSubscription
from api.serializers import *
from rest_framework.response import Response
from houzes_api import settings as AUTHORIZE_DOT_NET_CONFIG
from rest_framework import status

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
        if user.is_team_admin == False :
            response_data['status'] = False
            response_data['message'] = 'This feature is only available for team leader'
            return Response(response_data)

        upgrade_profile = UpgradeProfile.objects.filter(user = user).first()

        #CHARGE FOR FIRST MONTH
        first_month_amount = float(plan.plan_coin)
        # first_month_amount = 0.15
        charge_for_first_month_response = UpgradeProfileViewSet.charge_for_first_month(self, card_number, expiration_date, first_month_amount, card_code, card_name,user)
        if charge_for_first_month_response['messages']['resultCode'] == 'Error':
            response_data['status'] = False
            response_data['message'] = 'This transaction is not approved'
            return Response(response_data)
        elif charge_for_first_month_response['messages']['resultCode'] == 'Ok':
            if charge_for_first_month_response['transactionResponse']['responseCode']!='1':
                response_data['status'] = False
                response_data['message'] = 'This transaction is not approved'
                return Response(response_data)

        # IF SUBSCRIPTION EXISTS CANCEL THE SUBSCRIPTION
        if upgrade_profile.subscriptionId:
            UpgradeProfileViewSet.cancel_subscription(self, upgrade_profile)
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

        # Save applied coupon details


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

            notify.send(user, recipient=user, verb='upgraded the plan', action_object=upgrade_profile)

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

            notify.send(user, recipient=user, verb='upgraded the plan', action_object=upgrade_profile)

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

    @action(detail=False, methods=['POST'], url_path='add-coupon')
    def add_coupon_by_user(self, request, *args, **kwargs):
        response_data = {'status': False, 'data': None, 'message': ''}
        try:
            user = User.objects.get(id=request.user.id)
            coupon = request.data['coupon']
            affiliate_user = AffliateUser.objects.filter(code=coupon)
            if affiliate_user.exists():
                user.affiliate_user_id = affiliate_user[0].id
                user.save()
                upgrade_profile = UpgradeProfile.objects.filter(user=user).first()
                if upgrade_profile:
                    discount = user.affiliate_user.discount if user.affiliate_user.discount!=None else 0
                    amount = Plans.objects.get(id = upgrade_profile.plan.id).plan_coin
                    discounted_price = (amount / 100) * Decimal(discount)
                    total_amount = amount - discounted_price
                    if total_amount>0:
                        if not UpgradeProfileViewSet.update_subscription(self, upgrade_profile.subscriptionId,user, total_amount):
                            response_data['message'] = "Something went wrong. Please try again."
                            return Response(response_data, status=status.HTTP_200_OK)
                response_data['status'] = True
                response_data['message'] = "Coupon added successfully."
                user_serializer = UserSerializer(user)
                response_data['data'] = user_serializer.data
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data['status'] = False
                response_data['message'] = "Incorrect coupon code"
                return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            response_data['message'] = "Something went wrong. Please try again."
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_coupon_details(self, user, amount):
        response = {}
        try:
            response['success'] = False
            if user.affiliate_user:
                default_discount = user.affiliate_user.discount
                default_commission = user.affiliate_user.commission
                discount = (float(amount) / 100)*float(default_discount)
                total_discount = int(discount * 10**2) / 10**2
                total_amount = amount - total_discount
                commission = (float(total_amount) / 100) * float(default_commission)
                total_commission = int(commission * 10 ** 2) / 10 ** 2
                # total_discount = round((float(amount)/100)*float(default_discount), 2)
                # total_commission = round((float(amount)/100)*float(default_commission), 2)
                response['success'] = True
                response['discount'] = total_discount
                response['commission'] = total_commission
                response['total_amount'] = total_amount
        except Exception as e:
            response['success'] = False
        return response

    def create_subscription(self,upgrade_profile,plan_id,card_number,expiration_date):
        plan = Plans.objects.get(id = plan_id)
        firstName = User.objects.get(id=upgrade_profile.user.id).first_name
        lastName = User.objects.get(id=upgrade_profile.user.id).last_name
        cardNumber = card_number
        expirationDate = expiration_date
        subscriptionName = plan.plan_name

        amount = float(plan.plan_coin)
        total_amount = amount
        # amount = 0.15
        totalOccurrences =9999
        days = 30
        startDate = datetime.now() + timedelta(days=calendar.monthrange(datetime.now().year, datetime.now().month)[1])
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

        #Set the customer's identifying information
        customerData = apicontractsv1.customerType()
        customerData.type = "individual"
        customerData.id = str(upgrade_profile.user.id)
        customerData.email = User.objects.get(id = upgrade_profile.user.id).email

        # Create order information
        order = apicontractsv1.orderType()
        order.invoiceNumber = generate_shortuuid()
        order.description = "HouZes profile upgrade"

        # Get Coupon details
        coupon_reponse = UpgradeProfileViewSet.get_coupon_details(self, upgrade_profile.user, amount)
        if coupon_reponse['success']:
            amount = coupon_reponse['total_amount']

        # Setting subscription details
        subscription = apicontractsv1.ARBSubscriptionType()
        subscription.name = subscriptionName
        subscription.paymentSchedule = paymentschedule
        TWOPLACES = Decimal(10) ** -2
        subscription.amount = Decimal(amount).quantize(TWOPLACES)
        subscription.trialAmount = Decimal('0.00')
        subscription.billTo = billto
        subscription.order = order
        subscription.customer = customerData
        subscription.payment = payment

        # Creating the request
        request = apicontractsv1.ARBCreateSubscriptionRequest()
        request.merchantAuthentication = merchantAuth
        request.subscription = subscription
        # Creating and executing the controller
        controller = ARBCreateSubscriptionController(request)
        if getattr(settings, 'APP_ENV', None) == 'PROD':
            controller.setenvironment(constants.PRODUCTION)
        controller.execute()
        # Getting the response
        response = controller.getresponse()
        json_response = to_dict(response)
        if coupon_reponse['success']:
            total_discount = coupon_reponse['discount']
            total_commission = coupon_reponse['commission']
            coupon_user_form = {
                'user_id': upgrade_profile.user.id,
                'affiliate_user_id': upgrade_profile.user.affiliate_user_id,
                'discount': total_discount,
                'commission': total_commission,
                'total_amount': total_amount,
                'plan_id': plan_id,
                'activity_date': datetime.now(),
                'affiliate_is_active': upgrade_profile.user.affiliate_user.is_active
            }
            coupon_user = CouponUser(**coupon_user_form)
            coupon_user.save()
        return json_response

    def cancel_subscription(self, upgrade_profile):
        merchantAuth = apicontractsv1.merchantAuthenticationType()
        merchantAuth.name = AUTHORIZE_DOT_NET_MERCHANT_AUTH_NAME
        merchantAuth.transactionKey = AUTHORIZE_DOT_NET_MERCHANT_AUTH_TRANSACTION_KEY

        request = apicontractsv1.ARBCancelSubscriptionRequest()
        request.merchantAuthentication = merchantAuth
        request.refId = "cancel-subs"
        request.subscriptionId = upgrade_profile.subscriptionId

        controller = ARBCancelSubscriptionController(request)
        if getattr(settings, 'APP_ENV', None) == 'PROD':
            controller.setenvironment(constants.PRODUCTION)
        controller.execute()

        response = controller.getresponse()
        json_response = to_dict(response)
        print(json_response)
        return json_response

    def charge_for_first_month(self, card_number, expiration_date, amount, card_code, card_name,user):
        merchantAuth = apicontractsv1.merchantAuthenticationType()
        merchantAuth.name = AUTHORIZE_DOT_NET_MERCHANT_AUTH_NAME
        merchantAuth.transactionKey = AUTHORIZE_DOT_NET_MERCHANT_AUTH_TRANSACTION_KEY

        # Create the payment data for a credit card
        creditCard = apicontractsv1.creditCardType()
        creditCard.cardNumber = card_number
        creditCard.expirationDate = expiration_date
        creditCard.cardCode = card_code

        # Add the payment data to a paymentType object
        payment = apicontractsv1.paymentType()
        payment.creditCard = creditCard

        # Create order information
        order = apicontractsv1.orderType()
        order.invoiceNumber = generate_shortuuid()
        order.description = "HouZes first month subscription"

        # Set the customer's Bill To address
        customerAddress = apicontractsv1.customerAddressType()
        customerAddress.firstName = card_name
        customerAddress.lastName = ''
        # customerAddress.company = "REAL ACQUISITIONS"
        # customerAddress.address = "14 Main Street"
        # customerAddress.city = "Pecan Springs"
        # customerAddress.state = "TX"
        # customerAddress.zip = "44628"
        # customerAddress.country = "USA"

        # Set the customer's identifying information
        customerData = apicontractsv1.customerDataType()
        customerData.type = "individual"
        customerData.id = str(user.id)
        customerData.email = user.email

        # Create a transactionRequestType object and add the previous objects to it.
        transactionrequest = apicontractsv1.transactionRequestType()
        transactionrequest.transactionType = "authCaptureTransaction"
        TWOPLACES = Decimal(10) ** -2
        transactionrequest.amount = Decimal(amount).quantize(TWOPLACES)
        print(transactionrequest.amount)

        # order = apicontractsv1.orderType()
        # order.invoiceNumber = generate_shortuuid()
        # transactionrequest.order=order

        transactionrequest.payment = payment
        transactionrequest.x_po_num = generate_shortuuid()
        transactionrequest.x_duplicate_window = 0
        transactionrequest.order = order
        transactionrequest.customer = customerData
        transactionrequest.billTo = customerAddress

        # Assemble the complete transaction request
        createtransactionrequest = apicontractsv1.createTransactionRequest()
        createtransactionrequest.merchantAuthentication = merchantAuth
        createtransactionrequest.refId = "MerchantID-0001"
        createtransactionrequest.transactionRequest = transactionrequest
        # Create the controller
        createtransactioncontroller = createTransactionController(
            createtransactionrequest)
        if getattr(settings, 'APP_ENV', None) == 'PROD':
            createtransactioncontroller.setenvironment(constants.PRODUCTION)
        createtransactioncontroller.execute()

        response = createtransactioncontroller.getresponse()
        payment_response = to_dict(response)
        print(payment_response)
        return payment_response

    def update_subscription(self, subscriptionId,user, amount):
        merchantAuth = apicontractsv1.merchantAuthenticationType()
        merchantAuth.name = AUTHORIZE_DOT_NET_MERCHANT_AUTH_NAME
        merchantAuth.transactionKey = AUTHORIZE_DOT_NET_MERCHANT_AUTH_TRANSACTION_KEY

        # creditcard = apicontractsv1.creditCardType()
        # creditcard.cardNumber = "4111111111111111"
        # creditcard.expirationDate = "2020-12"

        # payment = apicontractsv1.paymentType()
        # payment.creditCard = creditcard

        # set profile information
        # profile = apicontractsv1.customerProfileIdType()
        # profile.customerProfileId = "121212"
        # profile.customerPaymentProfileId = "131313"
        # profile.customerAddressId = "141414"

        subscription = apicontractsv1.ARBSubscriptionType()
        # subscription.payment = payment
        # to update customer profile information
        # subscription.profile = profile
        TWOPLACES = Decimal(10) ** -2
        subscription.amount = Decimal(amount).quantize(TWOPLACES)

        request = apicontractsv1.ARBUpdateSubscriptionRequest()
        request.merchantAuthentication = merchantAuth
        # request.refId = "Sample"
        request.subscriptionId = subscriptionId
        request.subscription = subscription

        controller = ARBUpdateSubscriptionController(request)
        if getattr(settings, 'APP_ENV', None) == 'PROD':
            controller.setenvironment(constants.PRODUCTION)
        controller.execute()

        response = controller.getresponse()

        print(to_dict(response))

        if (response.messages.resultCode == "Ok"):
            return True
        else:
            return False

def to_dict(element):
    ret = {}
    if element.getchildren() == []:
        return element.text
    else:
        for elem in element.getchildren():
            subdict = to_dict(elem)
            ret[re.sub('{.*}', '', elem.tag)] = subdict
    return ret