from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response


from api.serializers import *
from api.models import *

class PropertyTagsViewSet(viewsets.ModelViewSet):
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    queryset = PropertyTags.objects.all()
    serializer_class = PropertyTagsSerializer
    # filterset_fields = ["data"]


    def list(self, request, *args, **kwargs):
        queryset = PropertyTags.objects.all().order_by('-id')
        serializer = PropertyTagsSerializer(queryset, many=True)

        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
            try:
                name = request.data['name']
                color = request.data['color']
                color_code = request.data['color_code']
            except:
                name = request.body['name']
                color = request.body['color']
                color_code = request.body['color_code']

            user_id = request.user.id
            user = User.objects.get(id=user_id)
            try:
                propertyTags = PropertyTags(user=user, name=name, color=color,color_code=color_code)
                propertyTags.save()

                propertyTagsSerializer = PropertyTagsSerializer(propertyTags)
                status = True
                data = propertyTagsSerializer.data
                message = name+" tag created"
            except:
                status = False
                data = None
                message = "Error creating property tag"
            return Response({'status': status, 'data': data, 'message': message})

    @action(detail=False)
    def PropertyTags_by_userId(self, request, *args, **kwargs):
        user_id = 4
        user = User.objects.get(id=user_id)
        propertyTags = PropertyTags.objects.filter(user=user)
        print(propertyTags)
        propertyTagsSerializer = PropertyTagsSerializer(propertyTags, many=True)
        return Response(propertyTagsSerializer.data)

    @action(detail=False,methods=['POST'],url_path='property/(?P<id>[\w-]+)/assign-tag')
    def assign_tag_to_property(self,request,*args,**kwargs):
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
                for tag in property.property_tags:
                    if tag['id']==property_tag :
                        message = 'Tag already exist'
                        tagExist = True
                if not tagExist :
                    property.property_tags.append({'id':property_tag})
                    property.save()
                    message = 'Tag added to the property'
                    status = True
                    # propertySerializer = PropertySerializer(property)
                    # data = propertySerializer.data
                    tags= []
                    for tag in property.property_tags:
                        property_tags = PropertyTags.objects.get(id=tag['id'])
                        print(PropertyTagsSerializer(property_tags).data)
                        tags.append(PropertyTagsSerializer(property_tags).data)
                    property_representation = {
                        'id': property.id,
                        'user_list': property.user_list_id,
                        'street': property.street,
                        'city': property.city,
                        'state': property.state,
                        'zip': property.zip,
                        'cad_acct': property.cad_acct,
                        'gma_tag': property.gma_tag,
                        'latitude': property.latitude,
                        'longitude': property.longitude,
                        'property_tags': tags,
                        'owner_info': property.owner_info,
                        'created_at': property.created_at,
                        'updated_at': property.updated_at
                    }
            except:
                message = 'property does not exist'
                status = False
        return Response({'status': status,'data': property_representation,'message': message})