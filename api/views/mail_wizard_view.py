import time

import pytz
from rest_framework import viewsets, status
from rest_framework.decorators import action
import requests
from api.serializers import *
from api.models import *
from rest_framework.response import Response
import datetime
from houzes_api import settings
import traceback

from houzes_api.util.s3_image_upload import image_upload


class MailWizardInfoViewSet(viewsets.ModelViewSet):
    queryset = MailWizardInfo.objects.all()
    serializer_class = MailWizardInfoSerializer

    @action(detail=False, methods=['POST'], url_path='property/(?P<id>[\w-]+)')
    def send_mail_to_property_owner(self, request, *args, **kwargs):
        response = {'status': False, 'data': {}, 'message': ''}
        property = Property.objects.get(id=kwargs['id'])
        try:
            data = request.data
        except:
            data = request.POST
        user = User.objects.get(id=request.user.id)

        # print(property.__dict__)
        # print(len(property.owner_info))

        if len(property.owner_info) == 0:
            response['status'] = False
            response['message'] = 'Sending unsuccessful! Ownership info is required.'
            return Response(response)

        full_name = property.owner_info[0]['full_name']
        mailing_street = property.owner_info[0]['formatted_address']['street']['formatted_full_street_name']
        mailing_city = property.owner_info[0]['formatted_address']['city']
        mailing_state = property.owner_info[0]['formatted_address']['state']
        mailing_zip = property.owner_info[0]['formatted_address']['zip_code']

        # user_info = request.data['user_info']

        item_id = data['tem_item_id']
        subs_id = data['subs_id']
        mail_count_target = data['mail_count']

        return self.hit_mailer_wizard(user, property, full_name, mailing_street, mailing_city, mailing_state, mailing_zip,
                                    item_id, subs_id, mail_count_target, False,data, request)

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
        try:
            data = request.data
        except:
            data = request.POST

        get_neighborhood = GetNeighborhood.objects.get(id=kwargs['id'])
        user = User.objects.get(id=request.user.id)

        if get_neighborhood.ownership_info == {}:
            response['status'] = False
            response['message'] = 'Owner info is empty for this neighbor. Please apply Fetch Ownership to get Owner info.'
            return Response(response)

        full_name = get_neighborhood.ownership_info['owner_info']['full_name']
        try:
            mailing_street = get_neighborhood.ownership_info['owner_info']['formatted_address']['street']['formatted_full_street_name']
        except:
            mailing_street = str(get_neighborhood.ownership_info['owner_info']['formatted_address']['street']['street_number'])+' '+get_neighborhood.ownership_info['owner_info']['formatted_address']['street']['street_name']
        mailing_city = get_neighborhood.ownership_info['owner_info']['formatted_address']['city']
        mailing_state = get_neighborhood.ownership_info['owner_info']['formatted_address']['state']
        mailing_zip = get_neighborhood.ownership_info['owner_info']['formatted_address']['zip_code']

        # user_info = request.data['user_info']

        item_id = data['tem_item_id']
        subs_id = data['subs_id']
        mail_count_target = data['mail_count']

        return self.hit_mailer_wizard(user, get_neighborhood, full_name, mailing_street, mailing_city, mailing_state, mailing_zip,
                                       item_id, subs_id, mail_count_target, True, data, request)

    @staticmethod
    def dict_val(dict_obj, key):
        if key in dict_obj.keys():
            return dict_obj[key]
        return ""

    def hit_mailer_wizard(self, user, requested_property, full_name, mailing_street, mailing_city, mailing_state, mailing_zip,
                           item_id, subs_id, mail_count_target, is_neighbor,data, request):

        response = {'status': False, 'data': {}, 'message': ''}
        manager = user
        is_file = False
        if 'logo' in data or 'mailing_list' in data or 'property_image' in data or 'user_photo' in data:
            is_file = True

        if not manager.is_team_admin:
            manager = User.objects.get(id=manager.invited_by)

        return_address_street =data['address_street']
        return_address_city = data['address_city']
        return_address_state = data['address_state']
        return_address_zip = data['address_zip']

        mailer_response_text = 'TEST RESPONSE'

        url = settings.MAILER_WIZARD_MICRO_SERVICE_DOMAIN+'mailer-service/send-mailer-data/'
        headers = {
            'Content-Type': 'application/json',
        }
        request_json = {
            "user_id": user.id,
            "list_id": requested_property.id,
            "response_text": mailer_response_text.strip(),
            "is_file" : False,
            "user_info": {
                "firstName": data['first_name'].strip() if 'first_name' in data else '',
                "lastName": data['last_name'].strip() if 'last_name' in data else '',
                "email": data['email'].strip() if 'email' in data else '',
                "proofEmail": data['email'].strip() if 'email' in data else '',
                "compName": data['company_name'].strip() if 'company_name' in data else '',
                "website": data['website'].strip() if 'website' in data else '',
                "telephoneNo": data['phone_no'].strip() if 'phone_no' in data else '',
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
                    "mailing_address1": mailing_street.strip(),
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
                    "prop_zip": requested_property.zip,
                    'offer_code': data['offer_code'].strip() if 'offer_code' in data else None
                },
            ]
        }
        logo = None
        cover_photo = None
        if is_file:
            if 'logo' in data:
                img_url = self.get_uploaded_img_url(request.FILES['logo'])
                if img_url:
                    request_json["logo"] = img_url
                    logo = img_url
            if 'property_image' in data:
                img_url = self.get_uploaded_img_url(request.FILES['property_image'])
                if img_url:
                    request_json["property_image"] = img_url
                    cover_photo = img_url
            if 'user_photo' in data:
                img_url = self.get_uploaded_img_url(request.FILES['user_photo'])
                if img_url:
                    request_json["user_photo"] = img_url

            request_json["is_file"] = True

        else:
            request_json["is_file"] = False
        print(request_json)
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
            print(r)
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

                mailer_wizard_user_info.first_name = data['first_name'].strip() if 'first_name' in data else ''
                mailer_wizard_user_info.last_name = data['last_name'].strip() if 'last_name' in data else ''
                mailer_wizard_user_info.email = data['email'].strip() if 'email' in data else ''
                mailer_wizard_user_info.phone_no = data['phone_no'].strip() if 'phone_no' in data else ''
                mailer_wizard_user_info.website = data['website'].strip() if 'website' in data else ''
                if logo:
                    mailer_wizard_user_info.logo = logo
                if cover_photo:
                    mailer_wizard_user_info.cover_photo = cover_photo
                mailer_wizard_user_info.agent_license = data['offer_code'].strip() if 'offer_code' in data else ''
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
                    mail_wizard_celery_task.run_at = pytz.UTC.localize(datetime.datetime.now())
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

    def get_uploaded_img_url(self,file):
        try:
            s3_path_prefix = "photos/mail-wizard/"
            file_name = generate_shortuuid() + str(time.time()) + '.png'
            img_data = image_upload(file, s3_path_prefix, file_name, True)
            if img_data["status"]:
                full_img_path = img_data['full_img_url']
                thumb_img_path = img_data['thumb_url']
                print(full_img_path)
                return full_img_path

        except:
            print('::::EXCEPTION OCCOURED WHILE UPLOADING::::')
            traceback.print_exc()
            return None

