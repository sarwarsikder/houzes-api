import json

from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, pagination,filters
from rest_framework.decorators import action
from django.http import HttpResponse, JsonResponse
from api.serializers import *
from api.models import *
from rest_framework.response import Response

class CustomPagination(pagination.PageNumberPagination):
    def get_paginated_response(self, data):
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.page.paginator.count,
            'results': data,
        })

class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    filterset_fields = ["street"]
    ordering = ['-id']

    def retrieve(self, request, *args, **kwargs):
        property_id = kwargs['pk']
        property = Property.objects.get(id=property_id)
        tags = []
        try:
            user_list_id = property.user_list.id
        except:
            user_list_id = None

        for tag in property.property_tags:
            property_tags = PropertyTags.objects.get(id=tag['id'])
            print(PropertyTagsSerializer(property_tags).data)
            tags.append(PropertyTagsSerializer(property_tags).data)

        property_representation = {
            'id' : property.id,
            'user_list' : user_list_id,
            'street': property.street,
            'city': property.city,
            'state': property.state,
            'zip': property.zip,
            'cad_acct': property.cad_acct,
            'gma_tag': property.gma_tag,
            'latitude' : property.latitude,
            'longitude' : property.longitude,
            'property_tags' : tags,
            'owner_info' : property.owner_info,
            'photos' : PropertyPhotosSerializer(PropertyPhotos.objects.filter(property=property),many=True).data,
            'notes': PropertyNotesSerializer(PropertyNotes.objects.filter(property=property),many=True).data,
            'created_at': property.created_at,
            'updated_at' : property.updated_at
        }
        return Response(property_representation)

    def create(self, request, *args, **kwargs):
        street = ""
        city = ""
        state = ""
        zip = ""
        cad_acct = ""
        gma_tag = None
        latitude = None
        longitude = None
        property_tags = []
        owner_info =  []
        user_list = None

        status = False
        data = {}
        message =""

        try:
            if 'street' in request.data:
                street = request.data['street']
            if 'city' in request.data:
                city = request.data['city']
            if 'state' in request.data:
                state = request.data['state']
            if 'zip' in request.data:
                zip = request.data['zip']
            if 'cad_acct' in request.data:
                cad_acct = request.data['cad_acct']
            if 'gma_tag' in request.data:
                gma_tag = request.data['gma_tag']
            if 'latitude' in request.data:
                latitude = request.data['latitude']
            if 'longitude' in request.data:
                longitude = request.data['longitude']
            if 'property_tags' in request.data:
                property_tags = request.data['property_tags']
            if 'owner_info' in request.data:
                owner_info = request.data['owner_info']
            if 'user_list' in request.data:
                user_list = request.data['user_list']
                user_list = UserList.objects.get(id=user_list)

        except:
            if 'street' in request.body:
                street = request.body['street']
            if 'city' in request.body:
                city = request.body['city']
            if 'state' in request.body:
                state = request.body['state']
            if 'zip' in request.body:
                zip = request.body['zip']
            if 'cad_acct' in request.body:
                cad_acct = request.body['cad_acct']
            if 'gma_tag' in request.body:
                gma_tag = request.body['gma_tag']
            if 'latitude' in request.body:
                latitude = request.body['latitude']
            if 'longitude' in request.body:
                longitude = request.body['longitude']
            if 'property_tags' in request.body:
                property_tags = request.body['property_tags']
            if 'owner_info' in request.body:
                owner_info = request.body['owner_info']
            if 'user_list' in request.body:
                user_list = request.body['user_list']
                user_list = UserList.objects.get(id=user_list)
        try:
            property = Property(street=street,city=city,state=state,zip=zip,cad_acct=cad_acct,gma_tag=gma_tag,latitude=latitude,longitude=longitude,property_tags=property_tags,owner_info=owner_info,user_list=user_list)
            property.save()

            status = True
            data = PropertySerializer(property).data
            message = "Successfully created property"
        except:
            status = False
            data = {}
            message = "Failed to create property"
        return Response({'status': status, 'data' : data, 'message' : message})

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
        try:
            requestData = request.data
        except:
            requestData = request.body
        print(requestData)
        objs = []
        iterator=0
        while iterator< len(requestData['cities']):
            property = Property()
            property.owner_info = json.loads('[{"ownerName" : "'+requestData['ownerName'][iterator]+'","ownerAddress" : "'+requestData['ownerAddress'][iterator]+'"}]')
            property.street = requestData['streets'][iterator]
            property.zip = requestData['zips'][iterator]
            property.city = requestData['cities'][iterator]
            property.state = requestData['states'][iterator]
            property.user_list_id = requestData['user_list']

            objs.append(property)

            iterator+=1

        Property.objects.bulk_create(objs, batch_size=50)
        return JsonResponse({'status': True, 'message' : 'Properties created'})

    # @action(detail=False, methods=['GET'], url_path='tag/(?P<id>[\w-]+)')
    # def get_property_by_tag(self, request, *args, **kwargs):
    #     tagId = kwargs['id']
    #     property = Property.objects.filter(property_tags__id = tagId)
    #     propertySerializer = PropertySerializer(property, many=True).data
    #     return HttpResponse(content=json.dumps(propertySerializer), status=200, content_type="application/json")


    @action(detail=False, url_path='list/(?P<pk>[\w-]+)')
    def get_properties_by_user_list(self, request, *args, **kwargs):
        listId = kwargs['pk']
        page_size = request.GET.get('limit')
        list = UserList.objects.get(id=listId)
        property = Property.objects.filter(user_list = list).annotate(photo_count=Count('propertyphotos'),note_count=Count('propertynotes')).order_by('-id')


        paginator = CustomPagination()
        if page_size:
            paginator.page_size = page_size
        else:
            paginator.page_size = 10

        result_page = paginator.paginate_queryset(property, request)
        serializer = PropertySerializer(result_page, many=True)
        return paginator.get_paginated_response(data=serializer.data)

    @action(detail=False, methods=['GET'], url_path='tag/(?P<id>[\w-]+)')
    def get_property_by_tag(self, request, *args, **kwargs):
        tagId = kwargs['id']
        page_size = request.GET.get('limit')
        property = Property.objects.filter(property_tags__contains = [{'id': int(tagId,10) }])
        paginator = CustomPagination()
        if page_size:
            paginator.page_size = page_size
        else:
            paginator.page_size = 10

        result_page = paginator.paginate_queryset(property, request)

        serializer = PropertySerializer(result_page, many=True)
        return paginator.get_paginated_response(data=serializer.data)

    def destroy(self, request, *args, **kwargs):
        property_id = kwargs['pk']
        try:
            Property.objects.get(id = property_id).delete()
            status = True
            message = "Property deleted"
        except:
            status = False
            message = "Error deleting property or property does not exist"
        return Response({'status': status, 'message': message})

    def partial_update(self, request, *args, **kwargs):
        status = False
        data ={}
        message = ""

        # res = super().partial_update(request, *args, **kwargs)
        property = Property.objects.get(id=kwargs['pk'])
        try:
            if 'street' in request.data:
                property.street = request.data['street']
            if 'city' in request.data:
                property.city = request.data['city']
            if 'state' in request.data:
                property.state = request.data['state']
            if 'zip' in request.data:
                property.zip = request.data['zip']
            if 'cad_acct' in request.data:
                property.cad_acct = request.data['cad_acct']
            if 'gma_tag' in request.data:
                property.gma_tag = request.data['gma_tag']
            if 'latitude' in request.data:
                property.latitude = request.data['latitude']
            if 'longitude' in request.data:
                property.longitude = request.data['longitude']
            if 'property_tags' in request.data:
                property.property_tags = request.data['property_tags']
            if 'owner_info' in request.data:
                property.owner_info = request.data['owner_info']
        except:
            if 'street' in request.body:
                property.street = request.body['street']
            if 'city' in request.body:
                property.city = request.body['city']
            if 'state' in request.body:
                property.state = request.body['state']
            if 'zip' in request.body:
                property.zip = request.body['zip']
            if 'cad_acct' in request.body:
                property.cad_acct = request.body['cad_acct']
            if 'gma_tag' in request.body:
                property.gma_tag = request.body['gma_tag']
            if 'latitude' in request.body:
                property.latitude = request.body['latitude']
            if 'longitude' in request.body:
                property.longitude = request.body['longitude']
            if 'property_tags' in request.body:
                property.property_tags = request.body['property_tags']
            if 'owner_info' in request.body:
                property.owner_info = request.body['owner_info']
        try:
            property.save()
            status = True
            data = PropertySerializer(property).data
            message = "Property updated successfully"
        except:
            status = False
            data = {}
            message = "Please provide all the field correctly"
        return Response({'status': status, 'data' : data, 'message' : message})
