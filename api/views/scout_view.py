from rest_framework import viewsets
from oauth2_provider.models import AccessToken
from api.serializers import *
from api.models import *

from django.http import JsonResponse

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
        if not request.data._mutable:
            state = request.data._mutable
            request.data._mutable = True

        request.data['manager_id'] = request.user.id

        name = "List of "+request.data['first_name'] + ' ' + request.data['last_name']
        # user = User.objects.get(id=request.data['manager_id'])

        access_token = request.META["HTTP_AUTHORIZATION"][7:]
        access_token_object = AccessToken.objects.get(token=access_token)
        user = access_token_object.user

        user_list = UserList(name=name, user=user, leads_count=0)
        user_list.save()
        # front end url
        base_url= "https://houzes.com"
        request.data['url'] = base_url+"/scout-form/"+str(user_list.id)+"/"+generate_shortuuid()

        if not request.data._mutable:
            request.data._mutable = state
        return super().create(request, *args, **kwargs)


