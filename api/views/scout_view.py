from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters, pagination
from oauth2_provider.models import AccessToken
from rest_framework.decorators import action
from rest_framework.response import Response

from api.serializers import *
from api.models import *

from django.http import JsonResponse

from houzes_api.settings import WEB_APP_URL


class CustomPagination(pagination.PageNumberPagination):
    def get_paginated_response(self, data):
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.page.paginator.count,
            'results': data,
        })

class ScoutViewSet(viewsets.ModelViewSet):
    queryset = Scout.objects.all()
    serializer_class = ScoutSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    ordering = ['-id']
    def get_queryset(self):
        return Scout.objects.filter(manager_id=self.request.user.id)

    def generate_shortuuid(self):
        shortuuid.set_alphabet("abcdefghijklmnopqrstuvwxyz0123456789")
        gUid = str(shortuuid.random(length=16))
        return gUid

    def create(self, request, *args, **kwargs):
        first_name = None
        last_name = None
        try:
            if 'first_name' in request.data:
                first_name = request.data['first_name']
            if 'last_name' in request.data:
                last_name = request.data['last_name']
            if 'email' in request.data:
                email = request.data['email']
            if 'phone_number' in request.data :
                phone_number = request.data['phone_number']
        except:
            if 'first_name' in request.body:
                first_name = request.body['first_name']
            if 'last_name' in request.body:
                last_name = request.body['last_name']
            if 'email' in request.body:
                email = request.body['email']
            if 'phone_number' in request.body :
                phone_number = request.body['phone_number']

        if first_name == None:
            status = False
            data = None
            message = "First name required"
            return Response({'status': status, 'data': data, 'message': message})
        if last_name == None:
            status = False
            data = None
            message = "Last name required"
            return Response({'status': status, 'data': data, 'message': message})

        name = "List of "+first_name + ' ' + last_name

        access_token = request.META["HTTP_AUTHORIZATION"][7:]
        access_token_object = AccessToken.objects.get(token=access_token)
        user = access_token_object.user

        user_list = UserList(name=name, user=user, leads_count=0)
        user_list.save()

        url = WEB_APP_URL+"/scout-form/"+str(user_list.id)+"/"+generate_shortuuid()
        manager = User.objects.get(id=request.user.id)

        try:
            scout = Scout(first_name=first_name,last_name=last_name,url=url,manager_id=manager, email=email, phone_number=phone_number)
            scout.save()
            scoutSerializer = ScoutSerializer(scout)
            scoutUserList = ScoutUserList(scout=scout, user_list=user_list)
            scoutUserList.save()
            status = True
            data = scoutSerializer.data
            message = "New scout/s created"
        except:
            status = False
            data = None
            message = "Error creating scout"

        return Response({'status': status, 'data': data, 'message': message})

    def destroy(self, request, *args, **kwargs):
        scout_id = kwargs['pk']
        status = False
        message=""
        if Scout.objects.filter(id=scout_id).count()==0:
            status = False
            message = "Scout not found"
        else:
            try:
                Scout.objects.get(id=scout_id).delete()
                status = True
                message = "Successfully deleted"
            except:
                status = False
                message = "Error deleting scout"

        return Response({'status': status, 'message': message})


    @action(detail=False, methods=['GET'], url_path='(?P<pk>[\w-]+)/properties')
    def get_user_list_by_user(self, request, *args, **kwargs):
        scout = Scout.objects.get(id = kwargs['pk'])
        scoutUserList = ScoutUserList.objects.filter(scout=scout)
        if scoutUserList.count():
            userList = scoutUserList[0].user_list
            property = Property.objects.filter(user_list=userList)
        else:
            property = Property.objects.none()
        page_size = request.GET.get('limit')
        paginator = CustomPagination()
        if page_size:
            paginator.page_size = page_size
        else:
            paginator.page_size = 10

        result_page = paginator.paginate_queryset(property, request)

        serializer = PropertySerializer(result_page, many=True)
        return paginator.get_paginated_response(data=serializer.data)

    @action(detail=False, methods=['GET'], url_path='member/(?P<id>[\w-]+)')
    def get_scout_by_member(self, request, *args, **kwargs):
        user = User.objects.get(id=kwargs['id'])
        if user.invited_by == request.user.id or user.id == request.user.id:
            scout = Scout.objects.filter(manager_id=user.id)
        else :
            scout = Scout.objects.none()
        scoutSerializer = ScoutSerializer(scout,many=True)
        return Response(scoutSerializer.data)
