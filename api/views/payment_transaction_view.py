from rest_framework import viewsets
from rest_framework.response import Response

from api.models import *
from api.serializers import *

class PaymentTransactionViewSet(viewsets.ModelViewSet):
    queryset = PaymentTransaction.objects.all()
    serializer_class = PaymentTransactionSerializer

    def list(self, request, *args, **kwargs):
        user = User.objects.get(id = request.user.id)
        if user.is_team_admin == False:
            return Response({})
        members = User.objects.filter(invited_by=user.id)
        members |= User.objects.filter(id = request.user.id)
        print(type(members))
        payment_transactions = PaymentTransaction.objects.filter(created_by__in = members)
        payment_transactions_serializer = PaymentTransactionSerializer(payment_transactions, many=True)
        return Response(payment_transactions_serializer.data)