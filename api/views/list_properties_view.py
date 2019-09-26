from django.db.models import Count
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from rest_framework import viewsets
from rest_framework import status, pagination
from rest_framework.decorators import action
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

class ListPropertiesViewSet(viewsets.ModelViewSet):
    queryset = ListProperties.objects.all()
    serializer_class = ListPropertiesSerializer
    filterset_fields = ["property_address"]

    @action(detail=False, url_path='list/(?P<pk>[\w-]+)')
    def list_propertiesByUserList(self, request, *args, **kwargs):
        listId = kwargs['pk']
        page_size = request.GET.get('limit')
        list = UserList.objects.get(id=listId)
        listProperties = ListProperties.objects.filter(user_list = list).annotate(photo_count=Count('property__propertyphotos'),note_count=Count('property__propertynotes'))


        paginator = CustomPagination()
        if page_size:
            paginator.page_size = page_size
        else:
            paginator.page_size = 10

        result_page = paginator.paginate_queryset(listProperties, request)
        serializer = ListPropertiesSerializer(result_page, many=True)
        return paginator.get_paginated_response(data=serializer.data)

    @action(detail=False, methods=['GET'], url_path='tag/(?P<id>[\w-]+)')
    def get_list_property_by_tag(self, request, *args, **kwargs):
        tagId = kwargs['id']
        page_size = request.GET.get('limit')
        listProperties = ListProperties.objects.filter(tag__id = tagId)

        paginator = CustomPagination()
        if page_size:
            paginator.page_size = page_size
        else:
            paginator.page_size = 10

        result_page = paginator.paginate_queryset(listProperties, request)

        serializer = ListPropertiesSerializer(result_page, many=True)
        return paginator.get_paginated_response(data=serializer.data)
