import time

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from api.serializers import *
from api.models import *
from houzes_api import settings
from houzes_api.util.file_upload import file_upload


class PropertyPhotosViewSet(viewsets.ModelViewSet):
    queryset = PropertyPhotos.objects.all()
    serializer_class = PropertyPhotosSerializer

    def get_queryset(self):
        return PropertyPhotos.objects.filter(user_id=self.request.user.id)

    # def create(self, request, *args, **kwargs):
    #     request.data['user'] = request.user.id
    #     return super().create(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        user_id = request.user.id
        user = User.objects.get(id=user_id)
        property_id = request.POST.get('property')
        property = Property.objects.get(id=property_id)
        s3_url = ""

        if 'photo_url' in request.FILES:
            file = request.FILES['photo_url']
            file_path = "photos/property_photos/{}/{}/{}".format(str(user_id), property_id, str(time.time()) + '.jpg')
            s3_url = "https://s3.{}.amazonaws.com/{}/{}".format(settings.AWS_REGION, settings.S3_BUCKET_NAME, file_path)
            file_upload(file, file_path)

        propertyPhotos = PropertyPhotos(user=user, property=property, photo_url=s3_url)
        propertyPhotos.save()

        propertyPhotosSerializer = PropertyPhotosSerializer(propertyPhotos)
        return Response(propertyPhotosSerializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, url_path='current-user')
    def propertyPhotos_by_userId(self, request, *args, **kwargs):
        user_id = request.user.id
        user = User.objects.get(id=user_id)
        propertyPhotos = PropertyPhotos.objects.filter(user=user)
        print(propertyPhotos)
        propertyPhotosSerializer = PropertyPhotosSerializer(propertyPhotos, many=True)
        return Response(propertyPhotosSerializer.data)

    @action(detail=False, url_path='property/(?P<pk>[\w-]+)')
    def propertyPhotos_by_propertyId(self, request, *args, **kwargs):
        propertyId = kwargs['pk']
        propertyPhotos = PropertyPhotos.objects.filter(property=propertyId)
        print(propertyPhotos)
        propertyPhotosSerializer = PropertyPhotosSerializer(propertyPhotos, many=True)
        return Response(propertyPhotosSerializer.data)