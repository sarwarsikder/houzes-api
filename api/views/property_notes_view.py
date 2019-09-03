from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from api.serializers import *
from api.models import *

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
        request.data['user'] = request.user.id
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

    @action(detail=False)
    def propertyNotes_by_propertyId(self, request, *args, **kwargs):
        propertyId = request.GET.get('property')
        property = Property.objects.get(id=propertyId)
        propertyNotes = PropertyNotes.objects.filter(property=property)
        print(propertyNotes)
        propertyNotesSerializer = PropertyNotesSerializer(propertyNotes, many=True)
        return Response(propertyNotesSerializer.data)