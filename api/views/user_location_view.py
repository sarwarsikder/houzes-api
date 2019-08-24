
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from decimal import Decimal

from api.serializers import *
from api.models import *



class UserLocationViewSet(viewsets.ModelViewSet):
    queryset = UserLocation.objects.all()
    serializer_class = UserLocationSerializer

    def create(self, request, *args, **kwargs):
        user_id = 4
        user = User.objects.get(id=user_id)

        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        is_driving = request.POST.get('is_driving')
        angle = request.POST.get('angle')

        if is_driving == 'True':
            is_driving = True
        else:
            is_driving = False
        userLocation = UserLocation(user=user, latitude=Decimal(latitude), longitude=Decimal(longitude),
                                    is_driving=is_driving, angle=Decimal(angle))
        userLocation.save()

        userLocationSerializer = UserLocationSerializer(userLocation)
        return Response(userLocationSerializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False)
    def userLocation_by_userId(self, request, *args, **kwargs):
        user_id = 4
        user = User.objects.get(id=user_id)
        userLocation = UserLocation.objects.filter(user=user)
        print(userLocation)
        userLocationSerializer = UserLocationSerializer(userLocation, many=True)
        return Response(userLocationSerializer.data)

