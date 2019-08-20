from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from decimal import Decimal

from api.serializers import *
from api.models import *

class UserDriverViewSet(viewsets.ModelViewSet):
    queryset = UserDriver.objects.all()
    serializer_class = UserDriverSerializer

    def create(self, request, *args, **kwargs):
        user_id = 4
        user = User.objects.get(id=user_id)
        list = request.POST.get('list')
        distance = request.POST.get('distance')
        travel_shape = request.POST.get('travel_shape')

        userList = UserList.objects.get(id=int(list))

        userDriver = UserDriver(list=userList, user=user, distance=Decimal(distance), travel_shape=travel_shape)
        userDriver.save()

        userDriverSerializer = UserDriverSerializer(userDriver)
        return Response(userDriverSerializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False)
    def userDriver_by_userId(self, request, *args, **kwargs):
        user_id = 4
        user = User.objects.get(id=user_id)
        userDriver = UserDriver.objects.filter(user=user)
        print(userDriver)
        userDriverSerializer = UserDriverSerializer(userDriver, many=True)
        return Response(userDriverSerializer.data)

