import os
import re
import sys
import traceback

from django.http import JsonResponse
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from oauth2_provider.models import AccessToken
from rest_framework.response import Response
from django.contrib.auth.hashers import make_password, check_password
from rest_framework.utils import json

from api.views.send_email_view import SendEmailViewSet
from houzes_api import settings
from houzes_api.util.file_upload import file_upload
import time
from django.core.mail import send_mail
import requests
from api.serializers import *
from api.models import *
from houzes_api.util.s3_image_upload import image_upload


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)
    filterset_fields = ["email"]

    @action(detail=False, methods=['GET'], url_path='get-current-user-info')
    def get_current_userinfo(self, request):
        access_token = request.META["HTTP_AUTHORIZATION"][7:]
        access_token_object = AccessToken.objects.get(token=access_token)
        user = access_token_object.user
        serializer = UserSerializer(user)
        try:
            if request.GET.get('device_id'):
                user_firebase = UserFirebase()
                user_firebase.device_type = request.GET.get('device_type')
                user_firebase.id = user_firebase.device_type.lower() + ":" + request.GET.get('device_id')
                user_firebase.device_version = request.GET.get('version')
                user_firebase.firebase_token = request.GET.get('firebase_token')
                user_firebase.user_id = user.id
                UserFirebase.objects.filter(id=user_firebase.id).update(firebase_token=user_firebase.firebase_token,
                                                                        device_version=user_firebase.device_version,
                                                                        user_id=user_firebase.user_id)
                user_firebase.save()
        except:
            print("-----------")
        return JsonResponse(serializer.data, safe=False)

    def generate_shortuuid(self):
        shortuuid.set_alphabet("abcdefghijklmnopqrstuvwxyz0123456789")
        gUid = str(shortuuid.random(length=16))
        return gUid

    # def check(email):
    #     regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
    #     if re.search(regex, email):
    #         return True
    #     else:
    #         return False

    def create(self, request, *args, **kwargs):
        status = False
        data = None
        message = ""

        password = None
        first_name = None
        last_name = None
        email = None
        phone_number = None
        invited_by = None
        is_active = False
        is_team_admin = False

        photo = None
        photo_thumb = None

        try:
            if 'password' in request.data:
                password = request.data['password']
                if password == "":
                    status = False
                    data = None
                    message = "Password is required"
                    return Response({'status': status, 'data': data, 'message': message})
                password = make_password(request.data['password'])
            if 'first_name' in request.data:
                first_name = request.data['first_name']
                if first_name == "":
                    status = False
                    data = None
                    message = "First Name is required"
                    return Response({'status': status, 'data': data, 'message': message})
            if 'last_name' in request.data:
                last_name = request.data['last_name']
                if last_name == "":
                    status = False
                    data = None
                    message = "Last Name is required"
                    return Response({'status': status, 'data': data, 'message': message})
            if 'email' in request.data:
                email = request.data['email']
                if email == "":
                    status = False
                    data = None
                    message = "Email is required"
                    return Response({'status': status, 'data': data, 'message': message})
                else:
                    email = email.lower().strip()
            if User.objects.filter(email=email).count() > 0:
                status = False
                data = None
                message = "Email already exists"
                return Response({'status': status, 'data': data, 'message': message})

            if 'phone_number' in request.data:
                phone_number = request.data['phone_number']
                if phone_number == "":
                    status = False
                    data = None
                    message = "Phone Number is required"
                    return Response({'status': status, 'data': data, 'message': message})
            print(request.data)
            # if 'is_active' in request.data:
            #     is_active = request.data['is_active']
            if 'invited_by' in request.data:
                invited_by = request.data['invited_by']
            if 'is_admin' in request.data:
                if isinstance(request.data['is_admin'], str):
                    is_team_admin = True
                else:
                    is_team_admin = request.data['is_admin']
            print(email)
            print(password)
            print(first_name)
            print(last_name)
            print(phone_number)

            if email == None or password == None or first_name == None or last_name == None or phone_number == None:
                status = False
                message = "Please provide all the required fields correctly"
                data = None
                return Response({'status': status, 'data': data, 'message': message})

        except:
            status = False
            message = "Please provide all the required fields correctly"
            data = None
            return Response({'status': status, 'data': data, 'message': message})

        try:
            s3_url = ""
            if 'photo' in request.FILES:
                # data['photo'] = "in progress"
                file = request.FILES['photo']
                # file_path = "photos/user/{}/{}".format(generate_shortuuid(), str(time.time()) + '.jpg')
                # s3_url = "https://s3.{}.amazonaws.com/{}/{}".format(settings.AWS_REGION, settings.S3_BUCKET_NAME,
                #                                                     file_path)
                # file_upload(file, file_path)
                # request.data['photo'] = s3_url
                # photo = s3_url
                # print(photo)

                s3_path_prefix = "photos/user/"
                file_name = generate_shortuuid() + str(time.time()) + '.png'
                img_data = image_upload(file, s3_path_prefix, file_name, True)
                if img_data["status"]:
                    full_img_path = img_data['full_img_url']
                    thumb_img_path = img_data['thumb_url']
                    photo = full_img_path
                    photo_thumb = thumb_img_path


        except:
            traceback.print_exc()
            status = False
            message = "Error uploading photo"
            data = None
            return Response({'status': status, 'data': data, 'message': message})

        try:
            user = User(email=email, password=password, first_name=first_name, last_name=last_name,
                        phone_number=phone_number, invited_by=invited_by, is_active=is_active, is_team_admin=is_team_admin,
                        photo=photo, photo_thumb=photo_thumb)
            print(user)
            # user.save()
            # if user.photo != None:
            #     if 'http' in user.photo:
            #         print('somossa eikhanei')
            #         user.photo = user.photo.replace("id", str(user.id))
            #         user.save()

            Invitations.objects.filter(email=user.email).delete()  # delete new user from invitation

            if invited_by == None :
                # Email verification task starts here
                user.is_team_admin = True
                user.save()
                code = generate_shortuuid()
                userVerifications = UserVerifications(code=code, user=user, is_used=False, verification_type='email')
                userVerifications.save()

                # send_mail(subject="HouZes email verification",
                #           message="Dear," + str(user.first_name) + ' ' + str(
                #               user.last_name) + " please confirm your email by clicking the link https://" + settings.WEB_APP_URL + '/verify-email/' + str(
                #               code),
                #           from_email=settings.EMAIL_HOST_USER,
                #           recipient_list=[email],
                #           fail_silently=False
                #           )
                subject = "HouZes email verification"
                body = "Please confirm your email by clicking the link below."
                url = "https://" + settings.WEB_APP_URL + '/verify-email/' + str(code)
                SendEmailViewSet.send_email_view(self, subject, body, email, first_name + ' ' + last_name, url)

                # Email verification task ends here

                userSerializer = UserSerializer(user)
                status = True
                data = userSerializer.data
                message = "Please click on the link that has been sent to your email to verify your account."
            else :
                user.is_active = True
                user.save()
                userSerializer = UserSerializer(user)
                status = True
                data = userSerializer.data
                message = "Account successfully created."
        except Exception as exc:
            traceback.print_exc()
            print(exc)
            status = False
            data = None
            message = "Error registering new account"

        return Response({'status': status, 'data': data, 'message': message})

    def partial_update(self, request, *args, **kwargs):
        user = User.objects.get(id=kwargs['pk'])
        message = ''
        if not request.data._mutable:
            state = request.data._mutable
            request.data._mutable = True
        if 'password' in request.data:
            if check_password(request.data['password'],user.password):
                print('SAME PASSWORD')
                return Response({'status': False, 'data': {}, 'message': 'Error! You have entered previously used password'})
            request.data['password'] = make_password(request.data['password'])
            if not 'old_password' in request.data:
                return Response({'status': False, 'data': {}, 'message': 'old password is required'})
            else:
                # user = User.objects.get(id=kwargs['pk'])
                if not user.check_password(request.data['old_password']):
                    return Response({'status': False, 'data': {}, 'message': 'Provide your valid old password'})
                else:
                    message = 'Successfully updated'
        s3_url = ""
        if 'photo' in request.FILES:
            file = request.FILES['photo']
            # file_path = "photos/user/{}/{}".format(kwargs['pk'], str(time.time()) + '.jpg')
            # s3_url = "https://s3.{}.amazonaws.com/{}/{}".format(settings.AWS_REGION, settings.S3_BUCKET_NAME, file_path)
            # file_upload(file, file_path)

            s3_path_prefix = "photos/user/{}/".format(kwargs['pk'])
            file_name = generate_shortuuid() + str(time.time()) + '.png'
            img_data = image_upload(file, s3_path_prefix, file_name, True)
            if img_data["status"]:
                full_img_path = img_data['full_img_url']
                thumb_img_path = img_data['thumb_url']
                request.data['photo'] = full_img_path
                request.data['photo_thumb'] = thumb_img_path
            else:
                return Response({'status': False, 'data': {}, 'message': img_data["msg"]})

        if not request.data._mutable:
            request.data._mutable = state

        message = 'Updated successfully'
        responseData = super().partial_update(request, *args, **kwargs)
        return Response({'status': True, 'data': responseData.data, 'message': message })

        # return super().partial_update(request, *args, **kwargs)

    @action(detail=False, methods=['GET'], url_path='user-verification/code/(?P<code>[\w-]+)')
    def userVericationByCode(self, requset, *args, **kwargs):
        code = kwargs['code']
        status = False
        message = ""

        if UserVerifications.objects.filter(code=code).count() > 0:
            userVerifications = UserVerifications.objects.get(code=code)
            print(userVerifications)
            print(userVerifications.user.id)
            user = User.objects.get(id=userVerifications.user.id)
            print(user)
            user.is_active = True
            user.is_team_admin = True
            user.save()

            status = True
            message = 'Account verification successfull'
        else:
            message = 'Account verification has failed '

        return Response({'status': status, 'message': message})

    @action(detail=False, methods=['GET'], url_path='invitation-key/(?P<key>[\w-]+)')
    def get_unregistered_member_by_invitation_key(self, request, *args, **kwargs):
        invitation_key = kwargs['key']
        invitations = Invitations.objects.filter(invitation_key=invitation_key)
        print(invitations[0])
        invitationsSerializer = InvitationsSerializer(invitations[0])
        return Response(invitationsSerializer.data)

    @action(detail=False, methods=['POST'], url_path='pending-check')
    def user_pending_check(self, request, *args, **kwargs):
        status = False
        message = ""
        try:
            email = request.data['username'].lower().strip()
        except:
            email = request.data['username'].lower().strip()
        if User.objects.filter(email=email).count() > 0:
            user = User.objects.filter(email=email)
            if user[0].is_active == False:
                message = "Please verify your email before sign in"
                return JsonResponse({"status": status, "message": message})
            else:
                status = True
                message = "Ready to log in"
                return JsonResponse({"status": status, "message": message})
        else:
            status = False
            message = 'User does not exist'
            return JsonResponse({"status": status, "message": message})

    def destroy(self, request, *args, **kwargs):
        user_id = kwargs['pk']
        status = False
        message = ""
        try:
            User.objects.get(id=user_id).delete()
        except:
            message = "Error deleting member"
            return Response({'status': status, 'message': message})
        status = True
        message = 'Successfully deleted'
        return Response({'status': status, 'message': message})

    @action(detail=False, methods=['POST'], url_path='fix-password/(?P<key>[\w-]+)')
    def fix_password(self, request, *args, **kwargs):
        link_key = kwargs['key']
        status = False
        data = {}
        message = ''
        try:
            password = request.data['password']
        except:
            password = request.body['password']
        if ForgetPassword.objects.filter(link_key=link_key):
            user = ForgetPassword.objects.filter(link_key=link_key)[0].user
            password = make_password(password)
            user.password = password
            user.save()
            ForgetPassword.objects.filter(user=user).delete()
            status = True
            data = UserSerializer(user).data
            message = 'Password successfully generated'
        else:
            status = False
            data = {}
            message = 'Error'
        return Response({'status': status, 'message': message})
