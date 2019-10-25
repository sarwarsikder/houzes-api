import requests
from django.contrib.auth.views import LoginView
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.views import generic
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.utils import json
from api.models import User

from houzes_api.settings import CLIENT_ID, CLIENT_SECRET

# REDIRECT_URL = 'http://localhost:4200/dashboard'
REDIRECT_URL = 'https://www.google.com'


# @api_view(['POST'])
# @permission_classes([AllowAny])
@csrf_exempt
def login(request):
    status = False
    message = ""
    try:
        username = request.POST['email']
        password = request.POST['password']
        client_id = request.POST['client_id']
        client_secret = request.POST['client_secret']
        grant_type = request.POST['grant_type']
    except:
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        username = body['email']
        password = body['password']
        client_id = body['client_id']
        client_secret = body['client_secret']
        grant_type = body['grant_type']

    # print(User.objects.filter(email=username).count())
    if User.objects.filter(email=username).count() > 0:
        user = User.objects.filter(email=username)
        if user[0].is_active == False:
            message = "Please verify your email before sign in"
            return JsonResponse({"status": status, "data": None, "message": message})

    current_url = request.scheme + '://' + request.META['HTTP_HOST']
    print(current_url + '/o/token/')
    print(grant_type)
    print(username)
    print(password)
    print(client_secret)
    print(client_id)

    try:
        r = requests.post(
            current_url + '/o/token/',
            data={
                'grant_type': grant_type,
                'username': username,
                'password': password,
                'client_id': client_id,
                'client_secret': client_secret,
            }, verify=True)
    except:
        print("Something Went Wrong")

    print(r.json())
    # response = redirect(REDIRECT_URL)
    # response.set_cookie('HOUZES_ACCESS_TOKEN', r.json()['access_token'], path='/', domain='.localhost:4200')
    # response.set_cookie('HOUZES_REFRESH_TOKEN', r.json()['refresh_token'], path='/', domain='.localhost:4200')
    # print(response)
    if 'error' in r.json():
        message = "Email or password incorrect"
        return JsonResponse({"status": status, "data": r.json(), "message": message})

    status = True
    message = "Successful log in"
    return JsonResponse({"status": status, "data": r.json(), "message": message})


@csrf_exempt
def facebook_login(request):
    print('working')
    try:
        access_token = request.POST['access_token']
    except:
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        access_token = body['access_token']
        r = requests.post(
            "https://graph.facebook.com/me",
            data={
                'fields': "email,first_name,last_name,gender,location,picture",
                'access_token': access_token,

            },
        )
        print(r.json()['email'])

        if User.objects.filter(email=r.json()['email']).count() > 0:
            print('This user exist')
            current_url = request.scheme + '://' + request.META['HTTP_HOST']
            # r_token = requests.post(
            #     current_url + '/o/authorize/',
            #     data={
            #        'response_type': 'code',
            #        'username': r.json()['email'],
            #        'client_id': CLIENT_ID,
            #        'client_secret': CLIENT_SECRET,
            #    },
            # )
            # print(r_token.json())
        return JsonResponse(r.json())
