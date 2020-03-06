from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.decorators import action
from django.core.mail import send_mail
from rest_framework import viewsets, filters, permissions

from api.serializers import *
from api.models import *
from api.views.send_email_view import SendEmailViewSet
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
                # send_mail(subject="HouZes Forgot Password",
                #           message="Dear user\n"+
                #               "Click this link to create a new password https://" + settings.WEB_APP_URL + '/forget-password/' +
                #                   str(link_key),
                #           from_email=settings.EMAIL_HOST_USER,
                #           recipient_list=[email],
                #           fail_silently=False
                #           )
                subject = "HouZes Forgot Password"
                body = "Click this link below to create a new password."
                url = "https://" + settings.WEB_APP_URL + "/forget-password/" +str(link_key)
                name = user.first_name + ' '+user.last_name
                SendEmailViewSet.send_email_view(self, subject, body, email, ' '+name, url)
                status = True
                forgetPassword = ForgetPassword(user=user, link_key=link_key)
                forgetPassword.save()
                data = ForgetPasswordSerializer(forgetPassword).data
                message = 'Please check your email to reset password'
            except:
                status = False
                data = {}
                message = 'Server Error'

        else:
            status = False
            message = 'User does not exist'

        return Response({'status': status, 'data' : data, 'message' : message})

    @action(detail=False, url_path='link-key/(?P<key>[\w-]+)')
    def get_forget_password_by_link_key(self, request, *args, **kwargs):
        forgetPassword = ForgetPassword.objects.filter(link_key=kwargs['key'])
        if forgetPassword.count():
            forgetPassword = forgetPassword[0]
            print(forgetPassword)
            forgetPasswordSerializer = ForgetPasswordSerializer(forgetPassword)
            return Response(forgetPasswordSerializer.data)