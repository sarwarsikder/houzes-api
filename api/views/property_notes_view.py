from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from api.serializers import *
from api.models import *
from rest_framework import status, pagination

class CustomPagination(pagination.PageNumberPagination):
    def get_paginated_response(self, data):
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.page.paginator.count,
            'results': data,
        })

class PropertyNotesViewSet(viewsets.ModelViewSet):
    queryset = PropertyNotes.objects.all()
    serializer_class = PropertyNotesSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    filterset_fields = "__all__"
    search_fields = ['title', 'notes']
    ordering = ['-id']

    def get_queryset(self):
        return PropertyNotes.objects.filter(user_id=self.request.user.id)

    def create(self, request, *args, **kwargs):

        try:
            propertyId =request.data['property']
            if 'title' in request.data:
                title = request.data['title']
            else:
                status = False
                message = "Title is not given"
                data = None
                return Response({'status': status, 'data': data, 'message': message})
            if 'notes' in request.data:
                notes = request.data['notes']
            else:
                status = False
                message = "Note is not given"
                data = None
                return Response({'status': status, 'data': data, 'message': message})
        except:
            propertyId = request.body['property']
            if 'title' in request.body:
                title = request.body['title']
            else:
                status = False
                message = "Title is not given"
                data = None
                return Response({'status': status, 'data': data, 'message': message})
            if 'notes' in request.body:
                notes = request.body['notes']
            else:
                status = False
                message = "Note is not given"
                data = None
                return Response({'status': status, 'data': data, 'message': message})

        userId = request.user.id
        user = User.objects.get(id=userId)
        property = Property.objects.get(id=propertyId)

        try:
            propertyNotes = PropertyNotes(property=property,notes=notes,title=title,user=user)
            propertyNotes.save()
            data = PropertyNotesSerializer(propertyNotes).data
            status = True
            message = "Property note inserted"

        except:
            status = False
            data = None
            message = "Error in  property note insertion"

        return Response({'status': status, 'data': data, 'message': message})

    @action(detail=False, url_path='property/(?P<pk>[\w-]+)')
    def get_propertyNotes_by_propertyId(self, request, *args, **kwargs):
        propertyId = kwargs['pk']
        page_size = request.GET.get('limit')
        property = Property.objects.get(id=propertyId)
        userId = request.user.id
        user = User.objects.get(id = userId)
        propertyNotes = PropertyNotes.objects.filter(property=property, user = user).order_by('-id')

        paginator = CustomPagination()
        if page_size:
            paginator.page_size = page_size
        else:
            paginator.page_size = 10

        result_page = paginator.paginate_queryset(propertyNotes, request)
        serializer = PropertyNotesSerializer(result_page, many=True)
        return paginator.get_paginated_response(data=serializer.data)

