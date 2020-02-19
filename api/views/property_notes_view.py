from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from api.serializers import *
from api.models import *
from rest_framework import status, pagination
from django.http import HttpResponse, JsonResponse

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

    # def get_queryset(self):
    #     return PropertyNotes.objects.filter(user_id=self.request.user.id)

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
        # userId = request.user.id
        # user = User.objects.get(id = userId)
        propertyNotes = PropertyNotes.objects.filter(property=property).order_by('-id')

        paginator = CustomPagination()
        if page_size:
            paginator.page_size = page_size
        else:
            paginator.page_size = 10

        result_page = paginator.paginate_queryset(propertyNotes, request)
        serializer = PropertyNotesSerializer(result_page, many=True)
        return paginator.get_paginated_response(data=serializer.data)

    @action(detail=False, methods=['post'], url_path='property/(?P<id>[\w-]+)/multiple-upload')
    def property_notes_bulk_create(self, request, *args, **kwargs):
        property_id = kwargs['id']
        property = Property.objects.get(id=property_id)
        try:
            requestData = request.data
        except:
            requestData = request.body
        print(requestData)
        objs = []

        for it in requestData:
            property_note = PropertyNotes()
            property_note.title = it['title']
            property_note.title = it['title']
            property_note.notes = it['notes']
            property_note.user = User.objects.get(id = request.user.id)
            property_note.property = property

            objs.append(property_note)

        PropertyNotes.objects.bulk_create(objs, batch_size=50)
        return JsonResponse({'status': True, 'message' : 'Property notes created'})

    def destroy(self, request, *args, **kwargs):
        note_id = kwargs['pk']
        status = False
        message = ""
        try:
            PropertyNotes.objects.get(id = note_id).delete()
        except:
            message = "Error deleting note"
            return Response({'status': status, 'message': message})
        status = True
        message = 'Note deleted successfully'
        return Response({'status': status, 'message': message})

    def partial_update(self, request, *args, **kwargs):
        note_id = kwargs['pk']
        propertyNote = PropertyNotes.objects.get(id=note_id)

        status = False
        data = {}
        message = None

        title = None
        notes = None
        if 'title' in request.data:
            title = request.data['title']
            if title == "":
                message = "Title is required"
                return Response({'status': status, 'data': data, 'message': message})
            else:
                propertyNote.title = title
        if 'notes' in request.data:
            notes = request.data['notes']
            if notes == "":
                message = "Note is required"
                return Response({'status': status, 'data': data, 'message': message})
            else:
                propertyNote.notes = notes

        try:
            propertyNote.save()

            propertyNoteSerializer = PropertyNotesSerializer(propertyNote)
            status = True
            data = propertyNoteSerializer.data
            message = 'Note updated successfully'
        except:
            status = False
            data = {}
            message = 'Error updating note'

        return Response({'status': status, 'data': data, 'message': message})
