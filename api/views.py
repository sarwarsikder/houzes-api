import datetime
import json
import time
from django.http import JsonResponse
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from oauth2_provider.models import AccessToken
from rest_framework.response import Response
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse
from houzes_api import settings
from houzes_api.util.file_upload import file_upload




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
        data = request.data
        data['password'] = make_password(data['password'])
        data['is_active'] = True
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class UserLocationViewSet(viewsets.ModelViewSet):
    queryset = UserLocation.objects.all()
    serializer_class = UserLocationSerializer

    @action(detail=False)
    def userLocation_by_userId(self,request,*args,**kwargs):
        user_id = 4
        user = User.objects.get(id = user_id)
        userLocation = UserLocation.objects.filter(user = user)
        print(userLocation)
        userLocationSerializer = UserLocationSerializer(userLocation, many=True)
        return Response(userLocationSerializer.data)


class UserVerificationsViewSet(viewsets.ModelViewSet):
    queryset = UserVerifications.objects.all()
    serializer_class = UserVerificationsSerializer

    @action(detail=False)
    def userVerification_by_userId(self,request,*args,**kwargs):
        user_id = 4
        user = User.objects.get(id = user_id)
        userVerifications = UserVerifications.objects.filter(user = user)
        print(userVerifications)
        userVerificationsSerializer = UserVerificationsSerializer(userVerifications, many=True)
        return Response(userVerificationsSerializer.data)


class PropertyTagsViewSet(viewsets.ModelViewSet):
    queryset = PropertyTags.objects.all()
    serializer_class = PropertyTagsSerializer

    @action(detail=False)
    def PropertyTags_by_userId(self,request,*args,**kwargs):
        user_id = 4
        user = User.objects.get(id = user_id)
        propertyTags = PropertyTags.objects.filter(user = user)
        print(propertyTags)
        propertyTagsSerializer = PropertyTagsSerializer(propertyTags, many=True)
        return Response(propertyTagsSerializer.data)


class PropertyNotesViewSet(viewsets.ModelViewSet):
    queryset = PropertyNotes.objects.all()
    serializer_class = PropertyNotesSerializer

    def create(self, request, *args, **kwargs):
        user_id = 4
        user = User.objects.get(id = user_id)
        property_id = request.query_params.get('property')
        print("-----------------------")
        print(property_id)
        print(int(property_id))
        property = PropertyInfo.objects.get(id = int(property_id))
        notes = request.query_params.get('notes')

        propertyNotes = PropertyNotes(user=user,property=property,notes = notes)
        propertyNotes.save()

        return Response('good')

    @action(detail=False)
    def propertyNotes_by_userId(self,request,*args,**kwargs):
        user_id = 4
        user = User.objects.get(id = user_id)
        propertyNotes = PropertyNotes.objects.filter(user = user)
        print(propertyNotes)
        propertyNotesSerializer = PropertyNotesSerializer(propertyNotes, many=True)
        return Response(propertyNotesSerializer.data)

class PropertyPhotosViewSet(viewsets.ModelViewSet):
    queryset = PropertyPhotos.objects.all()
    serializer_class = PropertyPhotosSerializer

    def create(self, request, *args, **kwargs):
        user_id = 4
        user = User.objects.get(id = user_id)
        property_id = request.query_params.get('property')
        property = PropertyInfo.objects.get(id = int(property_id))
        s3_url= ""

        if 'property_photo' in request.FILES:
            file = request.FILES['property_photo']
            file_path = "photos/property_photos/{}/{}/{}".format(str(user_id),property_id, str(time.time())+'.jpg')
            s3_url = "https://s3.{}.amazonaws.com/{}/{}".format(settings.AWS_REGION, settings.S3_BUCKET_NAME, file_path)
            file_upload(file, file_path)

        propertyPhotos = PropertyPhotos(user= user,property=property,photo_url=s3_url)
        propertyPhotos.save()

        return Response('good')

    @action(detail=False)
    def propertyPhotos_by_userId(self,request,*args,**kwargs):
        user_id = 4
        user = User.objects.get(id = user_id)
        propertyPhotos = PropertyPhotos.objects.filter(user = user)
        print(propertyPhotos)
        propertyPhotosSerializer = PropertyPhotosSerializer(propertyPhotos, many=True)
        return Response(propertyPhotosSerializer.data)



class UserListViewSet(viewsets.ModelViewSet):
    queryset = UserList.objects.all()
    serializer_class = UserListSerializer

    @action(detail=False)
    def userList_by_userId(self,request,*args,**kwargs):
        user_id = 4
        user = User.objects.get(id = user_id)
        userList = UserList.objects.filter(user = user)
        print(userList)
        userListSerializer = UserListSerializer(userList, many=True)
        return Response(userListSerializer.data)


class ListPropertiesViewSet(viewsets.ModelViewSet):
    queryset = ListProperties.objects.all()
    serializer_class = ListPropertiesSerializer


class UserDriverViewSet(viewsets.ModelViewSet):
    queryset = UserDriver.objects.all()
    serializer_class = UserDriverSerializer

    @action(detail=False)
    def userDriver_by_userId(self,request,*args,**kwargs):
        user_id = 4
        user = User.objects.get(id = user_id)
        userDriver = UserDriver.objects.filter(user = user)
        print(userDriver)
        userDriverSerializer = UserDriverSerializer(userDriver, many=True)
        return Response(userDriverSerializer.data)


class UserOwnershipUsageViewSet(viewsets.ModelViewSet):
    queryset = UserOwnershipUsage.objects.all()
    serializer_class = UserOwnershipUsageSerializer

    @action(detail=False)
    def userOwnershipUsage_by_userId(self,request,*args,**kwargs):
        user_id = 4
        user = User.objects.get(id = user_id)
        userOwnershipUsage = UserOwnershipUsage.objects.filter(user = user)
        print(userOwnershipUsage)
        userOwnershipUsagerSerializer = UserOwnershipUsageSerializer(userOwnershipUsage, many=True)
        return Response(userOwnershipUsagerSerializer.data)


class VisitedPropertiesViewSet(viewsets.ModelViewSet):
    queryset = VisitedProperties.objects.all()
    serializer_class = VisitedPropertiesSerializer


class UserSocketsViewSet(viewsets.ModelViewSet):
    queryset = UserSockets.objects.all()
    serializer_class = UserSocketsSerializer

    @action(detail=False)
    def userSockets_by_userId(self,request,*args,**kwargs):
        user_id = 4
        user = User.objects.get(id = user_id)
        userSockets = UserSockets.objects.filter(user = user)
        print(userSockets)
        userSocketsSerializer = UserSocketsSerializer(userSockets, many=True)
        return Response(userSocketsSerializer.data)


class PropertyInfoViewSet(viewsets.ModelViewSet):
    queryset = PropertyInfo.objects.all()
    serializer_class = PropertyInfoSerializer

    @action(detail=False)
    def get_details(self,request,*args,**kwargs):
        property_id =1
        propertyInfo = PropertyInfo.objects.get(id=property_id)
        # propertyPhoto = PropertyPhotos.objects.filter(property = propertyInfo)
        # propertyNotes = PropertyNotes.objects.filter(property = propertyInfo)
        #
        # propertyInfoSerializer = PropertyInfoSerializer(propertyInfo,many=True)
        propertyInfoSerializer = PropertyInfoSerializer(propertyInfo)
        print(str(propertyInfoSerializer.data))
        return Response(propertyInfoSerializer.data)