from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from notifications.signals import notify
from rest_framework import filters, pagination
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.models import *
from api.serializers import *

class PropertiesFilterByTagPagination(pagination.PageNumberPagination):
    def get_paginated_response(self, data):
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.page.paginator.count,
            'results': data
        })

class PropertyTagsViewSet(viewsets.ModelViewSet):
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    queryset = PropertyTags.objects.all()
    serializer_class = PropertyTagsSerializer

    # filterset_fields = ["data"]

    def list(self, request, *args, **kwargs):
        # queryset = PropertyTags.objects.all().order_by('-id')
        user = User.objects.get(id = request.user.id)
        if user.is_admin == False:
            user = User.objects.get(id = user.invited_by)
        queryset = PropertyTags.objects.filter(Q(user = user) | Q(user = None)).order_by('-id')
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
            propertyTags = PropertyTags(user=user, name=name, color=color, color_code=color_code)
            propertyTags.save()

            propertyTagsSerializer = PropertyTagsSerializer(propertyTags)
            status = True
            data = propertyTagsSerializer.data
            message = name + " tag created"
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

    @action(detail=False, methods=['POST'], url_path='property/(?P<id>[\w-]+)/assign-tag')
    def assign_tag_to_property(self, request, *args, **kwargs):
        propertyId = kwargs['id']
        status = False
        data = None
        message = ""
        try:
            property_tag = request.data['tag']
        except:
            property_tag = request.body['tag']

        if PropertyTags.objects.filter(id=property_tag).count() == 0:
            message = "Missing tag"
        else:
            try:
                tagExist = False
                property = Property.objects.get(id=propertyId)
                for tag in property.property_tags:
                    if tag['id'] == property_tag:
                        message = 'Tag already exist'
                        tagExist = True
                if not tagExist:
                    property.property_tags.append({'id': property_tag})
                    property.save()
                    message = 'Tag added to the property'
                    status = True
                    # propertySerializer = PropertySerializer(property)
                    # data = propertySerializer.data
                    tags = []
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
                    try:
                        user = User.objects.get(id=request.user.id)
                        notify.send(user, recipient=user,
                                    verb='tagged a property', action_object=property)
                    except:
                        print('Error in notification')
            except:
                message = 'property does not exist'
                status = False
        return Response({'status': status, 'data': property_representation, 'message': message})

    def destroy(self, request, *args, **kwargs):
        print(kwargs['pk'])
        tag_id = kwargs['pk']
        status = False
        message = ''
        property = Property.objects.filter(property_tags__icontains=tag_id)
        try:
            for p in property:
                tag_temp = []
                for t in p.property_tags:
                    if str(t['id']) != tag_id:
                        tag_temp.append(t)
                p.property_tags = tag_temp
                p.save()
            property_tags = PropertyTags.objects.get(id = tag_id).delete()
            status = True
            message = 'Property tag is deleted'
        except:
            status = False
            message = 'Error deleting property tag'

        return Response({'status': status, 'message': message})

    @action(detail=False, methods=['GET'], url_path='(?P<pk>[\w-]+)/property-cluster')
    def property_by_tag(self, request, *args, **kwargs):
        try:
            if "members" in request.GET:
                userList = UserList.objects.filter(user__in=list(map(int, request.GET.get("members").split(","))))
                property = Property.objects.filter(Q(user_list__in=userList) & (
                        Q(property_tags__contains=[{'id': kwargs['pk']}]) | Q(
                    property_tags__contains=[{'id': int(kwargs['pk'], 10)}])))
                page_size = 1000

                paginator = PropertiesFilterByTagPagination()
                if page_size:
                    paginator.page_size = page_size
                else:
                    paginator.page_size = 1000

                result_page = paginator.paginate_queryset(property, request)
                serializer = ClusterViewByListSerializer(result_page, many=True)
                return paginator.get_paginated_response(data=serializer.data)
            else:
                userList = UserList.objects.filter(user=request.user)
                property = Property.objects.filter(Q(user_list__in=userList) &(Q(property_tags__contains=[{'id': kwargs['pk']}]) | Q(property_tags__contains=[{'id': int(kwargs['pk'], 10)}])))
                page_size = request.GET.get('limit')


                paginator = PropertiesFilterByTagPagination()
                if page_size:
                    paginator.page_size = page_size
                else:
                    paginator.page_size = 1000

                result_page = paginator.paginate_queryset(property, request)
                serializer = ClusterViewByListSerializer(result_page, many=True)
                return paginator.get_paginated_response(data=serializer.data)
        except:
            print("-----")
        return Response({'next': None, 'previous': None, 'count': 0, 'results': []})
