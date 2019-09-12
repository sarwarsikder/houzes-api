from rest_framework import viewsets
from api.serializers import *
from api.models import *



class UserListViewSet(viewsets.ModelViewSet):
    queryset = UserList.objects.all()
    serializer_class = UserListSerializer
    ordering = ['-id']

    def get_queryset(self):
        return UserList.objects.filter(user_id=self.request.user.id)

    def create(self, request, *args, **kwargs):
        if '_mutable' in request.data:
            if not request.data._mutable:
                state = request.data._mutable
                request.data._mutable = True

        request.data['user'] = request.user.id

        if '_mutable' in request.data:
            if not request.data._mutable:
                request.data._mutable = state

        return super().create(request, *args, **kwargs)

