from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response


from api.serializers import *
from api.models import *

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
