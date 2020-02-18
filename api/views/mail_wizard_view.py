from rest_framework import viewsets, status
from rest_framework.decorators import action
import requests
from api.serializers import *
from api.models import *
from rest_framework.response import Response
import datetime
from houzes_api import settings
import traceback


class MailWizardInfoViewSet(viewsets.ModelViewSet):
    queryset = MailWizardInfo.objects.all()
    serializer_class = MailWizardInfoSerializer

    @action(detail=False, methods=['POST'], url_path='property/(?P<id>[\w-]+)')
    def send_mail_to_property_owner(self, request, *args, **kwargs):
        response = {'status': False, 'data': {}, 'message': ''}
        property = Property.objects.get(id=kwargs['id'])
        user = User.objects.get(id=request.user.id)

        # print(property.__dict__)
        # print(len(property.owner_info))

        if len(property.owner_info) == 0:
            response['status'] = False
            response['message'] = 'Sending unsuccessful! Ownership info is required.'
            return Response(response)

        full_name = property.owner_info[0]['full_name']
        full_address = property.owner_info[0]['full_address']
        mailing_city = property.owner_info[0]['formatted_address']['city']
        mailing_state = property.owner_info[0]['formatted_address']['state']
        mailing_zip = property.owner_info[0]['formatted_address']['zip_code']

        user_info = request.data['user_info']

        item_id = request.data['tem_item_id']
        subs_id = request.data['subs_id']
        mail_count_target = request.data['mail_count']
        return self.hit_mailer_wizard(user, property, full_name, full_address, mailing_city, mailing_state, mailing_zip,
                                      user_info, item_id, subs_id, mail_count_target, False)

    @action(detail=False, url_path='all')
    def get_mail_wizard(self, request, *args, **kwargs):
        response = {'status': False, 'message': ''}
        url = settings.MAILER_WIZARD_MICRO_SERVICE_DOMAIN+'mailer-service/fetch-templates/'
        print(url)
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
            response['message'] = 'Mail templates received successfully'
        except Exception as e:
            print('ex' + str(e))
            response['status'] = False
            response['message'] = 'Empty mail template'
        return Response(response)

    @action(detail=False, methods=['POST'], url_path='neighbor/(?P<id>[\w-]+)')
    def send_mail_to_neighbor_owner(self, request, *args, **kwargs):
        response = {'status': False, 'data' : {},'message': ''}
        get_neighborhood = GetNeighborhood.objects.get(id=kwargs['id'])
        user = User.objects.get(id=request.user.id)

        if get_neighborhood.ownership_info == {}:
            response['status'] = False
            response['message'] = 'Owner info is empty for this neighbor. Please apply Fetch Ownership to get Owner info.'
            return Response(response)

        full_name = get_neighborhood.ownership_info['owner_info']['full_name']
        full_address = get_neighborhood.ownership_info['owner_info']['full_address']
        mailing_city = get_neighborhood.ownership_info['owner_info']['formatted_address']['city']
        mailing_state = get_neighborhood.ownership_info['owner_info']['formatted_address']['state']
        mailing_zip = get_neighborhood.ownership_info['owner_info']['formatted_address']['zip_code']

        user_info = request.data['user_info']

        item_id = request.data['tem_item_id']
        subs_id = request.data['subs_id']
        mail_count_target = request.data['mail_count']

        return self.hit_mailer_wizard(user, get_neighborhood, full_name, full_address, mailing_city, mailing_state, mailing_zip,
                                      user_info, item_id, subs_id, mail_count_target, True)
        # prop_address1 = [get_neighborhood.street, get_neighborhood.city, get_neighborhood.state, get_neighborhood.zip]
        # separator = ', '
        #
        # url = 'http://13.59.67.162:8111/mailer-service/send-mailer-data/'
        # headers = {
        #     'Content-Type': 'application/json',
        # }
        # PARAMS = {
        #     "user_id": user.id,
        #     "list_id": get_neighborhood.id,
        #     "response_text": text_body.strip(),
        #     "user_info": {
        #         "firstName": user.first_name,
        #         "lastName": user.last_name,
        #         "email": user.email,
        #         "proofEmail": "",
        #         "compName": "",
        #         "website": "",
        #         "telephoneNo": ""
        #     },
        #     "letter_info": {
        #         "type": "Letter",
        #         "item_id": item_id,
        #         "paper_id": "7",
        #         "ink_id": "11",
        #         "envelope_id": "21",
        #         "postage_id": "5"
        #     },
        #     "is_imported": False,
        #     "rec_data": [
        #         {
        #             "full_name": full_name.strip(),
        #             "mailing_address1": full_address.strip(),
        #             "mailing_city": mailing_city.strip(),
        #             "mailing_state": mailing_state.strip(),
        #             "mailing_zip": mailing_zip.strip(),
        #             "prop_address1": separator.join(prop_address1),
        #             "prop_city": get_neighborhood.city,
        #             "prop_state": get_neighborhood.state,
        #             "prop_zip": get_neighborhood.zip
        #         },
        #     ]
        # }
        #
        # try:
        #     manager = user
        #     if not manager.is_admin:
        #         manager = User.objects.get(id=manager.invited_by)
        #     upgrade_profile = UpgradeProfile.objects.filter(user=manager).first()
        #     required_coin = 0.0
        #     required_coin = required_coin + float(PaymentPlan.objects.filter(payment_plan_name='mailer-wizard',
        #                                                                      plan=upgrade_profile.plan).first().payment_plan_coin)*mail_count_target
        #     if upgrade_profile.coin < required_coin:
        #         response['status'] = False
        #         response['data'] = {
        #             'payment': False,
        #             'upgrade_info': UserSerializer(manager).data['upgrade_info']
        #         }
        #         response['message'] = 'Mail wizard sending unsuccessful due to insufficient balance'
        #         return Response(response)
        #     upgrade_profile.coin = float(upgrade_profile.coin) - required_coin
        #     upgrade_profile.save()
        #     r = requests.post(url=url, json=PARAMS, headers=headers)
        #     if r.status_code == 200:
        #         mailWizardSubsType = MailWizardSubsType.objects.filter(id=subs_id).first()
        #
        #         mailWizardInfo = MailWizardInfo(property=None, neighbor=get_neighborhood, sender=user,
        #                                         subs_type=mailWizardSubsType,
        #                                         item_id=item_id,
        #                                         mail_count_target=mail_count_target)
        #         mailWizardInfo.save()
        #
        #         response['status'] = True
        #         response['data'] = {
        #             'payment': True,
        #             'upgrade_info': UserSerializer(manager).data['upgrade_info']
        #         }
        #         response['message'] = 'Mail wizard sent successfully'
        #
        #         try:
        #             mailWizardCeleryTask = MailWizardCeleryTasks()
        #             mailWizardCeleryTask.status = 0
        #             mailWizardCeleryTask.run_at = datetime.datetime.now()
        #             mailWizardCeleryTask.mail_wizard_info = mailWizardInfo
        #             mailWizardCeleryTask.save()
        #         except:
        #             print('Schedular insert error')
        #     else:
        #         response['status'] = False
        #         response['data'] = {
        #             'payment': False,
        #             'upgrade_info': UserSerializer(manager).data['upgrade_info']
        #         }
        #         response['message'] = 'Mail wizard sending unsuccessful'
        # except Exception as e:
        #     print('ex' + str(e))
        #     response['status'] = False
        #     response['data'] = {
        #         'payment': True,
        #         'upgrade_info': UserSerializer(manager).data['upgrade_info']
        #     }
        #     response['message'] = 'Mail wizard sending unsuccessful'
        # return Response(response)

    @staticmethod
    def dict_val(dict_obj, key):
        if key in dict_obj.keys():
            return dict_obj[key]
        return ""

    def hit_mailer_wizard(self, user, requested_property, full_name, full_address, mailing_city, mailing_state, mailing_zip,
                          user_info, item_id, subs_id, mail_count_target, is_neighbor):

        response = {'status': False, 'data': {}, 'message': ''}
        manager = user
        if not manager.is_admin:
            manager = User.objects.get(id=manager.invited_by)
        return_address_street = self.dict_val(user_info, 'address_street')
        return_address_city = self.dict_val(user_info, 'address_city')
        return_address_state = self.dict_val(user_info, 'address_state')
        return_address_zip = str(self.dict_val(user_info, 'address_zip'))

        # prop_address1 = [property.street, property.city, property.state, property.zip]
        # separator = ', '

        mailer_response_text = 'TEST RESPONSE'

        url = settings.MAILER_WIZARD_MICRO_SERVICE_DOMAIN+'mailer-service/send-mailer-data/'
        headers = {
            'Content-Type': 'application/json',
        }
        request_json = {
            "user_id": user.id,
            "list_id": requested_property.id,
            "response_text": mailer_response_text.strip(),
            "user_info": {
                "firstName": self.dict_val(user_info, 'first_name'),
                "lastName": self.dict_val(user_info, 'last_name'),
                "email": self.dict_val(user_info, 'email'),
                "proofEmail": self.dict_val(user_info, 'email'),
                "compName": self.dict_val(user_info, 'company_name'),
                "website": self.dict_val(user_info, 'website'),
                "telephoneNo": self.dict_val(user_info, 'phone_no')
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
                    "return_address1": return_address_street.strip(),
                    "return_city": return_address_city.strip(),
                    "return_state": return_address_state.strip(),
                    "return_zip": return_address_zip.strip(),
                    "prop_address1": requested_property.street,
                    "prop_city": requested_property.city,
                    "prop_state": requested_property.state,
                    "prop_zip": requested_property.zip
                },
            ]
        }

        try:
            upgrade_profile = UpgradeProfile.objects.filter(user=manager).first()
            required_coin = 0.0
            required_coin = required_coin + float(PaymentPlan.objects.filter(payment_plan_name='mailer-wizard',
                                                                             plan=upgrade_profile.plan).first()
                                                  .payment_plan_coin)*float(mail_count_target)
            if upgrade_profile.coin < required_coin:
                response['status'] = False
                response['data'] = {
                    'payment': False,
                    'upgrade_info': UserSerializer(manager).data['upgrade_info']
                }
                response['message'] = 'Sending unsuccessful! May have occured due to insufficient balance. '
                return Response(response)
            upgrade_profile.coin = float(upgrade_profile.coin) - required_coin
            upgrade_profile.save()
            r = requests.post(url=url, json=request_json, headers=headers)
            if r.status_code == 200:
                mail_wizard_subs_type = MailWizardSubsType.objects.filter(id=subs_id).first()

                mail_wizard_info = MailWizardInfo(property=None, neighbor=None, sender=user,
                                                  subs_type=mail_wizard_subs_type,
                                                  item_id=item_id,
                                                  request_json=request_json,
                                                  mail_count_target=mail_count_target)
                if is_neighbor:
                    mail_wizard_info.neighbor = requested_property
                else:
                    mail_wizard_info.property = requested_property
                mail_wizard_info.save()
                try:
                    mailer_wizard_user_info = MailWizardUserInfo.objects.get(user_id=user.id)
                except MailWizardUserInfo.DoesNotExist:
                    mailer_wizard_user_info = MailWizardUserInfo()
                mailer_wizard_user_info.user_id = user.id
                mailer_wizard_user_info.first_name = self.dict_val(user_info, 'first_name')
                mailer_wizard_user_info.last_name = self.dict_val(user_info, 'last_name')
                mailer_wizard_user_info.email = self.dict_val(user_info, 'email')
                mailer_wizard_user_info.phone_no = self.dict_val(user_info, 'phone_no')
                mailer_wizard_user_info.address_street = return_address_street
                mailer_wizard_user_info.address_city = return_address_city
                mailer_wizard_user_info.address_state = return_address_state
                mailer_wizard_user_info.address_zip = return_address_zip
                mailer_wizard_user_info.save()

                response['status'] = True
                response['data'] = {
                    'payment': True,
                    'upgrade_info': UserSerializer(manager).data['upgrade_info']
                }
                response['message'] = 'Mail sent successfully'

                try:
                    mail_wizard_celery_task = MailWizardCeleryTasks()
                    mail_wizard_celery_task.status = 0
                    mail_wizard_celery_task.run_at = datetime.datetime.now()
                    mail_wizard_celery_task.mail_wizard_info = mail_wizard_info
                    mail_wizard_celery_task.save()

                except Exception as e:
                    print('ex' + str(e))
                    traceback.print_exc()
                    print('Scheduler insert error')

            else:
                response['status'] = False
                response['data'] = {
                    'payment': False,
                    'upgrade_info': UserSerializer(manager).data['upgrade_info']

                }
                response['message'] = 'Mail sending unsuccessful'
        except Exception as e:
            print('ex' + str(e))
            response['status'] = False
            response['data'] = {
                'payment': True,
                'upgrade_info': UserSerializer(manager).data['upgrade_info']
            }
            response['message'] = 'Mail sending unsuccessful'
        return Response(response)

