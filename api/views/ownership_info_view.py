import requests
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework.utils import json
from api.models import *
from api.serializers import *
from houzes_api import settings
from houzes_api.util.file_upload import file_upload
from resizeimage import resizeimage
from PIL import Image
from io import BytesIO
import time


@csrf_exempt
def get_owner_info_by_address(request):
    objectResponse = None
    message=""
    data = []
    status = False
    url = 'http://172.18.1.11:8080/ownership-micro-service/api/owner-info/get-owner-info-by-address'
    address = request.POST['address']
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'client_id': 'ZDPLLBHQARK3QWSMVY0X2B15YQJSIYC5UJ2',
        'client_secret': 'RBVUBV6VJVBKJBDDJ2E2JEBJEO84594T54GB'
    }
    PARAMS = {'address': address}

    try:
        r = requests.post(url=url, data=PARAMS, headers = headers)
        jsonResponse = r.json()
        objectResponse = json.loads(json.dumps(jsonResponse))
        print(objectResponse['message'])

    except:
        status = False
        message = 'Micro Service Error'
        data = {}

    if 'error' in r.json():
        message = 'Error'
        data = {}
        status = False
        return JsonResponse({"status": status, 'data' : data, 'message' : message})
    if objectResponse['status'] == 200 :
        status = True
    if objectResponse['status'] != 200 :
        status = False
    message = objectResponse['message']
    data = objectResponse['owner_info']
    return JsonResponse({"status": status, 'data': data, 'message' : message})
