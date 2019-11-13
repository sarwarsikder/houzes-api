import traceback

from django.conf import settings
from rest_framework.response import Response
from rest_framework.decorators import api_view
import requests

from api.models import Property

POWER_TRACE_HOST = getattr(settings, "POWER_TRACE_HOST", None)
POWER_TRACE_CLIENT_ID = getattr(settings, "POWER_TRACE_CLIENT_ID", None)
POWER_TRACE_CLIENT_SECRET = getattr(settings, "POWER_TRACE_CLIENT_SECRET", None)
power_trace_headers = {'client_id': POWER_TRACE_CLIENT_ID,
                       'client_secret': POWER_TRACE_CLIENT_SECRET}


@api_view(['GET'])
def get_all_request_by_user_id(request, user_id):
    try:
        url = POWER_TRACE_HOST + 'api/powertrace/getAllRequestByUserId/' + str(user_id)
        power_trace_all_request_list_by_userId_res = requests.get(url, headers=power_trace_headers)
        return Response(power_trace_all_request_list_by_userId_res.json())
    except:
        traceback.print_exc()
        return Response({'code': 500, 'message': 'Server Error!'})


@api_view(['GET'])
def get_result_by_id(request, trace_id):
    try:
        url = POWER_TRACE_HOST + 'api/powertrace/trace-result-by-id?trace_request_id=' + str(trace_id)
        power_trace_result_by_id_res = requests.post(url, headers=power_trace_headers)
        return Response(power_trace_result_by_id_res.json())
    except:
        traceback.print_exc()
        return Response({'code': 500, 'message': 'Server Error!'})


@api_view(['POST'])
def create(request):
    try:
        power_trace_request_url = POWER_TRACE_HOST + 'api/powertrace/createRequest'
        power_trace_start_by_data_url = POWER_TRACE_HOST + 'api/powertrace/save-powertrace-info-by-data'

        if 'trace_name' not in request.data or request.data['trace_name'] is None or request.data['trace_name'].__eq__(
                ''):
            return Response({'code': 400, 'message': 'Trace name is required!'})
        if 'package_type' not in request.data or request.data['package_type'] is None:
            return Response({'code': 400, 'message': 'Package Type is required!'})
        if 'user_id' not in request.data or request.data['user_id'] is None:
            return Response({'code': 400, 'message': 'User id is required!'})
        if 'countId' not in request.data or request.data['countId'] is None:
            return Response({'code': 400, 'message': 'Count Id is required!'})

        power_trace_request_pload = {'trace_name': request.data['trace_name'],
                                     'package_type': request.data['package_type'],
                                     'user_id': request.data['user_id'], 'countId': request.data['countId']}
        power_trace_start_by_data_pload = {}
        total = int(request.data['countId'])
        for i in range(total):
            try:
                power_trace_start_by_data_pload['owner_name' + str(i)] = request.data['owner_name' + str(i)]
                power_trace_start_by_data_pload['owner_address' + str(i)] = request.data['owner_address' + str(i)]
            except:
                return Response(
                    {'code': 500, 'message': 'Failed to create request! owner_name/owner_address is missing.'})

        ## Powertrace request
        power_trace_request_res = requests.post(power_trace_request_url, data=power_trace_request_pload,
                                                headers=power_trace_headers)
        if power_trace_request_res.json()['code'] == 200:
            power_trace_request_id = int(power_trace_request_res.json()['data']['id'])
            power_trace_start_by_data_pload['trace_request_id'] = power_trace_request_id
            power_trace_start_by_data_pload['count_id'] = request.data['countId']

            power_trace_start_by_data_res = requests.post(power_trace_start_by_data_url,
                                                          data=power_trace_start_by_data_pload,
                                                          headers=power_trace_headers)
            print(power_trace_start_by_data_res.json())
            if power_trace_start_by_data_res.json()['code'] == 200:
                try:
                    if 'property_id' in request.data:
                        property_id = int(request.data['property_id'])
                        Property.objects.filter(id=property_id).update(power_trace_request_id=power_trace_request_id)
                except:
                    traceback.print_exc()
                return Response(power_trace_request_res.json())
            else:
                return Response({'code': 400, 'message': 'PowerTrace Failed due to Information parsing failure!',
                                 'data': power_trace_start_by_data_res.json()})
        else:
            return Response(
                {'code': 400, 'message': 'Trace name is already exists!', 'data': power_trace_request_res.json()})
    except:
        traceback.print_exc()
        return Response({'code': 500, 'message': 'Failed to create request! Server Error!'})

