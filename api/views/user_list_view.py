from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets,filters
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

