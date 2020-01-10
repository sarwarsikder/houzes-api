"""
Charge a credit card
"""

import imp
import os
import re
import sys

from authorizenet import apicontractsv1
from authorizenet.apicontrollers import createTransactionController
from django.http import JsonResponse
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
    try:
        card_number = request.data['card_number']
        expiration_date = request.data['expiration_date']
        card_code = request.data['card_code']
        is_save = request.data['is_save']
        amount = request.data['amount']
    except :
        # card_number = request.body['card_number']
        # expiration_date = request.body['expiration_date']
        # card_code = request.body['card_code']
        # is_save = request.body['is_save']
        # amount = request.body['amount']
        print('xx')

    manager = User.objects.get(id = request.user.id)
    if manager.is_admin == False :
        manager = User.objects.get(id = manager.invited_by)
    json_response = {'status' : False, 'data' : {}, 'message' : ""}
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

    # Create order information
    # order = apicontractsv1.orderType()
    # order.invoiceNumber = "10101"
    # order.description = "Golf Shirts"

    # Set the customer's Bill To address
    # customerAddress = apicontractsv1.customerAddressType()
    # customerAddress.firstName = "Ellen"
    # customerAddress.lastName = "Johnson"
    # customerAddress.company = "Souveniropolis"
    # customerAddress.address = "14 Main Street"
    # customerAddress.city = "Pecan Springs"
    # customerAddress.state = "TX"
    # customerAddress.zip = "44628"
    # customerAddress.country = "USA"

    # Set the customer's identifying information
    # customerData = apicontractsv1.customerDataType()
    # customerData.type = "individual"
    # customerData.id = "99999456654"
    # customerData.email = "EllenJohnson@example.com"

    # Add values for transaction settings
    # duplicateWindowSetting = apicontractsv1.settingType()
    # duplicateWindowSetting.settingName = "duplicateWindow"
    # duplicateWindowSetting.settingValue = "600"
    # settings = apicontractsv1.ArrayOfSetting()
    # settings.setting.append(duplicateWindowSetting)

    # setup individual line items
    # line_item_1 = apicontractsv1.lineItemType()
    # line_item_1.itemId = "12345"
    # line_item_1.name = "first"
    # line_item_1.description = "Here's the first line item"
    # line_item_1.quantity = "2"
    # line_item_1.unitPrice = "12.95"
    # line_item_2 = apicontractsv1.lineItemType()
    # line_item_2.itemId = "67890"
    # line_item_2.name = "second"
    # line_item_2.description = "Here's the second line item"
    # line_item_2.quantity = "3"
    # line_item_2.unitPrice = "7.95"

    # build the array of line items
    # line_items = apicontractsv1.ArrayOfLineItem()
    # line_items.lineItem.append(line_item_1)
    # line_items.lineItem.append(line_item_2)

    # Create a transactionRequestType object and add the previous objects to it.
    transactionrequest = apicontractsv1.transactionRequestType()
    transactionrequest.transactionType = "authCaptureTransaction"
    transactionrequest.amount = amount
    transactionrequest.payment = payment
    # transactionrequest.order = order
    # transactionrequest.billTo = customerAddress
    # transactionrequest.customer = customerData
    # transactionrequest.transactionSettings = settings
    # transactionrequest.lineItems = line_items

    # Assemble the complete transaction request
    createtransactionrequest = apicontractsv1.createTransactionRequest()
    createtransactionrequest.merchantAuthentication = merchantAuth
    createtransactionrequest.refId = "MerchantID-0001"
    createtransactionrequest.transactionRequest = transactionrequest
    # Create the controller
    createtransactioncontroller = createTransactionController(
        createtransactionrequest)
    createtransactioncontroller.execute()

    # response = createtransactioncontroller.getresponse()

    # if response is not None:
    #     # Check to see if the API request was successfully received and acted upon
    #     if response.messages.resultCode == "Ok":
    #         # Since the API request was successful, look for a transaction response
    #         # and parse it to display the results of authorizing the card
    #         if hasattr(response.transactionResponse, 'messages') is True:
    #             print(
    #                 'Successfully created transaction with Transaction ID: %s'
    #                 % response.transactionResponse.transId)
    #             print('Transaction Response Code: %s' %
    #                   response.transactionResponse.responseCode)
    #             print('Message Code: %s' %
    #                   response.transactionResponse.messages.message[0].code)
    #             print('Description: %s' % response.transactionResponse.
    #                   messages.message[0].description)
    #         else:
    #             print('Failed Transaction.')
    #             if hasattr(response.transactionResponse, 'errors') is True:
    #                 print('Error Code:  %s' % str(response.transactionResponse.
    #                                               errors.error[0].errorCode))
    #                 print(
    #                     'Error message: %s' %
    #                     response.transactionResponse.errors.error[0].errorText)
    #     # Or, print errors if the API request wasn't successful
    #     else:
    #         print('Failed Transaction.')
    #         if hasattr(response, 'transactionResponse') is True and hasattr(
    #                 response.transactionResponse, 'errors') is True:
    #             print('Error Code: %s' % str(
    #                 response.transactionResponse.errors.error[0].errorCode))
    #             print('Error message: %s' %
    #                   response.transactionResponse.errors.error[0].errorText)
    #         else:
    #             print('Error Code: %s' %
    #                   response.messages.message[0]['code'].text)
    #             print('Error message: %s' %
    #                   response.messages.message[0]['text'].text)
    # else:
    #     print('Null Response.')
    #
    # return response

    response = createtransactioncontroller.getresponse()
    payment_response = to_dict(response)
    if payment_response['messages']['resultCode']=='Ok' :
        upgradeProfile = UpgradeProfile.objects.filter(user= manager).first()
        if not upgradeProfile:
            upgradeProfile = UpgradeProfile()
            upgradeProfile.user = manager
            upgradeProfile.coin = 0
            upgradeProfile.plan = Plans.objects.filter(plan_name='Free').first()
        manager.upgrade = True
        manager.save()

        upgradeProfile.coin = float(upgradeProfile.coin) + float(amount)
        upgradeProfile.save()

        billing_card_info = BillingCardInfo()
        billing_card_info.user = User.objects.get(id=request.user.id)
        billing_card_info.card_name = None
        billing_card_info.card_number = card_number
        billing_card_info.card_code = card_code
        billing_card_info.exp_date = expiration_date
        billing_card_info.is_save = is_save
        billing_card_info.save()

        json_response['status'] = True
        json_response['data'] = UserSerializer(manager).data['upgrade_info']
        json_response['message'] = payment_response['transactionResponse']['messages']['message']['description']
    else:
        json_response['status'] = False
        json_response['data'] = UserSerializer(manager).data['upgrade_info']
        json_response['message'] = payment_response['transactionResponse']['errors']['error']['errorText']

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
