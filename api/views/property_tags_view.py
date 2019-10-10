from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response


from api.serializers import *
from api.models import *

class PropertyTagsViewSet(viewsets.ModelViewSet):
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    queryset = PropertyTags.objects.all()
    serializer_class = PropertyTagsSerializer
    # filterset_fields = ["data"]


    def list(self, request, *args, **kwargs):
        queryset = PropertyTags.objects.all()
        serializer = PropertyTagsSerializer(queryset, many=True)

        return Response({'status': status.is_success(Response.status_code), 'data': serializer.data,
                         'message': 'list of property tags'})

    def create(self, request, *args, **kwargs):
            try:
                name = request.data['name']
                color = request.data['color']
                color_code = request.data['color_code']
            except:
                name = request.body['name']
                color = request.body['color']
                color_code = request.body['color_code']

            user_id = request.user.id
            user = User.objects.get(id=user_id)
            try:
                propertyTags = PropertyTags(user=user, name=name, color=color,color_code=color_code)
                propertyTags.save()

                propertyTagsSerializer = PropertyTagsSerializer(propertyTags)
                status = True
                data = propertyTagsSerializer.data
                message = name+" tag created"
            except:
                status = False
                data = None
                message = "Error creating property tag"
            return Response({'status': status, 'data': data, 'message': message})

    @action(detail=False)
    def PropertyTags_by_userId(self, request, *args, **kwargs):
        user_id = 4
        user = User.objects.get(id=user_id)
        propertyTags = PropertyTags.objects.filter(user=user)
        print(propertyTags)
        propertyTagsSerializer = PropertyTagsSerializer(propertyTags, many=True)
        return Response(propertyTagsSerializer.data)
