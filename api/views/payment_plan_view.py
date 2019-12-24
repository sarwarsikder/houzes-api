from rest_framework import viewsets
from api.models import *
from api.serializers import *

class PaymentPlanViewSet(viewsets.ModelViewSet):
    queryset = PaymentPlan.objects.all()
    serializer_class = PaymentPlanSerializer