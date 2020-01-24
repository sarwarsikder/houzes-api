from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets,filters
from rest_framework.decorators import action
from rest_framework.response import Response
import threading

from api.serializers import *
from api.models import *



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
                status = True
                message = "List is deleted"
                scout_id = ScoutUserList.objects.filter(user_list=user_list.id).first()
                if scout_id:
                    scout_id = scout_id.id
                    Scout.objects.get(id=scout_id).delete()
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
        user_lists = UserList.objects.filter(user_id__in=members)
        user_list_serializer = UserListSerializer(user_lists,many = True)
        return Response(user_list_serializer.data)


    @action(detail=False, methods=['GET'], url_path='(?P<pk>[\w-]+)/assign-tag/(?P<id>[\w-]+)')
    def assign_tag_to_list(self, request, *args, **kwargs):
        response = {'status': False, 'data': {}, 'message': ''}
        user_list = UserList.objects.get(id=kwargs['pk'])
        user_list_serializer = UserListSerializer(user_list)
        user = User.objects.get(id = request.user.id)
        tag_id = kwargs['id']
        if user.is_admin == False:
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
