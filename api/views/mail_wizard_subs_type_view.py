from rest_framework import viewsets, status
from rest_framework.decorators import action
import requests
from api.serializers import *
from api.models import *
from rest_framework.response import Response


class MailWizardSubsTypeViewSet(viewsets.ModelViewSet):
    queryset = MailWizardSubsType.objects.all()
    serializer_class = MailWizardSubsTypeSerializer