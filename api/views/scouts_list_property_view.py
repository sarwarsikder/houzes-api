from rest_framework import viewsets
from api.serializers import *
from api.models import *

class ScoutsListPropertyViewSet(viewsets.ModelViewSet):
    queryset = ScoutsListProperty.objects.all()
    serializer_class = ScoutsListPropertySerializer

