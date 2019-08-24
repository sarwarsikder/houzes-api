from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from api.serializers import *
from api.models import *

class UserOwnershipUsageViewSet(viewsets.ModelViewSet):
    queryset = UserOwnershipUsage.objects.all()
    serializer_class = UserOwnershipUsageSerializer

    def create(self, request, *args, **kwargs):
        user_id = 4
        user = User.objects.get(id=user_id)

        property_id = request.POST.get('property')

        property = Property.objects.get(id=int(property_id))

        userOwnershipUsage = UserOwnershipUsage(user=user, property=property)
        userOwnershipUsage.save()

        userOwnershipUsageSerializer = UserOwnershipUsageSerializer(userOwnershipUsage)
        return Response(userOwnershipUsageSerializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False)
    def userOwnershipUsage_by_userId(self, request, *args, **kwargs):
        user_id = 4
        user = User.objects.get(id=user_id)
        userOwnershipUsage = UserOwnershipUsage.objects.filter(user=user)
        print(userOwnershipUsage)
        userOwnershipUsagerSerializer = UserOwnershipUsageSerializer(userOwnershipUsage, many=True)
        return Response(userOwnershipUsagerSerializer.data)
