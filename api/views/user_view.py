import os
import sys

from django.http import JsonResponse
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from oauth2_provider.models import AccessToken
from rest_framework.response import Response
from django.contrib.auth.hashers import make_password
from houzes_api import settings
from houzes_api.util.file_upload import file_upload
import time

from api.serializers import *
from api.models import *



class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)

    @action(detail=False, methods=['GET'], url_path='get-current-user-info')
    def get_current_userinfo(self, request):
        access_token = request.META["HTTP_AUTHORIZATION"][7:]
        access_token_object = AccessToken.objects.get(token=access_token)
        user = access_token_object.user
        serializer = UserSerializer(user)
        return JsonResponse(serializer.data, safe=False)


    def create(self, request, *args, **kwargs):
        # if '_mutable' in request.data:
        #     if not request.data._mutable:
        #         state = request.data._mutable
        #         request.data._mutable = True
        #
        # data = request.data
        # data['password'] = make_password(data['password'])
        # data['is_active'] = True
        password = None
        first_name =None
        last_name = None
        email = None
        phone_number = None
        invited_by = None
        is_active = False
        is_admin = False
        photo = None

        try:
            password = make_password(request.data['password'])
            first_name = request.data['first_name']
            last_name = request.data['last_name']
            email = request.data['email']
            phone_number = request.data['phone_number']
            print(request.data)
            invited_by = request.data['invited_by']
            is_active = request.data['is_active']
            is_admin = request.data['is_admin']

        except:
            print('noooooooooooooooooooo')

        try:
            s3_url = ""
            if 'photo' in request.FILES:
                # data['photo'] = "in progress"
                file = request.FILES['photo']
                file_path = "photos/user/{}/{}".format("id", str(time.time())+'.jpg')
                s3_url = "https://s3.{}.amazonaws.com/{}/{}".format(settings.AWS_REGION, settings.S3_BUCKET_NAME, file_path)
                file_upload(file, file_path)
                request.data['photo'] = s3_url
                photo = s3_url
        except:
            print('photo invalid')

        user = User(email=email,password=password,first_name=first_name,last_name=last_name,phone_number=phone_number,invited_by=invited_by,is_active=is_active,is_admin=is_admin,photo=photo)
        user.save()
        if user.photo !=None:
            if 'http' in user.photo:
                user.photo = user.photo.replace("id",str(user.id))
                user.save()
        userSerializer = UserSerializer(user)
        return Response(userSerializer.data, status=status.HTTP_201_CREATED)

    # def perform_create(self, serializer):
    #     instance = serializer.save()
    #     instance.is_active = True
    #     try:
    #         if "http" in instance.photo :
    #             instance.photo = instance.photo.replace("id", str(instance.id))
    #     except:
    #         print('----------------')


    def partial_update(self, request, *args, **kwargs):
        if not request.data._mutable:
            state = request.data._mutable
            request.data._mutable = True
        if 'password' in request.data:
            request.data['password'] = make_password(request.data['password'])

        s3_url = ""
        if 'photo' in request.FILES:
            file = request.FILES['photo']
            file_path = "photos/user/{}/{}".format(kwargs['pk'], str(time.time()) + '.jpg')
            s3_url = "https://s3.{}.amazonaws.com/{}/{}".format(settings.AWS_REGION, settings.S3_BUCKET_NAME, file_path)
            file_upload(file, file_path)
            request.data['photo'] = s3_url

        if not request.data._mutable:
            request.data._mutable = state
        return super().partial_update(request, *args, **kwargs)
        # except Exception as e:
        #     exc_type, exc_obj, exc_tb = sys.exc_info()
        #     fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        #     log = "----------- Error: " + str(exc_obj) + ", File: " + fname + ", Line: " + str(
        #         exc_tb.tb_lineno) + " ------------"
        #     print(log)
        #     return ''