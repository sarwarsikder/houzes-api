from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import action

from api.serializers import *
from api.models import *



class HistoryDetailViewSet(viewsets.ModelViewSet):
    queryset = HistoryDetail.objects.all()
    serializer_class = HistoryDetailSerializer
    ordering = ['-id']

    @action(detail=False, url_path='history/(?P<id>[\w-]+)')
    def get_history_details_by_history_id(self, request, *args, **kwargs):
        history_id = kwargs['id']
        history = History.objects.get(id = history_id)
        history_detail = HistoryDetail.objects.filter(history=history)
        data = HistoryDetailSerializer(history_detail,many=True).data
        return Response(data)
