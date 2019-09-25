from rest_framework import viewsets, status
from rest_framework.response import Response

from api.serializers import *
from api.models import *



class AssignMemberToListViewSet(viewsets.ModelViewSet):
    queryset = AssignMemberToList.objects.all()
    serializer_class = AssignMemberToListSerializer
    ordering = ['-id']

    def list(self, request, *args, **kwargs):
        queryset = AssignMemberToList.objects.all()
        serializer = AssignMemberToListSerializer(queryset, many=True)

        return Response({'status': status.is_success(Response.status_code),'data': serializer.data,'message': 'list of member assigned to list'})

