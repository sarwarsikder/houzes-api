from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters, pagination
from rest_framework.decorators import action
from rest_framework.response import Response
import threading
from django.http import HttpResponse, JsonResponse
from math import radians, cos, sin, asin, sqrt
from api.serializers import *
from api.models import *

class CustomPagination(pagination.PageNumberPagination):
    def get_paginated_response(self, data):
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.page.paginator.count,
            'results': data,
        })


class UserListViewSet(viewsets.ModelViewSet):
    queryset = UserList.objects.all()
    serializer_class = UserListSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    filterset_fields = "__all__"
    search_fields = ['name']
    ordering = ['-id']


    def get_queryset(self):
        return UserList.objects.filter(user_id=self.request.user.id)

    def create(self, request, *args, **kwargs):
        message= ""
        data = None
        status = False

        try:
            name =request.data['name']
        except:
            name = request.body['name']

        userId = request.user.id

        try:
            user = User.objects.get(id=userId)
            userList = UserList.objects.create(user=user,name=name)
            userList.save()
            userListSerializer = UserListSerializer(userList)
            data = userListSerializer.data
            status = True
            message = "The list '"+name+"' created successfully"
        except:
            status = False
            message = "The list is not created"

        return Response({'status': status,'data': data,'message': message})

    def destroy(self, request, *args, **kwargs):
        user_list_id = kwargs['pk']

        status = False
        message = ""

        if UserList.objects.filter(id=user_list_id).count()==0:
            status = False
            message = "List does not exist"
        else:
            try:
                user_list = UserList.objects.get(id=user_list_id)
                if user_list.is_default:
                    status=False
                    message="You can not delete your default list"
                    return Response({'status': status, 'message': message})
                status = True
                message = "List is deleted"
                #If user_list delete scout delete
                # scout_id = ScoutUserList.objects.filter(user_list=user_list.id).first()
                # if scout_id:
                #     scout_id = scout_id.id
                #     Scout.objects.get(id=scout_id).delete()
                user_list.delete()
            except:
                status = False
                message = "Error deleting list"

        return Response({'status': status,'message': message})

    def partial_update(self, request, *args, **kwargs):
        name = None
        user = User.objects.get(id=request.user.id)

        status = False
        data = {}
        message = ""

        try:
            name = request.data['name']
        except:
            name = request.body['name']

        try:
            user_list = UserList(name=name,user=user,leads_count=0)
            user_list.save()
            status = True
            data = UserListSerializer(user_list).data
            message = 'List updated'
        except:
            status = False
            data = {}
            message = 'Error updating list'

        return Response({'status': status,'message': message})

    @action(detail=False, methods=['GET'], url_path='user/(?P<id>[\w-]+)')
    def get_user_list_by_user(self, request, *args, **kwargs):
        userList = UserList.objects.filter(user__id = kwargs['id'])
        userListSerializer = UserListSerializer(userList,many=True)
        return Response(userListSerializer.data)

    @action(detail=False, methods=['POST'], url_path='(?P<pk>[\w-]+)/push')
    def push_list_to_member(self, request, *args, **kwargs):
        status = False
        data = {}
        message = ""
        try:
            memberId = request.data['member']
        except:
            memberId = request.body['member']
        try:
            member = User.objects.get(id=memberId)
            if member.invited_by!=request.user.id :
                status = False
                data = {}
                message = 'Invalid team member'
                return Response({'status': status, 'data': data, 'message': message})
        except:
            status = False
            data = {}
            message = 'Invalid team member'
            return Response({'status': status, 'data': data, 'message': message})
        try:
            userList = UserList.objects.get(id = kwargs['pk'])
            if userList.is_default:
                status = False
                data = {}
                message = 'You can not push your default list'
                return Response({'status': status, 'data': data, 'message': message})
            if userList.user.id != request.user.id:
                status = False
                data = {}
                message = 'Invalid list'
                return Response({'status': status, 'data': data, 'message': message})
        except:
            status = False
            data = {}
            message = 'Invalid list'
            return Response({'status': status, 'data': data, 'message': message})
        try:
            userList.user = member
            userList.save()
            status = True
            data = UserListSerializer(userList).data
            message = 'Successfully pushed list to '+member.first_name+' '+member.last_name
        except:
            status = False
            data = {}
            message = 'Error pushing list to team member'
        return Response({'status': status,'data' : data,'message': message})


    @action(detail=False, methods=['GET'], url_path='filter')
    def get_list_by_members(self, request, *args, **kwargs):
        print(':::::')
        members = [int(x) for x in request.GET.get('members').split(',')]
        print(members)
        user_lists = UserList.objects.filter(user_id__in=members).order_by('-created_at')
        user_list_serializer = UserListSerializer(user_lists,many = True)
        return Response(user_list_serializer.data)


    @action(detail=False, methods=['GET'], url_path='(?P<pk>[\w-]+)/assign-tag/(?P<id>[\w-]+)')
    def assign_tag_to_list(self, request, *args, **kwargs):
        response = {'status': False, 'data': {}, 'message': ''}
        user_list = UserList.objects.get(id=kwargs['pk'])
        user_list_serializer = UserListSerializer(user_list)
        user = User.objects.get(id = request.user.id)
        try:
            tag_id = int(kwargs['id'])
        except:
            tag_id = kwargs['id']
        if user.is_team_admin == False:
            user = User.objects.get(id=user.invited_by)
        try:
            property_tag = PropertyTags.objects.get(id=tag_id)
            if property_tag.user !=None:
                if property_tag.user != user :
                    response['message'] = 'Tag does not exist'
                    return Response(response)
        except:
            response['message'] = 'Tag does not exist'
            return Response(response)
        properties = Property.objects.filter(user_list = user_list)
        properties = properties.filter(~Q(property_tags__contains=[{'id': str(tag_id)}]) | ~Q(property_tags__contains=[{'id': tag_id}]))
        threading.Thread(target=UserListViewSet.tag_update_inside_property, args=(properties,tag_id,)).start()
        response['status'] = True
        response['message'] = 'properties of the list tagging started'
        return Response(response)

    def tag_update_inside_property(properties,tag_id):
        for property in properties:
            try:
                tags = []
                tags = property.property_tags
                tags.append({'id' : tag_id})
                property.property_tags = tags
                property.save()
            except:
                print('Exception occoured')

        print('Tag updated')

    @action(detail=False, methods=['GET'], url_path='(?P<pk>[\w-]+)/property-cluster')
    def properties_cluster_by_list_id(self, request, *args, **kwargs):
        user_list = UserList.objects.get(id=kwargs['pk'])
        property = Property.objects.filter(user_list=user_list)
        clusterViewByListSerializer = ClusterViewByListSerializer(property, many=True)
        return Response(clusterViewByListSerializer.data)

    @action(detail=False, methods=['GET'], url_path='load-list')
    def load_list(self, request, *args, **kwargs):
        load_list_response = []

        user = User.objects.get(id=request.user.id)
        # IF USER IS AN ADMIN
        if user.is_team_admin == True:
            users = User.objects.filter(Q(id=request.user.id) | Q(invited_by=request.user.id))
            # user_list = UserList.objects.filter(user__in=users).order_by('-created_at')
            for u in users:
                load_list_json = {}
                load_list_json["member_id"] = u.id
                load_list_json["list"]= UserListSerializer(UserList.objects.filter(user=u).order_by('-created_at'), many=True).data
                load_list_response.append(load_list_json)
        #IF USER IS A MEMBER
        else:
            load_list_json = {}
            load_list_json["member_id"] = user.id
            load_list_json["list"] = UserListSerializer(UserList.objects.filter(user=user).order_by('-created_at'),
                                                          many=True).data
            load_list_response.append(load_list_json)
        return JsonResponse(load_list_response,safe=False)

    @action(detail=False, methods=['GET'], url_path='(?P<pk>[\w-]+)/load-list/properties')
    def get_properties_in_load_list(self, request, *args, **kwargs):
        given_lat = request.GET.get('latitude')
        given_lng = request.GET.get('longitude')
        print(type(given_lat))
        print(given_lng)
        user_list = UserList.objects.get(id=kwargs['pk'])
        properties = Property.objects.filter(user_list=user_list)
        properties_filtered_id = []
        for property in properties:
            if given_lat and given_lng:
                given_lat = float(given_lat)
                given_lng = float(given_lng)
                # if self.check_if_within_area(property.longitude, property.latitude, given_lng, given_lat, 0.124274):
                if self.check_if_within_area(property.longitude, property.latitude, given_lng, given_lat, 3.21869):
                    properties_filtered_id.append(property.id)
            else:
                properties_filtered_id.append(property.id)
        properties_filtered = Property.objects.filter(id__in=properties_filtered_id)

        print(properties_filtered)

        load_list_property_serializer = LoadListPropertySerializer(properties_filtered, many=True)
        return Response(load_list_property_serializer.data)

    def check_if_within_area(self,lon1, lat1, lon2, lat2, distance):
        """
        Calculate the great circle distance between two points 
        on the earth (specified in decimal degrees)
        """
        # convert decimal degrees to radians
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        print(distance)

        # haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371 # Radius of earth in kilometers. Use 3956 for miles
        if c * r<=distance:
            return True
        else:
            return False

    @action(detail=False, methods=['GET'], url_path='load-list/user/(?P<id>[\w-]+)')
    def load_list_by_user(self, request, *args, **kwargs):
        requested_user = User.objects.get(id=request.user.id)
        user = User.objects.get(id=kwargs['id'])
        user_list = UserList.objects.filter(user=user).order_by('-created_at')
        user_list_serializer = UserListSerializer(user_list, many=True).data
        return JsonResponse(user_list_serializer, safe=False)