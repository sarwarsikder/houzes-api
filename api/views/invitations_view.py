from oauth2_provider.models import AccessToken
from rest_framework import viewsets, status
from api.serializers import *
from api.models import *
from django.core.mail import send_mail
from rest_framework.response import Response
import shortuuid
from django.conf import settings

class InvitationsViewSet(viewsets.ModelViewSet):
    queryset = Invitations.objects.all()
    serializer_class = InvitationsSerializer

    def generate_shortuuid(self):
        shortuuid.set_alphabet("abcdefghijklmnopqrstuvwxyz0123456789")
        gUid = str(shortuuid.random(length=16))
        return gUid

    def create(self, request, *args, **kwargs):
        print(request.user)

        _mutable = request.data._mutable
        request.data._mutable = True

        # receiver = request.data['email']
        receiver = 'nadimauswsit@gmail.com'
        invitation_key = generate_shortuuid()
        # print(User.objects.get(id=request.user.id))
        print(invitation_key)
        send_mail(subject="invitation",
                  message=str(request.user)+" sent you an invitation "+str(invitation_key),
                  from_email=settings.EMAIL_HOST_USER,
                  recipient_list=[receiver],
                  fail_silently=False
                  )

        request.data['invitation_key'] = invitation_key
        request.data._mutable = _mutable
        return super().create(request, *args, **kwargs)
