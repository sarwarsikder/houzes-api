from rest_framework import viewsets, status
from rest_framework.decorators import action
import requests
from api.serializers import *
from api.models import *
from rest_framework.response import Response


class MailWizardInfoViewSet(viewsets.ModelViewSet):
    queryset = MailWizardInfo.objects.all()
    serializer_class = MailWizardInfoSerializer

    @action(detail=False, methods=['POST'], url_path='property/(?P<id>[\w-]+)')
    def send_mail_to_property_owner(self, request, *args, **kwargs):
        status = False
        response = {'status': False, 'message': ''}
        property = Property.objects.get(id=kwargs['id'])
        user = User.objects.get(id=request.user.id)

        # print(property.__dict__)
        # print(len(property.owner_info))

        if len(property.owner_info) == 0:
            response['status'] = False
            response['message'] = 'Owner info is empty. Please apply Fetch Ownership to get Owner info.'
            return Response(response)

        full_name = property.owner_info[0]['full_name']
        full_address = property.owner_info[0]['full_address']
        mailing_city = property.owner_info[0]['formatted_address']['city']
        mailing_state = property.owner_info[0]['formatted_address']['state']
        mailing_zip = property.owner_info[0]['formatted_address']['zip_code']

        text_body = request.data['mail_text']
        item_id = request.data['tem_item_id']
        subs_id = request.data['subs_id']

        prop_address1 = [property.street, property.city, property.state, property.zip]
        separator = ', '

        url = 'http://13.59.67.162:8111/mailer-service/send-mailer-data/'
        headers = {
            'Content-Type': 'application/json',
        }
        PARAMS = {
            "user_id": user.id,
            "list_id": property.id,
            "response_text": text_body.strip(),
            "user_info": {
                "firstName": user.first_name,
                "lastName": user.last_name,
                "email": user.email,
                "proofEmail": "",
                "compName": "",
                "website": "",
                "telephoneNo": ""
            },
            "letter_info": {
                "type": "Letter",
                "item_id": item_id,
                "paper_id": "7",
                "ink_id": "11",
                "envelope_id": "21",
                "postage_id": "5"
            },
            "is_imported": False,
            "rec_data": [
                {
                    "full_name": full_name.strip(),
                    "mailing_address1": full_address.strip(),
                    "mailing_city": mailing_city.strip(),
                    "mailing_state": mailing_state.strip(),
                    "mailing_zip": mailing_zip.strip(),
                    "prop_address1": separator.join(prop_address1),
                    "prop_city": property.city,
                    "prop_state": property.state,
                    "prop_zip": property.zip
                },
            ]
        }

        try:
            manager = user
            if not manager.is_admin:
                manager = User.objects.get(id=manager.invited_by)
            upgrade_profile = UpgradeProfile.objects.filter(user=manager).first()
            required_coin = 0.0
            required_coin = required_coin + float(PaymentPlan.objects.filter(payment_plan_name='mailer-wizard',
                                                                                 plan=upgrade_profile.plan).first().payment_plan_coin)
            if upgrade_profile.coin < required_coin:
                response['status'] = False
                response['message'] = 'Mail wizard sending unsuccessful due to insufficient balance'
                return Response(response)
            upgrade_profile.coin = float(upgrade_profile.coin) - required_coin
            upgrade_profile.save()
            r = requests.post(url=url, json=PARAMS, headers=headers)
            if r.status_code == 200:
                mailWizardSubsType = MailWizardSubsType.objects.filter(id=subs_id).first()

                mailWizardInfo = MailWizardInfo(property=property, sender=user, subs_type=mailWizardSubsType,
                                                item_id=item_id)
                mailWizardInfo.save()

                # if mailWizardSubsType:
                #     mailWizardInfo = MailWizardInfo(property=property, sender=user, subs_type=mailWizardSubsType,
                #                                     item_id=item_id)
                #     mailWizardInfo.save()
                # else:
                #     mailWizardInfo = MailWizardInfo(property=property, sender=user, subs_type=None,
                #                                     item_id=item_id)
                #     mailWizardInfo.save()

                response['status'] = True
                response['message'] = 'Mail wizard sent successfully'
            else:
                response['status'] = False
                response['message'] = 'Mail wizard sending unsuccessful'
        except Exception as e:
            print('ex' + str(e))
            response['status'] = False
            response['message'] = 'Mail wizard sending unsuccessful'
        return Response(response)

    @action(detail=False, url_path='all')
    def get_mail_wizard(self, request, *args, **kwargs):
        response = {'status': False, 'message': ''}
        url = 'http://13.59.67.162:8111/mailer-service/fetch-templates/'
        headers = {
            'Content-Type': 'application/json',
        }

        PARAMS = {
        }

        try:
            res = requests.get(url=url)
            data = res.json()
            response['status'] = True
            response['data'] = data
            response['message'] = 'Mail wizard received successfully'
        except Exception as e:
            print('ex' + str(e))
            response['status'] = False
            response['message'] = 'Mail wizard received unsuccessful'
        return Response(response)
