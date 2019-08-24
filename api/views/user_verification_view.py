from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from api.serializers import *
from api.models import *

class UserVerificationsViewSet(viewsets.ModelViewSet):
    queryset = UserVerifications.objects.all()
    serializer_class = UserVerificationsSerializer

    def create(self, request, *args, **kwargs):
        user_id = 4
        user = User.objects.get(id=user_id)

        code = request.POST.get('code')
        is_used = request.POST.get('is_used')
        verification_type = request.POST.get('verification_type')

        if is_used == 'True':
            is_used = True
        else:
            is_used = False

        userVerifications = UserVerifications(user=user, code=code, is_used=is_used,
                                              verification_type=verification_type)
        userVerifications.save()

        userVerificationsSerializer = UserVerificationsSerializer(userVerifications)
        return Response(userVerificationsSerializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False)
    def userVerification_by_userId(self, request, *args, **kwargs):
        user_id = 4
        user = User.objects.get(id=user_id)
        userVerifications = UserVerifications.objects.filter(user=user)
        print(userVerifications)
        userVerificationsSerializer = UserVerificationsSerializer(userVerifications, many=True)
        return Response(userVerificationsSerializer.data)

