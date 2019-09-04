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

    @action(detail=False, methods=['GET'], url_path='get-current-userinfo')
    def get_current_userinfo(self, request):
        access_token = request.META["HTTP_AUTHORIZATION"][7:]
        access_token_object = AccessToken.objects.get(token=access_token)
        user = access_token_object.user
        serializer = UserSerializer(user)
        return JsonResponse(serializer.data, safe=False)


    def create(self, request, *args, **kwargs):
        if not request.data._mutable:
            state = request.data._mutable
            request.data._mutable = True

        data = request.data
        data['password'] = make_password(data['password'])
        data['is_active'] = True
        data['photo'] = "in progress"

        s3_url = ""
        if 'photo' in request.FILES:
            file = request.FILES['photo']
            file_path = "photos/user/{}/{}".format("id", str(time.time())+'.jpg')
            s3_url = "https://s3.{}.amazonaws.com/{}/{}".format(settings.AWS_REGION, settings.S3_BUCKET_NAME, file_path)
            file_upload(file, file_path)
            data['photo'] = s3_url

        if not request.data._mutable:
            request.data._mutable = state

        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        instance = serializer.save()
        instance.is_active = True
        if instance.photo == "in progress":
            instance.photo = None
        else:
            instance.photo = instance.photo.replace("id", str(instance.id))

    #
    # @action(detail=False, methods=['POST'], url_path='user-photo-upload')
    # def user_photo_upload(self, request):

    def partial_update(self, request, *args, **kwargs):

        if not request.data._mutable:
            state = request.data._mutable
            request.data._mutable = True
        # if '_mutable' in request.data.keys():
        #     print('hocce')
        #     state = request.data._mutable
        #     request.data._mutable = True
        print(kwargs['pk'])
        if 'password' in request.data:
            request.data['password'] = make_password(request.data['password'])

        request.data['photo'] = None

        # data['photo'] = str(self.upload_photo(request.FILES, kwargs['pk']))

        s3_url = ""
        if 'photo' in request.FILES:
            file = request.FILES['photo']
            file_path = "photos/user/{}/{}".format(kwargs['pk'], str(time.time()) + '.jpg')
            s3_url = "https://s3.{}.amazonaws.com/{}/{}".format(settings.AWS_REGION, settings.S3_BUCKET_NAME, file_path)
            file_upload(file, file_path)
            request.data['photo'] = s3_url
        # if '_mutable' in request.data:
        #     request.data._mutable = state

        if not request.data._mutable:
            request.data._mutable = state

        return super().partial_update(request, *args, **kwargs)
