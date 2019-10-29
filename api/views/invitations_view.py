from oauth2_provider.models import AccessToken
# from django.utils import simplejson
from rest_framework import viewsets, status
from rest_framework.decorators import action

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

    def generate_shortuuid(self):
        shortuuid.set_alphabet("abcdefghijklmnopqrstuvwxyz0123456789")
        gUid = str(shortuuid.random(length=16))
        return gUid

    def create(self, request, *args, **kwargs):
        try:
            receiver =request.data['email']
        except:
            receiver = request.body['email']

        status = False
        data = None
        message=""

        invitation_key = generate_shortuuid()
        try:
            send_mail(subject="Invitation",
                      message=str(request.user)+" sent you an invitation click here to accept "+settings.WEB_APP_URL+'/team-invite/'+str(invitation_key),
                      from_email=settings.EMAIL_HOST_USER,
                      recipient_list=[receiver],
                      fail_silently=False
                      )

            invitations = Invitations(user=User.objects.get(id=request.user.id),invitation_key = invitation_key,email=receiver,status=0)
            invitations.save()
            invitationsSerializer = InvitationsSerializer(invitations)
            status = True
            data = invitationsSerializer.data
            message = "Invitation sent to "+receiver+" successfully"
        except:
            status = False
            message = "User is not invited"
        return Response({'status': status,'data': data,'message': message})


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

    def destroy(self, request, *args, **kwargs):
        invitationId = kwargs['pk']
        status = False
        message=""
        try:
            Invitations.objects.get(id=invitationId).delete()
            status = True
            message = "Invitation deleted successfully"
        except:
            status = False
            message = "Invitation is not deleted"
        return Response({'status': status,'message': message})

