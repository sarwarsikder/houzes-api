from rest_framework import viewsets

from api.serializers import *
from api.models import *

from django.http import JsonResponse

class ScoutViewSet(viewsets.ModelViewSet):
    queryset = Scout.objects.all()
    serializer_class = ScoutSerializer

    def generate_shortuuid(self):
        shortuuid.set_alphabet("abcdefghijklmnopqrstuvwxyz0123456789")
        gUid = str(shortuuid.random(length=16))
        return gUid

    def create(self, request, *args, **kwargs):
        url = generate_shortuuid()
        request.data['url'] = "https://www.sample.com/"+url
        return super().create(request, *args, **kwargs)
