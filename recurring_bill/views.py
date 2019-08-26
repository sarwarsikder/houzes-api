from django.http import HttpResponse
from django.http import JsonResponse
import json
import xmltodict
import imp
import os
import sys
from authorizenet import apicontractsv1
from authorizenet.apicontrollers import *
# constants = imp.load_source('modulename', 'constants.py')
from decimal import *
from datetime import *
import re
from django.views.decorators.csrf import csrf_exempt


def to_dict(element):
    ret = {}
    if element.getchildren() == []:
        return element.text
    else:
        for elem in element.getchildren():
            subdict = to_dict(elem)
            ret[re.sub('{.*}', '', elem.tag)] = subdict
    return ret

@csrf_exempt
def create_subscription(request):
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    firstName = body['firstName']
    lastName = body['lastName']
    cardNumber = body['cardNumber']
    expirationDate = body['expirationDate']
    subscriptionName = body['subscriptionName']
    # print(firstName,lastName,cardNumber,expirationDate,amount,subscriptionName)
    amount = 20

    days = 30
    startDate = datetime(2019,8,30)

    # Setting the merchant details
    merchantAuth = apicontractsv1.merchantAuthenticationType()
    merchantAuth.name = '5wW5bq9qD5y'
    merchantAuth.transactionKey = '3Fh93wse887PV77B'
    # Setting payment schedule
    paymentschedule = apicontractsv1.paymentScheduleType()
    paymentschedule.interval = apicontractsv1.paymentScheduleTypeInterval()  # apicontractsv1.CTD_ANON() #modified by krgupta
    paymentschedule.interval.length = days
    paymentschedule.interval.unit = apicontractsv1.ARBSubscriptionUnitEnum.days
    paymentschedule.startDate = startDate
    paymentschedule.totalOccurrences = 9999
    paymentschedule.trialOccurrences = 1
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
    subscription.amount = amount
    subscription.trialAmount = Decimal('0.00')
    subscription.billTo = billto
    subscription.payment = payment
    # Creating the request
    request = apicontractsv1.ARBCreateSubscriptionRequest()
    request.merchantAuthentication = merchantAuth
    request.subscription = subscription
    # Creating and executing the controller
    controller = ARBCreateSubscriptionController(request)
    controller.execute()
    # Getting the response
    response = controller.getresponse()
    json_response = to_dict(response)

    return JsonResponse(json_response)

# if(os.path.basename(__file__) == os.path.b    asename(sys.argv[0])):
#     create_subscription(constants.amount, constants.days)

@csrf_exempt
def create_subscription_from_customer_profile(request):
    amount = 50
    days = 30
    profileId = "1508816387"
    paymentProfileId = "1508306528"
    # customerAddressId

    # Setting the merchant details
    merchantAuth = apicontractsv1.merchantAuthenticationType()
    merchantAuth.name = '5wW5bq9qD5y'
    merchantAuth.transactionKey = '3Fh93wse887PV77B'
    # Setting payment schedule
    paymentschedule = apicontractsv1.paymentScheduleType()
    paymentschedule.interval = apicontractsv1.paymentScheduleTypeInterval() #apicontractsv1.CTD_ANON() #modified by krgupta
    paymentschedule.interval.length = days
    paymentschedule.interval.unit = apicontractsv1.ARBSubscriptionUnitEnum.days
    paymentschedule.startDate = datetime(2020, 8, 30)
    paymentschedule.totalOccurrences = 12
    paymentschedule.trialOccurrences = 1

    #setting the customer profile details
    profile = apicontractsv1.customerProfileIdType()
    profile.customerProfileId = profileId
    profile.customerPaymentProfileId = paymentProfileId
    # profile.customerAddressId = customerAddressId

    # Setting subscription details
    subscription = apicontractsv1.ARBSubscriptionType()
    subscription.name = "Sample Subscription"
    subscription.paymentSchedule = paymentschedule
    subscription.amount = amount
    subscription.trialAmount = Decimal('0.00')
    subscription.profile = profile

    # Creating the request
    request = apicontractsv1.ARBCreateSubscriptionRequest()
    request.merchantAuthentication = merchantAuth
    request.subscription = subscription

    # Creating and executing the controller
    controller = ARBCreateSubscriptionController(request)
    controller.execute()
    # Getting the response
    response = controller.getresponse()

    json_response = to_dict(response)

    return JsonResponse(json_response)

@csrf_exempt
def get_subscription_details(request):
    # body_unicode = request.body.decode('utf-8')
    # body = json.loads(body_unicode)
    # subscriptionId = body['subscriptionId']

    subscriptionId = request.POST.get('subscriptionId')

    merchantAuth = apicontractsv1.merchantAuthenticationType()
    merchantAuth.name = '5wW5bq9qD5y'
    merchantAuth.transactionKey = '3Fh93wse887PV77B'


    getSubscription = apicontractsv1.ARBGetSubscriptionRequest()
    getSubscription.merchantAuthentication = merchantAuth
    getSubscription.subscriptionId = subscriptionId
    getSubscription.includeTransactions = True

    getSubscriptionController = ARBGetSubscriptionController(getSubscription)
    getSubscriptionController.execute()

    response = getSubscriptionController.getresponse()

    json_response = to_dict(response)

    return JsonResponse(json_response)

@csrf_exempt
def get_subscription_status(request):
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    subscriptionId = body['subscriptionId']

    # Setting the mercahnt details
    merchantAuth = apicontractsv1.merchantAuthenticationType()
    merchantAuth.name = '5wW5bq9qD5y'
    merchantAuth.transactionKey = '3Fh93wse887PV77B'
    # Seeting the request
    request = apicontractsv1.ARBGetSubscriptionStatusRequest()
    request.merchantAuthentication = merchantAuth
    request.refId = "Sample"
    request.subscriptionId = subscriptionId
    # Executing the controller
    controller = ARBGetSubscriptionStatusController(request)
    controller.execute()
    # Getting the response
    response = controller.getresponse()

    json_response = to_dict(response)
    return JsonResponse(json_response)

@csrf_exempt
def get_list_of_subscriptions(request):
    """get list of subscriptions"""
    merchantAuth = apicontractsv1.merchantAuthenticationType()
    merchantAuth.name = '5wW5bq9qD5y'
    merchantAuth.transactionKey = '3Fh93wse887PV77B'

    # set sorting parameters
    sorting = apicontractsv1.ARBGetSubscriptionListSorting()
    sorting.orderBy = apicontractsv1.ARBGetSubscriptionListOrderFieldEnum.id
    sorting.orderDescending = True

    # set paging and offset parameters
    paging = apicontractsv1.Paging()
    # Paging limit can be up to 1000 for this request
    paging.limit = 20
    paging.offset = 1

    request = apicontractsv1.ARBGetSubscriptionListRequest()
    request.merchantAuthentication = merchantAuth
    request.refId = "Sample"
    request.searchType = apicontractsv1.ARBGetSubscriptionListSearchTypeEnum.subscriptionInactive #subscriptionActive to get active subscription list
    request.sorting = sorting
    request.paging = paging

    controller = ARBGetSubscriptionListController(request)
    controller.execute()

    # Work on the response
    response = controller.getresponse()

    json_response = to_dict(response)
    print(json_response)
    return JsonResponse(json_response)

@csrf_exempt
def cancel_subscription(request):
    subscriptionId = "5956473"

    merchantAuth = apicontractsv1.merchantAuthenticationType()
    merchantAuth.name = '5wW5bq9qD5y'
    merchantAuth.transactionKey = '3Fh93wse887PV77B'

    request = apicontractsv1.ARBCancelSubscriptionRequest()
    request.merchantAuthentication = merchantAuth
    request.refId = "Sample"
    request.subscriptionId = subscriptionId

    controller = ARBCancelSubscriptionController(request)
    controller.execute()

    response = controller.getresponse()

    json_response = to_dict(response)
    return JsonResponse(json_response)

@csrf_exempt
def update_subscription(request):
    subscriptionId = "5956460"

    merchantAuth = apicontractsv1.merchantAuthenticationType()
    merchantAuth.name = '5wW5bq9qD5y'
    merchantAuth.transactionKey = '3Fh93wse887PV77B'

    creditcard = apicontractsv1.creditCardType()
    creditcard.cardNumber = "370000000000002"
    creditcard.expirationDate = "2020-12"

    payment = apicontractsv1.paymentType()
    payment.creditCard = creditcard

    #set profile information
    profile = apicontractsv1.customerProfileIdType()
    profile.customerProfileId = "121212"
    profile.customerPaymentProfileId = "131313"
    profile.customerAddressId = "141414"

    subscription = apicontractsv1.ARBSubscriptionType()
    subscription.payment = payment
    #to update customer profile information
    #subscription.profile = profile

    request = apicontractsv1.ARBUpdateSubscriptionRequest()
    request.merchantAuthentication = merchantAuth
    request.refId = "Sample"
    request.subscriptionId = subscriptionId
    request.subscription = subscription

    controller = ARBUpdateSubscriptionController(request)
    controller.execute()

    response = controller.getresponse()

    json_response = to_dict(response)
    return JsonResponse(json_response)


@csrf_exempt
def update_amount_of_subscription(request):
    # body_unicode = request.body.decode('utf-8')
    # body = json.loads(body_unicode)
    # amount = body['amount']
    # subscriptionId = body['subscriptionId']
    subscriptionId = request.POST.get('subscriptionId')
    amount = request.POST.get('amount')

    merchantAuth = apicontractsv1.merchantAuthenticationType()
    merchantAuth.name = '5wW5bq9qD5y'
    merchantAuth.transactionKey = '3Fh93wse887PV77B'


    subscription = apicontractsv1.ARBSubscriptionType()
    subscription.amount = amount

    request = apicontractsv1.ARBUpdateSubscriptionRequest()
    request.merchantAuthentication = merchantAuth
    request.refId = "Sample"
    request.subscriptionId = subscriptionId
    request.subscription = subscription

    controller = ARBUpdateSubscriptionController(request)
    controller.execute()

    response = controller.getresponse()

    json_response = to_dict(response)
    return JsonResponse(json_response)