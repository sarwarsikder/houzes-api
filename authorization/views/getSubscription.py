# import imp
# import os
# import re
# import sys
#
# from authorizenet import apicontractsv1
# from authorizenet.apicontrollers import createTransactionController, ARBGetSubscriptionController
# from django.http import JsonResponse
# from rest_framework.decorators import api_view
# from houzes_api import settings
#
# AUTHORIZE_DOT_NET_MERCHANT_AUTH_NAME = getattr(settings, 'AUTHORIZE_DOT_NET_MERCHANT_AUTH_NAME', None)
# AUTHORIZE_DOT_NET_MERCHANT_AUTH_TRANSACTION_KEY = getattr(settings, "AUTHORIZE_DOT_NET_MERCHANT_AUTH_TRANSACTION_KEY", None)
#
#
# def get_subscription(subscriptionId):
#     merchantAuth = apicontractsv1.merchantAuthenticationType()
#     merchantAuth.name = AUTHORIZE_DOT_NET_MERCHANT_AUTH_NAME
#     merchantAuth.transactionKey = AUTHORIZE_DOT_NET_MERCHANT_AUTH_TRANSACTION_KEY
#
#
#     getSubscription = apicontractsv1.ARBGetSubscriptionRequest()
#     getSubscription.merchantAuthentication = merchantAuth
#     getSubscription.subscriptionId = subscriptionId
#     getSubscription.includeTransactions = True
#
#     getSubscriptionController = ARBGetSubscriptionController(getSubscription)
#     getSubscriptionController.execute()
#
#     response = getSubscriptionController.getresponse()
#
#     if (response.messages.resultCode=="Ok"):
#         print ("Subscription Name : %s" % response.subscription.name)
#         print ("Subscription Amount: %.2f" % response.subscription.amount)
#         for transaction in response.subscription.arbTransactions.arbTransaction:
#             print "Transaction id: %d" % transaction.transId
#     else:
#         print ("response code: %s" % response.messages.resultCode)
#
#     return response
#
# if(os.path.basename(__file__) == os.path.basename(sys.argv[0])):
#     get_subscription(constants.subscriptionId)
