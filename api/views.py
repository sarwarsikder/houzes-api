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
from decimal import Decimal

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

    def create(self, request, *args, **kwargs):
        user_id = 4
        user = User.objects.get(id=user_id)

        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        is_driving = request.POST.get('is_driving')
        angle = request.POST.get('angle')

        if is_driving == 'True':
            is_driving = True
        else:
            is_driving = False
        userLocation = UserLocation(user=user, latitude=Decimal(latitude), longitude=Decimal(longitude),
                                    is_driving=is_driving, angle=Decimal(angle))
        userLocation.save()

        userLocationSerializer = UserLocationSerializer(userLocation)
        return Response(userLocationSerializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False)
    def userLocation_by_userId(self, request, *args, **kwargs):
        user_id = 4
        user = User.objects.get(id=user_id)
        userLocation = UserLocation.objects.filter(user=user)
        print(userLocation)
        userLocationSerializer = UserLocationSerializer(userLocation, many=True)
        return Response(userLocationSerializer.data)


class UserVerificationsViewSet(viewsets.ModelViewSet):
    queryset = UserVerifications.objects.all()
    serializer_class = UserVerificationsSerializer

    def create(self, request, *args, **kwargs):
        user_id = 4
        user = User.objects.get(id=user_id)

        code = request.POST.get('code')
        is_used = request.POST.get('is_used')
        verification_type = request.POST.get('verification_type')

        if is_used == 'True':
            is_used = True
        else:
            is_used = False

        userVerifications = UserVerifications(user=user, code=code, is_used=is_used,
                                              verification_type=verification_type)
        userVerifications.save()

        userVerificationsSerializer = UserVerificationsSerializer(userVerifications)
        return Response(userVerificationsSerializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False)
    def userVerification_by_userId(self, request, *args, **kwargs):
        user_id = 4
        user = User.objects.get(id=user_id)
        userVerifications = UserVerifications.objects.filter(user=user)
        print(userVerifications)
        userVerificationsSerializer = UserVerificationsSerializer(userVerifications, many=True)
        return Response(userVerificationsSerializer.data)


class PropertyTagsViewSet(viewsets.ModelViewSet):
    queryset = PropertyTags.objects.all()
    serializer_class = PropertyTagsSerializer

    def create(self, request, *args, **kwargs):
        user_id = 4
        name = request.POST.get('name')
        color = request.POST.get('color')

        user = User.objects.get(id=user_id)

        propertyTags = PropertyTags(user=user, name=name, color=color)
        propertyTags.save()

        propertyTagsSerializer = PropertyTagsSerializer(propertyTags)
        return Response(propertyTagsSerializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False)
    def PropertyTags_by_userId(self, request, *args, **kwargs):
        user_id = 4
        user = User.objects.get(id=user_id)
        propertyTags = PropertyTags.objects.filter(user=user)
        print(propertyTags)
        propertyTagsSerializer = PropertyTagsSerializer(propertyTags, many=True)
        return Response(propertyTagsSerializer.data)


class PropertyNotesViewSet(viewsets.ModelViewSet):
    queryset = PropertyNotes.objects.all()
    serializer_class = PropertyNotesSerializer

    def get_queryset(self):
        return PropertyNotes.objects.filter(user_id=self.request.user.id)

    def create(self, request, *args, **kwargs):
        request.data['user'] = request.user.id
        return super().create(request, *args, **kwargs)

    #
    # @action(detail=False)
    # def propertyNotes_by_userId(self, request, *args, **kwargs):
    #     user_id = 4
    #     user = User.objects.get(id=user_id)
    #     propertyNotes = PropertyNotes.objects.filter(user=user)
    #     print(propertyNotes)
    #     propertyNotesSerializer = PropertyNotesSerializer(propertyNotes, many=True)
    #     return Response(propertyNotesSerializer.data)


class PropertyPhotosViewSet(viewsets.ModelViewSet):
    queryset = PropertyPhotos.objects.all()
    serializer_class = PropertyPhotosSerializer

    def get_queryset(self):
        return PropertyPhotos.objects.filter(user_id=self.request.user.id)

    def create(self, request, *args, **kwargs):
        request.data['user'] = request.user.id
        return super().create(request, *args, **kwargs)

    # def create(self, request, *args, **kwargs):
    #     user_id = 4
    #     user = User.objects.get(id=user_id)
    #     property_id = request.POST.get('property')
    #     property = Property.objects.get(id=int(property_id))
    #     s3_url = ""
    #
    #     if 'property_photo' in request.FILES:
    #         file = request.FILES['property_photo']
    #         file_path = "photos/property_photos/{}/{}/{}".format(str(user_id), property_id, str(time.time()) + '.jpg')
    #         s3_url = "https://s3.{}.amazonaws.com/{}/{}".format(settings.AWS_REGION, settings.S3_BUCKET_NAME, file_path)
    #         file_upload(file, file_path)
    #
    #     propertyPhotos = PropertyPhotos(user=user, property=property, photo_url=s3_url)
    #     propertyPhotos.save()
    #
    #     propertyPhotosSerializer = PropertyPhotosSerializer(propertyPhotos)
    #     return Response(propertyPhotosSerializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False)
    def propertyPhotos_by_userId(self, request, *args, **kwargs):
        user_id = 4
        user = User.objects.get(id=user_id)
        propertyPhotos = PropertyPhotos.objects.filter(user=user)
        print(propertyPhotos)
        propertyPhotosSerializer = PropertyPhotosSerializer(propertyPhotos, many=True)
        return Response(propertyPhotosSerializer.data)


class UserListViewSet(viewsets.ModelViewSet):
    queryset = UserList.objects.all()
    serializer_class = UserListSerializer

    def get_queryset(self):
        return UserList.objects.filter(user_id=self.request.user.id)

    def create(self, request, *args, **kwargs):
        request.data['user'] = request.user.id
        return super().create(request, *args, **kwargs)


class ListPropertiesViewSet(viewsets.ModelViewSet):
    queryset = ListProperties.objects.all()
    serializer_class = ListPropertiesSerializer


class UserDriverViewSet(viewsets.ModelViewSet):
    queryset = UserDriver.objects.all()
    serializer_class = UserDriverSerializer

    def create(self, request, *args, **kwargs):
        user_id = 4
        user = User.objects.get(id=user_id)
        list = request.POST.get('list')
        distance = request.POST.get('distance')
        travel_shape = request.POST.get('travel_shape')

        userList = UserList.objects.get(id=int(list))

        userDriver = UserDriver(list=userList, user=user, distance=Decimal(distance), travel_shape=travel_shape)
        userDriver.save()

        userDriverSerializer = UserDriverSerializer(userDriver)
        return Response(userDriverSerializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False)
    def userDriver_by_userId(self, request, *args, **kwargs):
        user_id = 4
        user = User.objects.get(id=user_id)
        userDriver = UserDriver.objects.filter(user=user)
        print(userDriver)
        userDriverSerializer = UserDriverSerializer(userDriver, many=True)
        return Response(userDriverSerializer.data)


class UserOwnershipUsageViewSet(viewsets.ModelViewSet):
    queryset = UserOwnershipUsage.objects.all()
    serializer_class = UserOwnershipUsageSerializer

    def create(self, request, *args, **kwargs):
        user_id = 4
        user = User.objects.get(id=user_id)

        property_id = request.POST.get('property')

        property = Property.objects.get(id=int(property_id))

        userOwnershipUsage = UserOwnershipUsage(user=user, property=property)
        userOwnershipUsage.save()

        userOwnershipUsageSerializer = UserOwnershipUsageSerializer(userOwnershipUsage)
        return Response(userOwnershipUsageSerializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False)
    def userOwnershipUsage_by_userId(self, request, *args, **kwargs):
        user_id = 4
        user = User.objects.get(id=user_id)
        userOwnershipUsage = UserOwnershipUsage.objects.filter(user=user)
        print(userOwnershipUsage)
        userOwnershipUsagerSerializer = UserOwnershipUsageSerializer(userOwnershipUsage, many=True)
        return Response(userOwnershipUsagerSerializer.data)


class VisitedPropertiesViewSet(viewsets.ModelViewSet):
    queryset = VisitedProperties.objects.all()
    serializer_class = VisitedPropertiesSerializer


class UserSocketsViewSet(viewsets.ModelViewSet):
    queryset = UserSockets.objects.all()
    serializer_class = UserSocketsSerializer

    def create(self, request, *args, **kwargs):
        user_id = 4
        user = User.objects.get(id=user_id)

        socket_id = request.POST.get('socket_id')
        is_connected = request.POST.get('is_connected')

        if is_connected == 'True':
            is_connected = True
        else:
            is_connected = False

        userSockets = UserSockets(user=user, socket_id=socket_id, is_connected=is_connected)
        userSockets.save()

        userSocketsSerializer = UserSocketsSerializer(userSockets)
        return Response(userSocketsSerializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False)
    def userSockets_by_userId(self, request, *args, **kwargs):
        user_id = 4
        user = User.objects.get(id=user_id)
        userSockets = UserSockets.objects.filter(user=user)
        print(userSockets)
        userSocketsSerializer = UserSocketsSerializer(userSockets, many=True)
        return Response(userSocketsSerializer.data)


class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer

    @action(detail=False)
    def get_details(self, request, *args, **kwargs):
        # property_id = request.data.get('id')
        property_id = 1
        property = Property.objects.get(id=property_id)
        property_with_notes = property.propertynotes_set.all()
        property_with_photos = property.propertyphotos_set.all()
        property = PropertySerializer(property).data
        property['notes'] = PropertyNotesSerializer(property_with_notes, many=True).data
        property['photos'] = PropertyPhotosSerializer(property_with_photos, many=True).data
        return HttpResponse(content=json.dumps(property), status=200, content_type="application/json")

    @action(detail=False)
    def get_info(self, request, *args, **kwargs):
        google_place_id = request.data.get('place_id')
        property = Property.objects.get(google_place_id=google_place_id)
        if property:
            property_with_notes = property.propertynotes_set.all()
            property_with_photos = property.propertyphotos_set.all()
            property = PropertySerializer(property).data
            property['notes'] = PropertyNotesSerializer(property_with_notes, many=True).data
            property['photos'] = PropertyPhotosSerializer(property_with_photos, many=True).data
            return HttpResponse(content=json.dumps(property), status=200, content_type="application/json")

        else:
            return super().create(request, *args, **kwargs)
