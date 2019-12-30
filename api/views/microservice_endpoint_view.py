import requests
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.decorators import authentication_classes, permission_classes

from api.models import GetNeighborhood


@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def provide_ownership_info(request,id):
    return JsonResponse(get_owner_info_by_request_id(id))

def get_owner_info_by_request_id(request_id):
    status = False
    data = {}
    message = ''
    url = 'http://58.84.34.65:8080/ownership-micro-service/api/owner-info/get-owner-info-from-request-id'
    headers = {
        'client_id': 'ZDPLLBHQARK3QWSMVY0X2B15YQJSIYC5UJ2',
        'client_secret': 'RBVUBV6VJVBKJBDDJ2E2JEBJEO84594T54GB'
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
        GetNeighborhood.objects.filter(ownership_info_request_id=request_id).update(ownership_info=objectResponse['data'],owner_status = "complete")
    else:
        status = False
        message = objectResponse['message']
        data = {}
    return ({'status': status, 'data': data, 'message': message})