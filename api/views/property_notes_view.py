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
        # if '_mutable' in request.data:
        if not request.data._mutable:
            state = request.data._mutable
            request.data._mutable = True

        request.data['user'] = request.user.id

        # if '_mutable' in request.data:
        if not request.data._mutable:
            request.data._mutable = state

        return super().create(request, *args, **kwargs)

    #
    # @action(detail=False)
    # def propertyNotes_by_userId(self, request, *args, **kwargs):
    #     user_id = 4
    #     user = User.objects.get(id=user_id)
    #     propertyNotes = PropertyNotes.objects.filter(user=user)
    #     print(propertyNotes)
    #     propertyNotesSerializer = PropertyNotesSerializer(propertyNotes, many=True)
    #     return Response(propertyNotesSerializer.data)

    @action(detail=False, url_path='property/(?P<pk>[\w-]+)')
    def propertyNotes_by_propertyId(self, request, *args, **kwargs):
        propertyId = kwargs['pk']
        page_size = request.GET.get('limit')
        property = Property.objects.get(id=propertyId)
        userId = request.user.id
        user = User.objects.get(id = userId)
        propertyNotes = PropertyNotes.objects.filter(property=property, user = user)
        print(propertyNotes)
        propertyNotesSerializer = PropertyNotesSerializer(propertyNotes, many=True)

        paginator = CustomPagination()
        if page_size:
            paginator.page_size = page_size
        else:
            paginator.page_size = 10
        # paginator.offset = 0
        result_page = paginator.paginate_queryset(propertyNotes, request)
        serializer = PropertyNotesSerializer(result_page, many=True)
        return paginator.get_paginated_response(data=serializer.data)

        # return Response(propertyNotesSerializer.data)