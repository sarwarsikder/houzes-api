import re
import traceback

from authorizenet import apicontractsv1
from authorizenet.constants import constants
from authorizenet.apicontrollers import createTransactionController, ARBGetSubscriptionController
from houzes_api import settings

AUTHORIZE_DOT_NET_MERCHANT_AUTH_NAME = getattr(settings, 'AUTHORIZE_DOT_NET_MERCHANT_AUTH_NAME', None)
AUTHORIZE_DOT_NET_MERCHANT_AUTH_TRANSACTION_KEY = getattr(settings, "AUTHORIZE_DOT_NET_MERCHANT_AUTH_TRANSACTION_KEY",
                                                          None)


class CheckSubscription:
    def get_subscription_status(self, subscriptionId):
        try:
            print(":::::::::::::SUBSCRIPTION CHECK:::::::::::::::::::"+subscriptionId)
            merchantAuth = apicontractsv1.merchantAuthenticationType()
            merchantAuth.name = AUTHORIZE_DOT_NET_MERCHANT_AUTH_NAME
            merchantAuth.transactionKey = AUTHORIZE_DOT_NET_MERCHANT_AUTH_TRANSACTION_KEY

            getSubscription = apicontractsv1.ARBGetSubscriptionRequest()
            getSubscription.merchantAuthentication = merchantAuth
            getSubscription.subscriptionId = subscriptionId
            getSubscription.includeTransactions = True

            getSubscriptionController = ARBGetSubscriptionController(getSubscription)
            getSubscriptionController.setenvironment(constants.PRODUCTION)
            getSubscriptionController.execute()

            response = getSubscriptionController.getresponse()
            json_response = to_dict(response)
            print(json_response)
            if (response.messages.resultCode == "Ok"):
                return True
            else:
                print("response code: %s" % response.messages.resultCode)
                return False
        except:
            traceback.print_exc()
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