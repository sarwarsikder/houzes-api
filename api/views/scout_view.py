from rest_framework import viewsets
from oauth2_provider.models import AccessToken
from rest_framework.response import Response

from api.serializers import *
from api.models import *

from django.http import JsonResponse

from houzes_api.settings import WEB_APP_URL


class ScoutViewSet(viewsets.ModelViewSet):
    queryset = Scout.objects.all()
    serializer_class = ScoutSerializer

    def get_queryset(self):
        return Scout.objects.filter(manager_id=self.request.user.id)

    def generate_shortuuid(self):
        shortuuid.set_alphabet("abcdefghijklmnopqrstuvwxyz0123456789")
        gUid = str(shortuuid.random(length=16))
        return gUid

    def create(self, request, *args, **kwargs):
        first_name = None
        last_name = None
        try:
            if 'first_name' in request.data:
                first_name = request.data['first_name']

            if 'last_name' in request.data:
                last_name = request.data['last_name']
        except:
            if 'first_name' in request.body:
                first_name = request.body['first_name']
            if 'last_name' in request.body:
                last_name = request.body['last_name']

        if first_name == None:
            status = False
            data = None
            message = "First name required"
            return Response({'status': status, 'data': data, 'message': message})
        if last_name == None:
            status = False
            data = None
            message = "Last name required"
            return Response({'status': status, 'data': data, 'message': message})

        name = "List of "+first_name + ' ' + last_name

        access_token = request.META["HTTP_AUTHORIZATION"][7:]
        access_token_object = AccessToken.objects.get(token=access_token)
        user = access_token_object.user

        user_list = UserList(name=name, user=user, leads_count=0)
        user_list.save()

        url = WEB_APP_URL+"/scout-form/"+str(user_list.id)+"/"+generate_shortuuid()
        manager = User.objects.get(id=request.user.id)

        try:
            scout = Scout(first_name=first_name,last_name=last_name,url=url,manager_id=manager)
            scout.save()
            scoutSerializer = ScoutSerializer(scout)
            status = True
            data = scoutSerializer.data
            message = "Scout is created"
        except:
            status = False
            data = None
            message = "Error creating scout"

        return Response({'status': status, 'data': data, 'message': message})


