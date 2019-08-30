from rest_framework import viewsets
from oauth2_provider.models import AccessToken
from api.serializers import *
from api.models import *

from django.http import JsonResponse

class ScoutViewSet(viewsets.ModelViewSet):
    queryset = Scout.objects.all()
    serializer_class = ScoutSerializer

    def generate_shortuuid(self):
        shortuuid.set_alphabet("abcdefghijklmnopqrstuvwxyz0123456789")
        gUid = str(shortuuid.random(length=16))
        return gUid

    def create(self, request, *args, **kwargs):

        print(str(request.data['manager_id'])+' '+request.data['first_name'])
        print("---------------------------")
        print(User.objects.get(id=request.data['manager_id']))
        name = "List of "+request.data['first_name'] + ' ' + request.data['last_name']
        # user = User.objects.get(id=request.data['manager_id'])

        access_token = request.META["HTTP_AUTHORIZATION"][7:]
        access_token_object = AccessToken.objects.get(token=access_token)
        user = access_token_object.user

        user_list = UserList(name=name, user=user, leads_count=0)
        user_list.save()
        # front end url
        base_url= "http://172.18.1.11:8191"
        request.data['url'] = base_url+"/"+str(user_list.id)+"/"+generate_shortuuid()
        return super().create(request, *args, **kwargs)
