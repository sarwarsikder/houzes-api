import requests
import shortuuid
import traceback
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.decorators import authentication_classes, permission_classes

from api.models import GetNeighborhood
from houzes_api import settings

FETCH_OWNER_INFO_CLIENT_ID = getattr(settings, "FETCH_OWNER_INFO_CLIENT_ID", None)
FETCH_OWNER_INFO_CLIENT_SECRET = getattr(settings, "FETCH_OWNER_INFO_CLIENT_SECRET", None)

POWER_TRACE_HOST = getattr(settings, "POWER_TRACE_HOST", None)
POWER_TRACE_CLIENT_ID = getattr(settings, "POWER_TRACE_CLIENT_ID", None)
POWER_TRACE_CLIENT_SECRET = getattr(settings, "POWER_TRACE_CLIENT_SECRET", None)
power_trace_headers = {'client_id': POWER_TRACE_CLIENT_ID,
                       'client_secret': POWER_TRACE_CLIENT_SECRET}


@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def provide_ownership_info(request,id):
    return JsonResponse(get_owner_info_by_request_id(id))

def provide_power_trace(request,id):
    print(id)
    power_trace_result = get_power_trace_by_request_id(id)
    print(power_trace_result)
    return JsonResponse(power_trace_result)

def get_owner_info_by_request_id(request_id):
    get_neighborhoods = GetNeighborhood.objects.filter(ownership_info_request_id=request_id)
    status = False
    data = {}
    message = ''
    url = 'http://58.84.34.65:8080/ownership-micro-service/api/owner-info/get-owner-info-from-request-id'
    headers = {
        'client_id': FETCH_OWNER_INFO_CLIENT_ID,
        'client_secret': FETCH_OWNER_INFO_CLIENT_SECRET
    }
    PARAMS = {
        "id": request_id
    }
    try:
        r = requests.post(url=url, data=PARAMS, headers=headers)
        objectResponse = r.json()
        print(objectResponse)
    except:
        print('ex')
        status = False
        message = 'Get neighborhood micro service error'
        return ({"status": status, "data": {}, 'message': message})
    if (objectResponse['status']) == 200:
        status = True
        message = objectResponse['message']
        data = objectResponse['data']
        for neighbor in get_neighborhoods :
            for owner_info in objectResponse['data']:
                if int(owner_info['property_id']) == neighbor.id:
                    neighbor.ownership_info = owner_info
                    neighbor.owner_status = "complete"
                    neighbor.save()
        if get_neighborhoods.first():
            if get_neighborhoods.first().is_power_trace_requested:
                power_trace_request = request_power_trace(get_neighborhoods)
                print('after power trace request')
                print(power_trace_request)
                if power_trace_request['code']!=200:
                    get_neighborhoods.update(status='complete')
            else :
                get_neighborhoods.update(status='complete')
    else:
        status = False
        message = objectResponse['message']
        data = {}
    return ({'status': status, 'data': data, 'message': message})

def request_power_trace(get_neighborhoods):
    print('REQUEST POWER TRACE')
    print(generate_shortuuid())
    try:
        power_trace_request_url = POWER_TRACE_HOST + 'api/powertrace/createRequest'
        power_trace_start_by_data_url = POWER_TRACE_HOST + 'api/powertrace/save-powertrace-info-by-data'


        power_trace_request_pload = {'trace_name': generate_shortuuid(),
                                     'package_type': 2,
                                     'user_id': get_neighborhoods.first().requested_by.id}
        power_trace_start_by_data_pload = {}
        total = 0

        total = get_neighborhoods.count()
        power_trace_request_pload['countId'] = total
        i=0
        for neighbor in get_neighborhoods:
            try:
                power_trace_start_by_data_pload['owner_name' + str(i)] = neighbor.ownership_info['owner_info']['full_name']
                power_trace_start_by_data_pload['owner_address' + str(i)] = neighbor.ownership_info['owner_info']['full_address']
                power_trace_start_by_data_pload['property_id' + str(i)] = int(neighbor.ownership_info['property_id'])
            except:
                return (
                    {'code': 500,
                     'message': 'Failed to create request! owner_name/owner_address/property_id is missing.'})
            i = i+1
        ## Powertrace request
        power_trace_request_res = requests.post(power_trace_request_url, data=power_trace_request_pload,
                                                headers=power_trace_headers)
        if power_trace_request_res.json()['code'] == 200:
            power_trace_request_id = int(power_trace_request_res.json()['data']['id'])
            power_trace_start_by_data_pload['trace_request_id'] = power_trace_request_id
            power_trace_start_by_data_pload['count_id'] = total

            power_trace_start_by_data_res = requests.post(power_trace_start_by_data_url,
                                                          data=power_trace_start_by_data_pload,
                                                          headers=power_trace_headers)
            # print(power_trace_start_by_data_res.json())
            if power_trace_start_by_data_res.json()['code'] == 200:
                get_neighborhoods.update(power_trace_request_id=power_trace_start_by_data_res.json()['data'][0]['trace_requests_id'],power_trace_status='requested')
                return power_trace_request_res.json()
            else:
                return {'code': 400, 'message': 'PowerTrace Failed due to Information parsing failure!',
                                 'data': power_trace_start_by_data_res.json()}
        else:
            return {'code': 400, 'message': 'Trace name is already exists!', 'data': power_trace_request_res.json()}
    except:
        traceback.print_exc()
        return {'code': 500, 'message': 'Failed to create request! Server Error!'}

def get_power_trace_by_request_id(id):
    get_neighbors = GetNeighborhood.objects.filter(power_trace_request_id=id)
    try:
        power_trace_request_url = POWER_TRACE_HOST + 'api/powertrace/trace-result-by-id?trace_request_id='+str(id)
        power_trace_result_by_id_res = requests.post(power_trace_request_url, headers=power_trace_headers)
        if power_trace_result_by_id_res.json()['code'] == 200:
            for power_trace_result in power_trace_result_by_id_res.json()['data']:
                for neighbor in get_neighbors:
                    if neighbor.id == int(power_trace_result['client_lead_info_id']):
                        neighbor.power_trace_status = "complete"
                        neighbor.power_trace = power_trace_result
                        neighbor.save()

    except:
        traceback.print_exc()
        return {'code': 500, 'message': 'Failed to create request! Server Error!'}
    get_neighbors.update(status ='complete')
    return power_trace_result_by_id_res.json()

def generate_shortuuid():
    shortuuid.set_alphabet("abcdefghijklmnopqrstuvwxyz0123456789")
    gUid = str(shortuuid.random(length=16))
    return gUid
