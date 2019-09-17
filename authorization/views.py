import requests
from django.contrib.auth.views import LoginView
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.views import generic
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from requests import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.utils import json

from houzes_api.settings import CLIENT_ID, CLIENT_SECRET

# REDIRECT_URL = 'http://localhost:4200/dashboard'
REDIRECT_URL = 'https://www.google.com'


# @api_view(['POST'])
# @permission_classes([AllowAny])
@csrf_exempt
def login(request):
    # print(request.data['email'])
    # print(request.data['password'])
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    current_url = request.scheme + '://' + request.META['HTTP_HOST']
    r = requests.post(
        current_url + '/o/token/',
        data={
            'grant_type': 'password',
            'username': body['email'],
            'password': body['password'],
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
        },
    )

    print(r.json())
    # response = redirect(REDIRECT_URL)
    # response.set_cookie('HOUZES_ACCESS_TOKEN', r.json()['access_token'], path='/', domain='.localhost:4200')
    # response.set_cookie('HOUZES_REFRESH_TOKEN', r.json()['refresh_token'], path='/', domain='.localhost:4200')
    # print(response)
    if 'error' in r.json():
        return JsonResponse({'response': 'failed'})
    return JsonResponse(r.json())
