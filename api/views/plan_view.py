from rest_framework import viewsets
from api.models import *
from api.serializers import *

class PlanViewSet(viewsets.ModelViewSet):
    queryset = Plans.objects.all()
    serializer_class = PlanSerializer