from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status,filters,pagination
from rest_framework.response import Response
from rest_framework.utils import json

from api.serializers import *
from api.models import *


class CustomPagination(pagination.PageNumberPagination):
    def get_paginated_response(self, data):
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.page.paginator.count,
            'results': data,
        })
class ActivityLogViewSet(viewsets.ModelViewSet):
    queryset = ActivityLog.objects.all()
    serializer_class = ActivityLogSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    filterset_fields = ["activity"]
    ordering = ['-id']

    def list(self, request, *args, **kwargs):
        page_size = request.GET.get('limit')
        users = User.objects.filter(Q(id=request.user.id) | Q(invited_by=request.user.id))
        activityLog = ActivityLog.objects.filter(user__in = users).order_by('-created_at')
        paginator = CustomPagination()
        if page_size:
            paginator.page_size = page_size
        else:
            paginator.page_size = 10

        result_page = paginator.paginate_queryset(activityLog, request)
        serializer = ActivityLogSerializer(result_page, many=True)
        return paginator.get_paginated_response(data=serializer.data)