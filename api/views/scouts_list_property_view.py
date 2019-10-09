from rest_framework import viewsets
from api.serializers import *
from api.models import *

class ScoutsListPropertyViewSet(viewsets.ModelViewSet):
    queryset = ScoutsProperty.objects.all()
    serializer_class = ScoutsPropertySerializer

