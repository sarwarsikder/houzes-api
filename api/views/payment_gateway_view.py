"""
Charge a credit card
"""

import imp
import os
import re
import sys
import traceback

from authorizenet import apicontractsv1
from authorizenet.apicontrollers import createTransactionController
from django.http import JsonResponse
from authorizenet.constants import constants
from rest_framework.decorators import api_view
from houzes_api import settings

AUTHORIZE_DOT_NET_MERCHANT_AUTH_NAME = getattr(settings, 'AUTHORIZE_DOT_NET_MERCHANT_AUTH_NAME', None)
AUTHORIZE_DOT_NET_MERCHANT_AUTH_TRANSACTION_KEY = getattr(settings, "AUTHORIZE_DOT_NET_MERCHANT_AUTH_TRANSACTION_KEY", None)

# CONSTANTS = imp.load_source('modulename', 'constants.py')
from api.serializers import *


@api_view(['POST'])
def charge_credit_card(request):
    """
    Charge a credit card
    """
    card_number = ""
    expiration_date = ""
    card_code = ""
    is_save = False
    amount = 0
    card_name = None
    json_response = {'status': False, 'data': {}, 'message': ""}

    try:
        card_number = request.data['card_number']
        expiration_date = request.data['expiration_date']
        card_code = request.data['card_code']
        is_save = request.data['is_save']
        amount = request.data['amount']
        card_name = request.data['card_name']

        manager = User.objects.get(id=request.user.id)
        if manager.is_admin == False:
            manager = User.objects.get(id=manager.invited_by)

        # Create a merchantAuthenticationType object with authentication details
        # retrieved from the constants file
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

        # Create a transactionRequestType object and add the previous objects to it.
        transactionrequest = apicontractsv1.transactionRequestType()
        transactionrequest.transactionType = "authCaptureTransaction"
        transactionrequest.amount = amount
        transactionrequest.payment = payment

        # Assemble the complete transaction request
        createtransactionrequest = apicontractsv1.createTransactionRequest()
        createtransactionrequest.merchantAuthentication = merchantAuth
        createtransactionrequest.refId = "MerchantID-0001"
        createtransactionrequest.transactionRequest = transactionrequest
        # Create the controller
        createtransactioncontroller = createTransactionController(
            createtransactionrequest)
        createtransactioncontroller.setenvironment(constants.PRODUCTION)
        createtransactioncontroller.execute()

        response = createtransactioncontroller.getresponse()
        payment_response = to_dict(response)
        print(payment_response)
        if payment_response['messages']['resultCode'] == 'Ok':
            try:
                if payment_response['transactionResponse']['responseCode'] == '1':
                    upgradeProfile = UpgradeProfile.objects.filter(user=manager).first()
                    if not upgradeProfile:
                        upgradeProfile = UpgradeProfile()
                        upgradeProfile.user = manager
                        upgradeProfile.coin = 0
                        upgradeProfile.plan = Plans.objects.filter(plan_name='Free').first()
                    manager.upgrade = True
                    manager.save()

                    upgradeProfile.coin = float(upgradeProfile.coin) + float(amount)
                    upgradeProfile.save()

                    if BillingCardInfo.objects.filter(user__id=manager.id, card_number=card_number).first():
                        if is_save:
                            BillingCardInfo.objects.filter(user=manager, card_number=card_number).update(
                                card_name=card_name, card_code=card_code, exp_date=expiration_date, is_save=is_save)
                        else:
                            BillingCardInfo.objects.filter(user=manager, card_number=card_number).update(
                                card_name=card_name, card_code=card_code, exp_date=expiration_date)
                    else:
                        billing_card_info = BillingCardInfo()
                        billing_card_info.user = manager
                        billing_card_info.card_number = card_number
                        billing_card_info.card_code = card_code
                        billing_card_info.exp_date = expiration_date
                        billing_card_info.card_name = card_name
                        billing_card_info.is_save = is_save
                        billing_card_info.save()

                    json_response['status'] = True
                    json_response['data'] = UserSerializer(manager).data['upgrade_info']
                    json_response['message'] = payment_response['transactionResponse']['messages']['message'][
                        'description']
                else:
                    json_response['status'] = False
                    json_response['data'] = UserSerializer(manager).data['upgrade_info']
                    json_response['message'] = payment_response['transactionResponse']['errors']['error']['errorText']
            except:
                traceback.print_exc()
                json_response['status'] = False
                json_response['data'] = UserSerializer(manager).data['upgrade_info']
                json_response['message'] = 'Payment transaction failed'
        else:
            print('::::::::::payment response if failed:::::::::::::::::::')
            print(payment_response)
            json_response['status'] = False
            json_response['data'] = UserSerializer(manager).data['upgrade_info']
            try:
                json_response['message'] = payment_response['transactionResponse']['errors']['error']['errorText']
            except:
                json_response['message'] = payment_response['messages']['message']['text']

    except Exception as exc:
        traceback.print_exc()
        json_response['status'] = False
        json_response['data'] = None
        json_response['message'] = str(exc)

    return JsonResponse(json_response)


def to_dict(element):
    ret = {}
    if element.getchildren() == []:
        return element.text
    else:
        for elem in element.getchildren():
            subdict = to_dict(elem)
            ret[re.sub('{.*}', '', elem.tag)] = subdict
    return ret
# if (os.path.basename(__file__) == os.path.basename(sys.argv[0])):
#     charge_credit_card(CONSTANTS.amount)
