from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from rest_framework import viewsets
from rest_framework import status, pagination
from rest_framework.decorators import action
from rest_framework.response import Response
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
        listProperties = ListProperties.objects.filter(user_list = list)
        print(listProperties)
        # listPropertiesSerializer = ListPropertiesSerializer(listProperties, many=True)

        paginator = CustomPagination()
        if page_size:
            paginator.page_size = page_size
        else:
            paginator.page_size = 10
        # paginator.offset = 0
        result_page = paginator.paginate_queryset(listProperties, request)
        serializer = ListPropertiesSerializer(result_page, many=True)
        return paginator.get_paginated_response(data=serializer.data)