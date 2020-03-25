import datetime
import json

import jwt
import requests
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from social_core.backends.oauth import BaseOAuth2
from social_core.utils import handle_http_errors

from api.models import *
from houzes_api import settings


class AppleOAuth2(BaseOAuth2):
    """apple authentication backend"""

    name = 'apple'
    ACCESS_TOKEN_URL = 'https://appleid.apple.com/auth/token'
    SCOPE_SEPARATOR = ','
    ID_KEY = 'uid'
    access_token = ''

    # @csrf_exempt
    @handle_http_errors
    # @api_view(['POST'])
    # @permission_classes([AllowAny])
    # @staticmethod
    def do_auth(self, request, *args, **kwargs):
        """
        Finish the auth process once the access_token was retrieved
        Get the email from ID token received from apple
        """
        # print(request.body)
        # body_unicode = request.body.decode('utf-8')
        # print(body_unicode)
        # body = json.loads(body_unicode)
        # print(body)
        # access_token = body['access_token']
        access_token = 'c0b268acca7e64c04a1a9074dbbe28718.0.ntqv.K3_ckZWPd4yGTrgkRzm7ew'
        # access_token = 'eyJraWQiOiI4NkQ4OEtmIiwiYWxnIjoiUlMyNTYifQ.eyJpc3MiOiJodHRwczovL2FwcGxlaWQuYXBwbGUuY29tIiwiYXVkIjoiY29tLnJhLmhvdXplcy1pb3MiLCJleHAiOjE1ODUwNjgyNTcsImlhdCI6MTU4NTA2NzY1Nywic3ViIjoiMDAwMzA1LjgyODYzZjliYTBkMjRmNTZhM2VlOTRmOGI0YWZhMzFmLjA5NTkiLCJjX2hhc2giOiJJdDB2cEx6WU9Ha0p3d2NwSmdmRWhBIiwiZW1haWwiOiJ3b3Jrc3BhY2VpbmZvdGVjaEBnbWFpbC5jb20iLCJlbWFpbF92ZXJpZmllZCI6InRydWUiLCJhdXRoX3RpbWUiOjE1ODUwNjc2NTcsIm5vbmNlX3N1cHBvcnRlZCI6dHJ1ZX0.bNRvdAxsNYa0ccAFaDm1ooPw_8gb9wmiUdaxNvDeEIjMWUjR5pwgj3BiYIOYeK3Jg7NXiNWN3D4esT6FwdtwPqEo1IkUKD-FW-KM4R5ChFKA7owE8C5bKvudYFUBgoxthysFe7BaTQsrvKJNkJYSh_slgdT7OfoZZm-TxMNKoI8FuXLwu5oSzXIa5s1KRwir4qQXlXUpRRif1T5kX-iXRP_pNeakn7bmzgjn2OtA_BlYDxwNhkjzqSgrkEFdcppvxTMAhsBpQJhWoUm0eO2g0SPRmBPKkNxbieg_f5HJlmhnY_YS1ntMTcM7d_A2ybO8uxPLVoxdCt-wRTfrPBYVug'
        print(':::::::::::::::::::PRINTING ACCESS TOKEN:::::::::::::::::::')
        print(access_token)
        response_data = {}
        client_id = settings.SOCIAL_AUTH_APPLE_ID_CLIENT
        client_secret = AppleOAuth2.get_key_and_secret(self)

        headers = {'content-type': "application/x-www-form-urlencoded"}
        data = {
            'client_id': client_id,
            'client_secret': client_secret,
            'code': access_token,
            'grant_type': 'authorization_code',
            'redirect_uri': 'https://houzes.com/'
        }

        res = requests.post(AppleOAuth2.ACCESS_TOKEN_URL, data=data, headers=headers)
        print(res)
        response_dict = res.json()
        print('::::::::::::::::APPLE RESPONSE:::::::::::::::')
        print(response_data)
        id_token = response_dict.get('id_token', None)

        if id_token:
            decoded = jwt.decode(id_token, '', verify=False)
            response_data.update({'email': decoded['email']}) if 'email' in decoded else None
            response_data.update({'uid': decoded['sub']}) if 'sub' in decoded else None

        response = kwargs.get('response') or {}
        response.update(response_data)
        response.update({'access_token': access_token}) if 'access_token' not in response else None

        kwargs.update({'response': response, 'backend': self})
        print('KAM KORE AI PORJONTO')

        return self.strategy.authenticate(*args, **kwargs)

    def get_user_details(self, response):
        email = response.get('email', None)
        details = {
            'email': email,
        }
        return details

    def get_key_and_secret(self):
        print("::::::::::::::GET KEY & SECRET:::::::::::::::")
        headers = {
            'kid': settings.SOCIAL_AUTH_APPLE_ID_KEY,
            'alg': 'ES256'
        }
        print('::::::::PRINTING HEADERS:::::::')
        print(headers)
        payload = {
            'iss': settings.SOCIAL_AUTH_APPLE_ID_TEAM,
            'iat': timezone.now() - datetime.timedelta(days=1),
            'exp': timezone.now() + datetime.timedelta(days=180),
            'aud': 'https://appleid.apple.com',
            'sub': settings.SOCIAL_AUTH_APPLE_ID_CLIENT,
        }
        print(":::::::::::PRINTING PAYLOAD::::::::::::::::")
        print(payload)

        client_secret = jwt.encode(
            payload,
            settings.SOCIAL_AUTH_APPLE_ID_KEY,
            # algorithm='ES256',
            headers=headers
        ).decode("utf-8")

        print('::::::::::::PRINTING CLIENT SECRET::::::::::::::::')
        print(client_secret)

        return client_secret


@csrf_exempt
@permission_classes([AllowAny])
def token_conversion(request, *args, **kwargs):
    print(':::::::::::::PRINTING REQUEST::::::::::::')
    json_response = {
        'name': 'Nadim'
    }
    AppleOAuth2.do_auth(AppleOAuth2, request, *args, **kwargs)
    return JsonResponse(json_response)


@csrf_exempt
@permission_classes([AllowAny])
def apple_login(request, *args, **kwargs):
    user_id = request.POST.get('user_id')
    code = request.POST.get("code")
    res = requests.get("http://localhost:60061/apple-login?code=" + code)
    if res.status_code == 200 and res.text.startswith("{"):
        res_text = json.loads(res.text)
        return JsonResponse(res_text)
    else:
        return JsonResponse({"success": False})


def create_account(email, first_name=None, last_name=None):
    user = User.objects.filter(email=email).first()
    if user:
        print("USER EXIST")
    else:
        User.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            invited_by=None,
            photo=None,
            photo_thumb=None,
            is_active=True,
            is_team_admin=True
        )
