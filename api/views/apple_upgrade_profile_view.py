from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from api.models import *
from api.serializers import UserSerializer, UpgradeProfileSerializer


@api_view(['POST'])
def apple_upgrade_profile(request):
    user = User.objects.get(id=request.user.id)
    if user.is_team_admin == False:
        return JsonResponse({'status': False, 'data': None, 'message' : 'This feature is only available for team leader'})
    plan_id = request.POST.get('plan')
    plan = Plans.objects.get(id=plan_id)
    upgrade_profile = UpgradeProfile.objects.filter(user=user).first()
    if upgrade_profile:
        upgrade_profile.coin = float(upgrade_profile.coin) + 0
        upgrade_profile.plan = plan
        upgrade_profile.subscriptionId = None
        upgrade_profile.save()

    else:
        upgrade_profile = UpgradeProfile()
        upgrade_profile.user = user
        upgrade_profile.coin = 0
        upgrade_profile.plan = plan
        upgrade_profile.save()

    return JsonResponse({'status' : True, 'data': UpgradeProfileSerializer(upgrade_profile).data, 'message':'Payment transaction successful'})