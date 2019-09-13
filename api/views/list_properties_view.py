from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from rest_framework import viewsets
from api.serializers import *
from api.models import *

class ListPropertiesViewSet(viewsets.ModelViewSet):
    queryset = ListProperties.objects.all()
    serializer_class = ListPropertiesSerializer
    filterset_fields = ["property_address"]
