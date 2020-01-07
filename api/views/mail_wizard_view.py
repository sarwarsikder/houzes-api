from rest_framework import viewsets, status
from rest_framework.decorators import action
import requests
from api.serializers import *
from api.models import *
from rest_framework.response import Response




class MailWizardInfoViewSet(viewsets.ModelViewSet):
    queryset = MailWizardInfo.objects.all()
    serializer_class = MailWizardInfoSerializer

    @action(detail=False, url_path='property/(?P<id>[\w-]+)')
    def send_mail_to_property_owner(self, request, *args, **kwargs):
        property = Property.objects.get(id=kwargs['id'])
        url = 'http://172.18.1.11:8002/mailer-service/send-mailer-data/'
        headers = {
            'Content-Type': 'application/json',
        }
        PARAMS = {
            {
                "user_id": 26,
                "list_id": 56,
                "response_text": "hi....",
                "user_info": {
                    "firstName": "hhhh",
                    "lastName": "kkkkk",
                    "email": "zahidul@workspaceit.com",
                    "proofEmail": "",
                    "compName": "",
                    "website": "",
                    "telephoneNo": ""
                },
                "letter_info": {
                    "type": "Letter",
                    "size_id": "",
                    "size_name": "",
                    "item_id": "527",
                    "item_name": "TAPLT1",
                    "paper_id": "7",
                    "paper_name": "Yellow",
                    "ink_id": "11",
                    "ink_name": "Color",
                    "envelope_id": "21",
                    "envelope_name": "#10 ENVELOPE - WHITE - $.04",
                    "postage_id": "5",
                    "postage_name": "Presorted First Class Stamp w/ Cancellation - $ 0.424 Each 500 or More",
                    "date": "30 jan 2019"
                },
                "is_imported": False,
                "rec_data": [
                    {
                        "full_name": "test name",
                        "mailing_address1": "mailing address",
                        "mailing_city": " Anchorage",
                        "mailing_state": "Alaska",
                        "mailing_zip": "99501",
                        "prop_address1": "Proof address",
                        "prop_city": "Anchorage",
                        "prop_state": "Alaska",
                        "prop_zip": "99501"
                    },
                    {
                        "full_name": "test name",
                        "mailing_address1": "mailing address",
                        "mailing_city": " Anchorage ",
                        "mailing_state": "Alaska ",
                        "mailing_zip": "99501",
                        "prop_address1": "Proof address",
                        "prop_city": "Anchorage ",
                        "prop_state": "Alaska ",
                        "prop_zip": "99501"
                    }
                ]
            }
        }
        try:
            r = requests.post(url=url, data=PARAMS, headers=headers)
            objectResponse = r.json()
            print(objectResponse)
        except:
            print('ex')
            status = False
            message = 'Get neighborhood micro service error'
        return Response({'status' : True})