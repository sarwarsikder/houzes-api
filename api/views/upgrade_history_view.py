from rest_framework import viewsets
from rest_framework.decorators import action
from api.models import *
from api.serializers import *
from rest_framework.response import Response

class UpgradeHistoryViewSet(viewsets.ModelViewSet):
    queryset = UpgradeHistory.objects.all()
    serializer_class = UpgradeHistorySerializer