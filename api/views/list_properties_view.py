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
        print(tagId)
        page_size = request.GET.get('limit')
        listProperties = ListProperties.objects.filter(property_tags__contains = [{'id' : 8 }])
        print(listProperties)
        paginator = CustomPagination()
        if page_size:
            paginator.page_size = page_size
        else:
            paginator.page_size = 10

        result_page = paginator.paginate_queryset(listProperties, request)

        serializer = ListPropertiesSerializer(result_page, many=True)
        return paginator.get_paginated_response(data=serializer.data)

    @action(detail=False,methods=['POST'],url_path='(?P<id>[\w-]+)/assign-tag')
    def assign_tag_to_list_property(self,request,*args,**kwargs):
        listPropertiesId = kwargs['id']
        status = False
        data = None
        message=""
        try:
            property_tag = request.data['tag']
        except :
            property_tag = request.body['tag']

        if PropertyTags.objects.filter(id=property_tag).count()==0:
            message="Missing tag"
        else:
            try:
                tagExist = False
                listProperties = ListProperties.objects.get(id=listPropertiesId)
                print(listProperties.property_tags)
                for tag in listProperties.property_tags:
                    if tag['id']==property_tag :
                        message = 'Tag already exist'
                        tagExist = True
                if not tagExist :
                    print(type(listProperties.property_tags))
                    listProperties.property_tags.append({'id':property_tag})
                    listProperties.save()
                    message = 'Tag added to the property'
                    status = True
                    listPropertiesSerializer = ListPropertiesSerializer(listProperties)
                    data = listPropertiesSerializer.data
            except:
                message = 'property does not exist'
                status = False
        return Response({'status': status,'data': data,'message': message})
