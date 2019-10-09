import json
from rest_framework import viewsets, pagination
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
    filterset_fields = ["street"]

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

    # @action(detail=False, methods=['post'], url_path='bulk-create')
    # def property_bulk_create(self, request, *args, **kwargs):
    #     requestData = request.data
    #
    #     objs = []
    #     iterator=0
    #     while iterator< len(requestData['street']):
    #         property = Property()
    #         property.owner_info = json.loads('[{"ownerName" : "'+requestData['ownerName'][iterator]+'","ownerAddress" : "'+requestData['ownerAddress'][iterator]+'"}]')
    #         property.street = requestData['street'][iterator]
    #         property.zip = requestData['zip'][iterator]
    #         property.city = requestData['city'][iterator]
    #         property.state = requestData['state'][iterator]
    #
    #
    #         property_create = Property(owner_info= property.owner_info,street=property.street,zip = property.zip,state=property.state,city=property.city)
    #         property_create.save()
    #
    #         list_property = ListProperties()
    #         list_property.user_list_id = requestData['list']
    #         list_property.property_id = property_create.id
    #         list_property.property_address = requestData['propertyAddress'][iterator]
    #         list_property.owner_info = json.loads('[{"ownerName" : "'+requestData['ownerName'][iterator]+'","ownerAddress" : "'+requestData['ownerAddress'][iterator]+'"}]')
    #
    #         objs.append(list_property)
    #
    #         iterator+=1
    #
    #     ListProperties.objects.bulk_create(objs, batch_size=50)
    #
    #     return JsonResponse({'response': 'success'})

    @action(detail=False, methods=['GET'], url_path='tag/(?P<id>[\w-]+)')
    def get_property_by_tag(self, request, *args, **kwargs):
        tagId = kwargs['id']
        property = Property.objects.filter(property_tags__id = tagId)
        propertySerializer = PropertySerializer(property, many=True).data
        return HttpResponse(content=json.dumps(propertySerializer), status=200, content_type="application/json")

    @action(detail=False,methods=['GET'],url_path='(?P<id>[\w-]+)/note')
    def get_note_by_property(self, request, *args, **kwargs):
        propertyId = kwargs['id']
        property = Property.objects.get(id=propertyId)
        propertyNotes = PropertyNotes.objects.filter(property = property)
        propertyNotesSerializer = PropertyNotesSerializer(propertyNotes,many=True)
        return HttpResponse(content=json.dumps(propertyNotesSerializer.data), status=200, content_type="application/json")

    @action(detail=False, url_path='list/(?P<pk>[\w-]+)')
    def list_propertiesByUserList(self, request, *args, **kwargs):
        listId = kwargs['pk']
        page_size = request.GET.get('limit')
        list = UserList.objects.get(id=listId)
        property = Property.objects.filter(user_list = list).annotate(photo_count=Count('property__propertyphotos'),note_count=Count('property__propertynotes'))


        paginator = CustomPagination()
        if page_size:
            paginator.page_size = page_size
        else:
            paginator.page_size = 10

        result_page = paginator.paginate_queryset(property, request)
        serializer = PropertySerializer(result_page, many=True)
        return paginator.get_paginated_response(data=serializer.data)

    @action(detail=False, methods=['GET'], url_path='tag/(?P<id>[\w-]+)')
    def get_list_property_by_tag(self, request, *args, **kwargs):
        tagId = kwargs['id']
        print(type(tagId))
        page_size = request.GET.get('limit')
        property = Property.objects.filter(property_tags__contains = [{'id' : int(tagId,10) }])
        print(property)
        paginator = CustomPagination()
        if page_size:
            paginator.page_size = page_size
        else:
            paginator.page_size = 10

        result_page = paginator.paginate_queryset(property, request)

        serializer = PropertySerializer(result_page, many=True)
        return paginator.get_paginated_response(data=serializer.data)

    @action(detail=False,methods=['POST'],url_path='(?P<id>[\w-]+)/assign-tag')
    def assign_tag_to_list_property(self,request,*args,**kwargs):
        propertyId = kwargs['id']
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
                property = Property.objects.get(id=propertyId)
                print(property.property_tags)
                for tag in property.property_tags:
                    if tag['id']==property_tag :
                        message = 'Tag already exist'
                        tagExist = True
                if not tagExist :
                    print(type(property.property_tags))
                    property.property_tags.append({'id':property_tag})
                    property.save()
                    message = 'Tag added to the property'
                    status = True
                    propertySerializer = PropertySerializer(property)
                    data = PropertySerializer.data
            except:
                message = 'property does not exist'
                status = False
        return Response({'status': status,'data': data,'message': message})