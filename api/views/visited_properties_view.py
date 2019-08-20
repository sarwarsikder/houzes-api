from rest_framework import viewsets
from api.serializers import *
from api.models import *

class VisitedPropertiesViewSet(viewsets.ModelViewSet):
    queryset = VisitedProperties.objects.all()
    serializer_class = VisitedPropertiesSerializer
