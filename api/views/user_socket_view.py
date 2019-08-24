from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from api.serializers import *
from api.models import *

class UserSocketsViewSet(viewsets.ModelViewSet):
    queryset = UserSockets.objects.all()
    serializer_class = UserSocketsSerializer

    def create(self, request, *args, **kwargs):
        user_id = 4
        user = User.objects.get(id=user_id)

        socket_id = request.POST.get('socket_id')
        is_connected = request.POST.get('is_connected')

        if is_connected == 'True':
            is_connected = True
        else:
            is_connected = False

        userSockets = UserSockets(user=user, socket_id=socket_id, is_connected=is_connected)
        userSockets.save()

        userSocketsSerializer = UserSocketsSerializer(userSockets)
        return Response(userSocketsSerializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False)
    def userSockets_by_userId(self, request, *args, **kwargs):
        user_id = 4
        user = User.objects.get(id=user_id)
        userSockets = UserSockets.objects.filter(user=user)
        print(userSockets)
        userSocketsSerializer = UserSocketsSerializer(userSockets, many=True)
        return Response(userSocketsSerializer.data)
