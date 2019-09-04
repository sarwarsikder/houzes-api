import json
from rest_framework import viewsets
from rest_framework.decorators import action
from django.http import HttpResponse
from api.serializers import *
from api.models import *

class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer

    @action(detail=False,url_path='property')
    def get_details(self, request, *args, **kwargs):
        # property_id = request.data.get('id')
        property_id = request.GET.get('id')
        property = Property.objects.get(id=property_id)
        property_with_notes = property.propertynotes_set.all()
        property_with_photos = property.propertyphotos_set.all()
        property = PropertySerializer(property).data
        property['notes'] = PropertyNotesSerializer(property_with_notes, many=True).data
        property['photos'] = PropertyPhotosSerializer(property_with_photos, many=True).data
        return HttpResponse(content=json.dumps(property), status=200, content_type="application/json")

    @action(detail=False, url_path='google-place')
    def get_info(self, request, *args, **kwargs):
        google_place_id = request.GET.get('id')
        property = Property.objects.get(google_place_id=google_place_id)
        if property:
            property_with_notes = property.propertynotes_set.all()
            property_with_photos = property.propertyphotos_set.all()
            property = PropertySerializer(property).data
            property['notes'] = PropertyNotesSerializer(property_with_notes, many=True).data
            property['photos'] = PropertyPhotosSerializer(property_with_photos, many=True).data
            return HttpResponse(content=json.dumps(property), status=200, content_type="application/json")

        else:
            return super().create(request, *args, **kwargs)
