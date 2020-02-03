import traceback

from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.serializers import MailWizardUserInfoSerializer
from api.models import MailWizardUserInfo


class MailWizardUserInfoViewSet(viewsets.ModelViewSet):
    queryset = MailWizardUserInfo.objects.all()
    serializer_class = MailWizardUserInfoSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    filterset_fields = ["user"]

    @action(detail=False, methods=['get'], url_path='get')
    def get_user_info(self, request):
        response = {'status': False, 'data': {}, 'message': ''}
        try:
            response['status'] = True
            response['data'] = MailWizardUserInfoSerializer(MailWizardUserInfo.objects.filter
                                                            (user_id=request.user.id).first()).data
        except MailWizardUserInfo.DoesNotExist:
            traceback.print_exc()
        return Response(response)



