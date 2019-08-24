from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from api.serializers import *
from api.models import *

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

