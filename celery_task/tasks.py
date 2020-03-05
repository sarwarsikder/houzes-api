import requests
from celery import shared_task
from celery.task import periodic_task, task
import datetime

from api.models import *
from api.serializers import UserSerializer
from houzes_api.celery_app import app
from houzes_api import  settings


@app.task()
def test_celery():
    print("Celery works!")


@task()
@periodic_task(run_every=datetime.timedelta(seconds=30))
def periodic_task():
    print("************PERIODIC CHECK FOR TASKS STARTED************************")
    pending_tasks = MailWizardCeleryTasks.objects.filter(status=0, run_at__lte=datetime.datetime.now())
    print(pending_tasks)
    for pending_task in pending_tasks:
        pending_task.status = 1
        pending_task.save()

        # process_celery_task
        process_celery_task.delay(pending_task.id)

    print("************PERIODIC CHECK FOR TASKS ENDED************************")


@app.task()
def process_celery_task(task_id):
    print("#####################PROCESSING A TASK#######################")
    celery_task: MailWizardCeleryTasks = MailWizardCeleryTasks.objects.get(pk=task_id)
    mail_wizard_info: MailWizardInfo = MailWizardInfo.objects.get(pk=celery_task.mail_wizard_info_id)

    # sending mailer wizard
    send_mailer_wizard(mail_wizard_info)

    celery_task.status = 2
    celery_task.save()
    print("Completed Celery Task: {}".format(celery_task.id))

    mail_wizard_info.mail_counter = mail_wizard_info.mail_counter + 1
    mail_wizard_info.save()
    print("Increase Mail Counter: {}".format(mail_wizard_info.mail_counter))

    if mail_wizard_info.mail_counter < mail_wizard_info.mail_count_target:
        add_new_task(mail_wizard_info, celery_task)


def add_new_task(mail_wizard_info: MailWizardInfo, old_task: MailWizardCeleryTasks):
    mail_wizard_subs_type: MailWizardSubsType = MailWizardSubsType.objects.get(pk=mail_wizard_info.subs_type_id)
    run_at = datetime.datetime.now() + datetime.timedelta(days=mail_wizard_subs_type.days_interval)
    print('next run date: {}'.format(run_at))
    celery_task: MailWizardCeleryTasks = MailWizardCeleryTasks(run_at=run_at,
                                                               mail_wizard_info_id=old_task.mail_wizard_info_id)
    celery_task.save()


def send_mailer_wizard(mail_wizard_info: MailWizardInfo):
    print("Sending Mailer wizard...")
    if mail_wizard_info.property_id:
        res = send_mail_wizard_to_property(mail_wizard_info)
        print(res)
    elif mail_wizard_info.neighbor_id:
        res = send_mail_wizard_to_neighbor(mail_wizard_info)
        print(res)


def send_mail_wizard_to_property(mail_wizard: MailWizardInfo):
    response = {'status': False, 'data': {}, 'message': ''}
    property = Property.objects.get(id=mail_wizard.property_id)
    user = User.objects.get(id=mail_wizard.sender_id)

    if len(property.owner_info) == 0:
        response['status'] = False
        response['message'] = 'Owner info is empty. Please apply Fetch Ownership to get Owner info.'
        return response

    full_name = property.owner_info[0]['full_name']
    mailing_street = property.owner_info[0]['formatted_address']['street']['formatted_full_street_name']
    mailing_city = property.owner_info[0]['formatted_address']['city']
    mailing_state = property.owner_info[0]['formatted_address']['state']
    mailing_zip = property.owner_info[0]['formatted_address']['zip_code']

    text_body = ''
    item_id = mail_wizard.item_id

    prop_address1 = [property.street, property.city, property.state, property.zip]
    separator = ', '

    url = settings.MAILER_WIZARD_MICRO_SERVICE_DOMAIN + 'mailer-service/send-mailer-data/'
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
                "mailing_address1": mailing_street.strip(),
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
        r = requests.post(url=url, json=PARAMS, headers=headers)
        if r.status_code == 200:
            response['status'] = True
            response['data'] = {
                'payment': True,
                'upgrade_info': UserSerializer(manager).data['upgrade_info']
            }
            response['message'] = 'Mail wizard sent successfully'
        else:
            response['status'] = False
            response['data'] = {
                'payment': False,
                'upgrade_info': UserSerializer(manager).data['upgrade_info']

            }
            response['message'] = 'Mail wizard sending unsuccessful'
    except Exception as e:
        print('ex' + str(e))
        response['status'] = False
        response['data'] = {
            'payment': True,
            'upgrade_info': UserSerializer(manager).data['upgrade_info']
        }
        response['message'] = 'Mail wizard sending unsuccessful'
    return response


def send_mail_wizard_to_neighbor(mail_wizard: MailWizardInfo):
    response = {'status': False, 'data': {}, 'message': ''}
    get_neighborhood = GetNeighborhood.objects.get(id=mail_wizard.neighbor_id)
    user = User.objects.get(id=mail_wizard.sender_id)

    if get_neighborhood.ownership_info == {}:
        response['status'] = False
        response['message'] = 'Owner info is empty for this neighbor. Please apply Fetch Ownership to get Owner info.'
        return response

    full_name = get_neighborhood.ownership_info['owner_info']['full_name']
    mailing_street = get_neighborhood.ownership_info['owner_info']['formatted_address']['street']['formatted_full_street_name']
    mailing_city = get_neighborhood.ownership_info['owner_info']['formatted_address']['city']
    mailing_state = get_neighborhood.ownership_info['owner_info']['formatted_address']['state']
    mailing_zip = get_neighborhood.ownership_info['owner_info']['formatted_address']['zip_code']

    text_body = ''
    item_id = mail_wizard.item_id

    prop_address1 = [get_neighborhood.street, get_neighborhood.city, get_neighborhood.state, get_neighborhood.zip]
    separator = ', '

    url = settings.MAILER_WIZARD_MICRO_SERVICE_DOMAIN + 'mailer-service/send-mailer-data/'
    headers = {
        'Content-Type': 'application/json',
    }
    PARAMS = {
        "user_id": user.id,
        "list_id": get_neighborhood.id,
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
                "mailing_address1": mailing_street.strip(),
                "mailing_city": mailing_city.strip(),
                "mailing_state": mailing_state.strip(),
                "mailing_zip": mailing_zip.strip(),
                "prop_address1": separator.join(prop_address1),
                "prop_city": get_neighborhood.city,
                "prop_state": get_neighborhood.state,
                "prop_zip": get_neighborhood.zip
            },
        ]
    }

    try:
        manager = user
        if not manager.is_admin:
            manager = User.objects.get(id=manager.invited_by)
        r = requests.post(url=url, json=PARAMS, headers=headers)
        if r.status_code == 200:
            response['status'] = True
            response['data'] = {
                'payment': True,
                'upgrade_info': UserSerializer(manager).data['upgrade_info']
            }
            response['message'] = 'Mail wizard sent successfully'
        else:
            response['status'] = False
            response['data'] = {
                'payment': False,
                'upgrade_info': UserSerializer(manager).data['upgrade_info']
            }
            response['message'] = 'Mail wizard sending unsuccessful'
    except Exception as e:
        print('ex' + str(e))
        response['status'] = False
        response['data'] = {
            'payment': True,
            'upgrade_info': UserSerializer(manager).data['upgrade_info']
        }
        response['message'] = 'Mail wizard sending unsuccessful'
    return response
