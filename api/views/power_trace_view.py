import traceback

from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
import requests

from api.models import Property
from api.serializers import PropertySerializer


@api_view(['GET'])
def start(request):
    return Response('powertrace start!')

@api_view(['POST'])
def create(request):
    try:
        power_trace_request_url = 'http://powertrace-service.ratoolkit.com:8080/ra-powertrace/api/powertrace/createRequest'
        power_trace_start_by_data_url = 'http://powertrace-service.ratoolkit.com:8080/ra-powertrace/api/powertrace/save-powertrace-info-by-data'
        headers = {'client_id': 'HQARK3QZDPLLBWSMVY0X2C5UJ2B15YQJSIY',
                   'client_secret': 'URBVBVBDDJ2E2JEBJEO84594T546VJVBKJGB'}


        if 'trace_name' not in request.data or request.data['trace_name'] is None or request.data['trace_name'].__eq__(''):
            return Response({'code': 400, 'message': 'Trace name is required!'})
        if 'package_type' not in request.data or request.data['package_type'] is None or request.data['package_type'].__eq__(''):
            return Response({'code': 400, 'message': 'Package Type is required!'})
        if 'user_id' not in request.data or request.data['user_id'] is None or request.data['user_id'].__eq__(''):
            return Response({'code': 400, 'message': 'User id is required!'})
        if 'countId' not in request.data or request.data['countId'] is None or request.data['countId'].__eq__(''):
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
                return Response({'code': 500, 'message': 'Failed to create request! owner_name/owner_address is missing.'})


        ## Powertrace request
        power_trace_request_res = requests.post(power_trace_request_url, data=power_trace_request_pload, headers=headers)
        if power_trace_request_res.json()['code'] == 200:
            power_trace_start_by_data_pload['trace_request_id'] = power_trace_request_res.json()['data']['id']
            power_trace_start_by_data_pload['count_id'] = request.data['countId']

            power_trace_start_by_data_res = requests.post(power_trace_start_by_data_url, data=power_trace_start_by_data_pload, headers=headers)
            print(power_trace_start_by_data_res.json())
            if power_trace_start_by_data_res.json()['code'] == 200:
                return Response(power_trace_request_res.json())
            else:
                return Response({'code': 400, 'message': 'PowerTrace Failed due to Information parsing failure!', 'data': power_trace_start_by_data_res.json()})
        else:
            return Response({'code': 400, 'message': 'Trace name already exists!', 'data': power_trace_request_res.json()})
    except:
        traceback.print_exc()
        return Response({'code': 500, 'message': 'Failed to create request! Server Error!'})

class PowerTraceView(APIView):
    def get(self, request):
        return Response('powertrace get!')
