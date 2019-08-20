from rest_framework import viewsets
from api.serializers import *
from api.models import *



class UserListViewSet(viewsets.ModelViewSet):
    queryset = UserList.objects.all()
    serializer_class = UserListSerializer

    def get_queryset(self):
        return UserList.objects.filter(user_id=self.request.user.id)

    def create(self, request, *args, **kwargs):
        request.data['user'] = request.user.id
        return super().create(request, *args, **kwargs)

