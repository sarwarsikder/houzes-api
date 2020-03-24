import json

import jwt
import requests
import datetime

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from oauth2_provider.views.mixins import OAuthLibMixin
from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from houzes_api import settings
from django.utils import timezone
from social_core.backends.oauth import BaseOAuth2
from social_core.utils import handle_http_errors
from braces.views import CsrfExemptMixin
from django.utils import timezone


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
        access_token = 'c10439e13dfed4538bb99e75c0a109749.0.ntqv.pYksPFnbJABytXC9gf3iQw'
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
            'kid': settings.SOCIAL_AUTH_APPLE_ID_KEY
        }
        print('::::::::PRINTING HEADERS:::::::')
        print(headers)
        payload = {
            'iss': settings.SOCIAL_AUTH_APPLE_ID_TEAM,
            'iat': timezone.now(),
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
