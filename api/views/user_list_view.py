from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets,filters
from rest_framework.decorators import action
from rest_framework.response import Response

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
                UserList.objects.get(id=user_list_id).delete()
                status = True
                message = "List is deleted"
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
