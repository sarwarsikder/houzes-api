from django.http import JsonResponse
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from oauth2_provider.models import AccessToken
from api.serializers import *
from api.models import *


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)

    @action(detail=False, methods=['GET'], url_path='get-current-userinfo')
    def get_current_userinfo(self, request):
        access_token = request.META["HTTP_AUTHORIZATION"][7:].split("-")[0]
        access_token_object = AccessToken.objects.get(token=access_token)
        user = access_token_object.user
        serializer = UserSerializer(user)
        return JsonResponse(serializer.data, safe=False)


class UserLocationViewSet(viewsets.ModelViewSet):
    queryset = UserLocation.objects.all()
    serializer_class = UserLocationSerializer


class UserVerificationsViewSet(viewsets.ModelViewSet):
    queryset = UserVerifications.objects.all()
    serializer_class = UserVerificationsSerializer


class PropertyTagsViewSet(viewsets.ModelViewSet):
    queryset = PropertyTags.objects.all()
    serializer_class = PropertyTagsSerializer


class PropertyNotesViewSet(viewsets.ModelViewSet):
    queryset = PropertyNotes.objects.all()
    serializer_class = PropertyNotesSerializer


class PropertyPhotosViewSet(viewsets.ModelViewSet):
    queryset = PropertyPhotos.objects.all()
    serializer_class = PropertyPhotosSerializer


class UserListViewSet(viewsets.ModelViewSet):
    queryset = UserList.objects.all()
    serializer_class = UserListSerializer


class ListPropertiesViewSet(viewsets.ModelViewSet):
    queryset = ListProperties.objects.all()
    serializer_class = ListPropertiesSerializer


class UserDriverViewSet(viewsets.ModelViewSet):
    queryset = UserDriver.objects.all()
    serializer_class = UserDriverSerializer


class UserOwnershipUsageViewSet(viewsets.ModelViewSet):
    queryset = UserOwnershipUsage.objects.all()
    serializer_class = UserOwnershipUsageSerializer


class VisitedPropertiesViewSet(viewsets.ModelViewSet):
    queryset = VisitedProperties.objects.all()
    serializer_class = VisitedPropertiesSerializer


class UserSocketsViewSet(viewsets.ModelViewSet):
    queryset = UserSockets.objects.all()
    serializer_class = UserSocketsSerializer
