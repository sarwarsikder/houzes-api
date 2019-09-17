import json
from rest_framework import viewsets
from rest_framework.decorators import action
from django.http import HttpResponse, JsonResponse
from api.serializers import *
from api.models import *


class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    filterset_fields = ["property_address"]

    @action(detail=False, url_path='info/(?P<pk>[\w-]+)')
    def get_details_by_google_place_id(self, request, *args, **kwargs):
        property_id = kwargs['pk']
        property = Property.objects.get(id=property_id)
        property_with_notes = property.propertynotes_set.all()
        property_with_photos = property.propertyphotos_set.all()
        property = PropertySerializer(property).data
        property['notes'] = PropertyNotesSerializer(property_with_notes, many=True).data
        property['photos'] = PropertyPhotosSerializer(property_with_photos, many=True).data
        return HttpResponse(content=json.dumps(property), status=200, content_type="application/json")

    @action(detail=False, url_path='google-place/(?P<id>[\w-]+)')
    def get_info(self, request, *args, **kwargs):
        google_place_id = kwargs['id']
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

    @action(detail=False, methods=['post'], url_path='bulk-create')
    def property_bulk_create(self, request, *args, **kwargs):
        requestData = request.data

        objs = []
        iterator=0
        while iterator< len(requestData['propertyAddress']):
            property = Property()
            property.owner_info = json.loads('[{"ownerName" : "'+requestData['ownerName'][iterator]+'","ownerAddress" : "'+requestData['ownerAddress'][iterator]+'"}]')
            property.property_address = requestData['propertyAddress'][iterator]

            property_create = Property(owner_info= property.owner_info,property_address=property.property_address)
            property_create.save()

            list_property = ListProperties()
            list_property.user_list_id = requestData['list']
            list_property.property_id = property_create.id
            list_property.property_address = requestData['propertyAddress'][iterator]
            list_property.owner_info = json.loads('[{"ownerName" : "'+requestData['ownerName'][iterator]+'","ownerAddress" : "'+requestData['ownerAddress'][iterator]+'"}]')

            objs.append(list_property)

            iterator+=1

        ListProperties.objects.bulk_create(objs, batch_size=50)

        return JsonResponse({'response': 'success'})

    @action(detail=False, methods=['GET'], url_path='tag/(?P<id>[\w-]+)')
    def get_property_by_tag(self, request, *args, **kwargs):
        tagId = kwargs['id']
        property = Property.objects.filter(property_tags__id = tagId)
        propertySerializer = PropertySerializer(property, many=True).data
        return HttpResponse(content=json.dumps(propertySerializer), status=200, content_type="application/json")
