from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from api.models import *
from api.serializers import UserSerializer


@api_view(['POST'])
def apple_payment_gateway(request):
    manager = User.objects.get(id=request.user.id)
    if manager.is_team_admin == False:
        return JsonResponse({'status': False, 'data': None, 'message' : 'Only team manager can pay'})
    amount = request.POST.get('amount')
    print(amount)
    upgrade_profile = UpgradeProfile.objects.filter(user=manager).first()
    if not upgrade_profile:
        upgrade_profile = UpgradeProfile()
        upgrade_profile.user = manager
        upgrade_profile.coin = 0
        upgrade_profile.plan = Plans.objects.filter(plan_name='Free').first()
    manager.upgrade = True
    manager.save()

    upgrade_profile.coin = float(upgrade_profile.coin) + float(amount)
    upgrade_profile.save()
    return JsonResponse({'status' : True, 'data': UserSerializer(manager).data['upgrade_info'], 'message':'Payment transaction successful'})