from rest_framework import viewsets
from rest_framework.decorators import action

from api.models import *
from api.serializers import *
from rest_framework.response import Response

class UpgradeProfileViewSet(viewsets.ModelViewSet):
    queryset = UpgradeProfile.objects.all()
    serializer_class = UpgradeProfileSerializer

    def create(self, request, *args, **kwargs):
        response_data = {'status': False, 'data': {}, 'message' :''}
        try:
            plan_id = request.data['plan']
        except:
            plan_id = request.body['plan']
        try:
            plan = Plans.objects.get(id = plan_id)
        except :
            response_data['status'] = False
            response_data['message'] = 'This package is currently not available'
            return Response(response_data)
        user = User.objects.get(id = request.user.id)
        if user.is_admin == False :
            response_data['status'] = False
            response_data['message'] = 'This feature is only available for team leader'
            return Response(response_data)

        upgrade_profile = UpgradeProfile.objects.filter(user = user).first()

        if upgrade_profile :
            upgrade_profile.coin = upgrade_profile.coin+plan.plan_coin
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

            response_data['status'] = True
            response_data['data'] = upgrade_profile_serializer.data
            response_data['message'] = 'Profile is upgraded'
        else:
            upgrade_profile = UpgradeProfile()
            upgrade_profile.user = user
            upgrade_profile.coin = plan.plan_coin
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

            response_data['status'] = True
            response_data['data'] = upgrade_profile_serializer.data
            response_data['message'] = 'Profile is upgraded'

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