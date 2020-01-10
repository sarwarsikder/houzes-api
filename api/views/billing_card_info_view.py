from rest_framework import viewsets, status
from rest_framework.decorators import action
import requests
from api.serializers import *
from api.models import *
from rest_framework.response import Response


class BillingCardInfoViewSet(viewsets.ModelViewSet):
    queryset = BillingCardInfo.objects.all()
    serializer_class = BillingCardInfoSerializer

    @action(detail=False, methods=['POST'], url_path='save')
    def send_mail_to_property_owner(self, request, *args, **kwargs):
        status = False
        response = {'status': False, 'message': ''}

        user = User.objects.get(id=request.user.id)

        print(user)
        print("")

        card_name = request.data['card_name_post_data']
        card_number = request.data['card_number_post_data']
        card_code = request.data['card_code_post_data']
        exp_date = request.data['exp_date_post_data']
        is_save = request.data['is_save_post_data']

        try:
            billingCardInfoObj = BillingCardInfo(user=user, card_name=card_name.strip(),
                                                 card_number=card_number.strip(),
                                                 card_code=card_code.strip(), exp_date=exp_date.strip(),
                                                 is_save=is_save)
            billingCardInfoObj.save()

            response['status'] = True
            response['message'] = 'Billing card added successfully'

        except Exception as e:
            print('ex' + str(e))
            response['status'] = False
            response['message'] = 'Billing card added unsuccessful'
        return Response(response)

    @action(detail=False, url_path='all')
    def get_(self, request, *args, **kwargs):
        response = {'status': False, 'data' : [], 'message': ''}

        try:
            billingCard = BillingCardInfo.objects.all().filter(user_id=request.user.id)
            print(len(billingCard))
            if len(billingCard) == 0:
                response['status'] = True
                response['message'] = 'Billing Card Info Empty'
                return Response(response)

            data = BillingCardInfoSerializer(billingCard, many=True).data

            response['status'] = True
            response['data'] = data
            response['message'] = 'Billing Card Info received successful'

        except Exception as e:
            print('ex' + str(e))
            response['status'] = False
            response['message'] = 'Billing Card Info received unsuccessful'
        return Response(response)

    def list(self, request, *args, **kwargs):
        billing_card_info = BillingCardInfo.objects.filter(user__id = request.user.id)
        billing_card_info_serializer = BillingCardInfoSerializer(billing_card_info, many=True)
        return Response(billing_card_info_serializer.data)
