from oauth2_provider.models import AccessToken
# from django.utils import simplejson
from rest_framework import viewsets, status
from api.serializers import *
from api.models import *
from django.core.mail import send_mail
from rest_framework.response import Response
import shortuuid
from django.conf import settings
from django.http import HttpResponse, JsonResponse
import json
import datetime
from django.core import serializers


class InvitationsViewSet(viewsets.ModelViewSet):
    queryset = Invitations.objects.all()
    serializer_class = InvitationsSerializer


    # def get_queryset(self):
    #     return Invitations.objects.filter(user=self.request.user.id)

    def generate_shortuuid(self):
        shortuuid.set_alphabet("abcdefghijklmnopqrstuvwxyz0123456789")
        gUid = str(shortuuid.random(length=16))
        return gUid

    def create(self, request, *args, **kwargs):
        print(request.user)

        receiver = request.data['email']
        request.data['status'] = 0

        # _mutable = request.data._mutable
        # request.data._mutable = True
        print(receiver)
        # receiver = 'nadimauswsit@gmail.com'
        invitation_key = generate_shortuuid()
        # print(User.objects.get(id=request.user.id))
        print(invitation_key)
        send_mail(subject="Invitation",
                  message=str(request.user)+" sent you an invitation "+str(invitation_key),
                  from_email=settings.EMAIL_HOST_USER,
                  recipient_list=[receiver],
                  fail_silently=False
                  )

        request.data['invitation_key'] = invitation_key
        request.data['user'] = request.user.id
        # request.data._mutable = _mutable
        return super().create(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        users = UserSerializer(User.objects.filter(invited_by=request.user.id),many=True)
        # user = User.objects.get(id = re)
        unregistered_invitations = InvitationsSerializer(Invitations.objects.filter(status=0, user_id=request.user.id),many=True)
        dict = {
            # 'users': list(),
            'users': users.data,
            'unregistered_invitations': unregistered_invitations.data,
        }
        print(dict)
        # return HttpResponse(json.dumps(str(dict)))

        return JsonResponse(dict)