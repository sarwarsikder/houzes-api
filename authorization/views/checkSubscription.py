# import imp
# import os
# import re
# import sys
import re

from authorizenet import apicontractsv1
from authorizenet.apicontrollers import createTransactionController, ARBGetSubscriptionController
# from django.http import JsonResponse
# from rest_framework.decorators import api_view
from houzes_api import settings

AUTHORIZE_DOT_NET_MERCHANT_AUTH_NAME = getattr(settings, 'AUTHORIZE_DOT_NET_MERCHANT_AUTH_NAME', None)
AUTHORIZE_DOT_NET_MERCHANT_AUTH_TRANSACTION_KEY = getattr(settings, "AUTHORIZE_DOT_NET_MERCHANT_AUTH_TRANSACTION_KEY",
                                                          None)


class CheckSubscription:
    def get_subscription_status(self, subscriptionId):
        print(":::::::::::::SUBSCRIPTION CHECK:::::::::::::::::::")
        merchantAuth = apicontractsv1.merchantAuthenticationType()
        merchantAuth.name = AUTHORIZE_DOT_NET_MERCHANT_AUTH_NAME
        merchantAuth.transactionKey = AUTHORIZE_DOT_NET_MERCHANT_AUTH_TRANSACTION_KEY

        getSubscription = apicontractsv1.ARBGetSubscriptionRequest()
        getSubscription.merchantAuthentication = merchantAuth
        getSubscription.subscriptionId = subscriptionId
        getSubscription.includeTransactions = True

        getSubscriptionController = ARBGetSubscriptionController(getSubscription)
        getSubscriptionController.execute()

        response = getSubscriptionController.getresponse()
        json_response = to_dict(response)
        print(json_response)
        if (response.messages.resultCode == "Ok"):
            # print ("Subscription Name : %s" % response.subscription.name)
            # print ("Subscription Amount: %.2f" % response.subscription.amount)
            # for transaction in response.subscription.arbTransactions.arbTransaction:
            #     print "Transaction id: %d" % transaction.transId
            return True
        else:
            print("response code: %s" % response.messages.resultCode)
            return False
        # return response

    # if(os.path.basename(__file__) == os.path.basename(sys.argv[0])):
    #     get_subscription(constants.subscriptionId)
def to_dict(element):
    ret = {}
    if element.getchildren() == []:
        return element.text
    else:
        for elem in element.getchildren():
            subdict = to_dict(elem)
            ret[re.sub('{.*}', '', elem.tag)] = subdict
    return ret