from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.utils import json

from api.serializers import *
from api.models import *



class AssignMemberToListViewSet(viewsets.ModelViewSet):
    queryset = AssignMemberToList.objects.all()
    serializer_class = AssignMemberToListSerializer
    ordering = ['-id']

    def list(self, request, *args, **kwargs):
        queryset = AssignMemberToList.objects.all()
        serializer = AssignMemberToListSerializer(queryset, many=True)

        return Response({'status': status.is_success(Response.status_code),'data': serializer.data,'message': 'List of member assigned to list'})

    def create(self, request, *args, **kwargs):
        try:
            list_id = request.data['list']
            member_id = request.data['member']
            print('try works')

        except:
            body_unicode = request.body.decode('utf-8')
            body = json.loads(body_unicode)

            list_id = body['list']
            member_id = body['member']
            print('catch works')

        userList = UserList.objects.get(id=list_id)
        member = User.objects.get(id=member_id)

        print(userList)
        print(member)

        message= ""
        data = None
        status = False

        if (AssignMemberToList.objects.filter(list=userList,member=member).count())>0 :
            message = "This member is already assigned to this list"
        elif UserList.objects.filter(id=list_id,user__id=request.user.id).count()==0 :
            message = "You can assign your member only to your list"
        elif User.objects.filter(id=member_id,invited_by=request.user.id).count()==0 :
            message = "You can only assign your team member in your list"
        else:
            message = str(User.objects.get(id=member_id).first_name)+" "+str(User.objects.get(id=member_id).last_name)+" is assigned to "+str(UserList.objects.get(id=list_id).name)
            assignMemberToList = AssignMemberToList(list=userList,member=member)
            assignMemberToList.save()
            assignMemberToListSerializer = AssignMemberToListSerializer(assignMemberToList)
            data = assignMemberToListSerializer.data
            status = True
        return Response({'status': status,'data': data,'message': message})

    def destroy(self, request, *args, **kwargs):
        data = None
        message =""
        status = False

        if AssignMemberToList.objects.filter(id=int(kwargs['pk'])).count()==0:
            message = "The entry you want to delete does not exist"
            print(message)
        if AssignMemberToList.objects.filter(id=int(kwargs['pk'])).count()>0:
            list = AssignMemberToList.objects.get(id=int(kwargs['pk'])).list
            list_id = list.id
            user = User.objects.get(id=request.user.id)
            userList = UserList.objects.filter(id=int(list_id),user=user)
            if userList.count()<0 :
                message = "You can only delete the member from your own list"
                print(message)
            else:
                AssignMemberToList.objects.filter(id=int(kwargs['pk'])).delete()
                message = "Member is deleted from the list"
                print(message)
                status = True

        return Response({'status': status   ,'data': data,'message': message})
