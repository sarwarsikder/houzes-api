from rest_framework import viewsets
from api.serializers import *
from api.models import *

class ListPropertiesViewSet(viewsets.ModelViewSet):
    queryset = ListProperties.objects.all()
    serializer_class = ListPropertiesSerializer

