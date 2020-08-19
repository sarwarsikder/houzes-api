from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from api.models import *
from api.serializers import UserSerializer
from authorization.views.checkSubscription import CheckSubscription as cs
from authorization.views.downgradeProfile import DowngradeProfile as dp

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def subscription_fail_webhook(request):
    subscriptionId = request.data['payload']['id']
    upgrade_profile = UpgradeProfile.objects.filter(subscriptionId = subscriptionId).first()
    try:
        if upgrade_profile:
            print('::::::::::IF UPGRADE PROFILE:::::::::::::')
            if upgrade_profile.subscriptionId != None:
                user = upgrade_profile.user
                print(upgrade_profile.subscriptionId)
                if not cs.get_subscription_status(None, upgrade_profile.subscriptionId):
                    # IF SUBSCRIPTION STATUS IS FALSE DOWNGRADE PROFILE
                    dp.downgrade(None, upgrade_profile, user)

        else:
            print("::::::::::INVALID USER::::::::::")
    except:
        print('EXCEPTION OCCURED WHILE CHECKING SUBSCRIPTION')
    return JsonResponse({'status' : True})