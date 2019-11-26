from rest_framework import viewsets
from api.serializers import *
from api.models import *

class ScoutUserListViewSet(viewsets.ModelViewSet):
    queryset = ScoutUserList.objects.all()
    serializer_class = ScoutUserListSerializer

