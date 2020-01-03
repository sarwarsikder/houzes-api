from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from api.serializers import *
from api.models import *



class GetNeighborhoodViewSet(viewsets.ModelViewSet):
    queryset = GetNeighborhood.objects.all()
    serializer_class = GetNeighborhoodSerializer

    @action(detail=False, methods=['GET'], url_path='property/(?P<id>[\w-]+)')
    def get_neighborhood_by_property_id(self, request, *args, **kwargs):
        property = Property.objects.get(id = kwargs['id'])
        get_neighborhood = GetNeighborhood.objects.filter(property=property)
        get_neighborhood_serializer = GetNeighborhoodSerializer(get_neighborhood, many=True)
        data = get_neighborhood_serializer.data
        return Response(data)