from rest_framework import viewsets
from api.serializers import MailWizardUserInfoSerializer
from api.models import MailWizardUserInfo


class MailWizardUserInfoViewSet(viewsets.ModelViewSet):
    queryset = MailWizardUserInfo.objects.all()
    serializer_class = MailWizardUserInfoSerializer
