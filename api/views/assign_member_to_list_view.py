from rest_framework import viewsets, status
from api.serializers import *
from api.models import *



class AssignMemberToListViewSet(viewsets.ModelViewSet):
    queryset = AssignMemberToList.objects.all()
    serializer_class = AssignMemberToListSerializer
    ordering = ['-id']