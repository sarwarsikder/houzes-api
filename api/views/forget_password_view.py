from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.decorators import action
from django.core.mail import send_mail
from rest_framework import viewsets, filters, permissions

from api.serializers import *
from api.models import *
from houzes_api import settings


class ForgetPasswordViewSet(viewsets.ModelViewSet):
    queryset = ForgetPassword.objects.all()
    serializer_class = ForgetPasswordSerializer
    permission_classes = (permissions.AllowAny,)


    def create(self, request, *args, **kwargs):
        email = ''
        status = False
        data = {}
        message = ''
        try:
            email = request.data['email']
        except :
            email =request.body['email']

        user = User.objects.filter(email=email)
        if user.count():
            user = user[0]
            try:
                if ForgetPassword.objects.filter(user = user).count() :
                    ForgetPassword.objects.filter(user=user).delete()
                link_key = generate_shortuuid()
                send_mail(subject="HouZes Forgot Password",
                          message="Dear user\n"+
                              "Click this link to create a new password https://" + settings.WEB_APP_URL + '/forget-password/' +
                                  str(link_key),
                          from_email=settings.EMAIL_HOST_USER,
                          recipient_list=[email],
                          fail_silently=False
                          )
                status = True
                forgetPassword = ForgetPassword(user=user, link_key=link_key)
                forgetPassword.save()
                data = ForgetPasswordSerializer(forgetPassword).data
                message = 'Please check your email to fix your password'
            except:
                status = False
                data = {}
                message = 'Error'

        else:
            status = False
            message = 'User does not exist'

        return Response({'status': status, 'data' : data, 'message' : message})
