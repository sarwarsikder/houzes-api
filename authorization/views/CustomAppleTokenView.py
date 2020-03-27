import datetime
import re
import traceback

import oauth2_provider
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny

from api.models import *
from authorization.views import AppleEmail


# from social_core.backends.oauth import BaseOAuth2
# from social_core.utils import handle_http_errors


# class AppleOAuth2(BaseOAuth2):
#     """apple authentication backend"""
#
#     name = 'apple'
#     ACCESS_TOKEN_URL = 'https://appleid.apple.com/auth/token'
#     SCOPE_SEPARATOR = ','
#     ID_KEY = 'uid'
#     access_token = ''
#
#     # @csrf_exempt
#     @handle_http_errors
#     # @api_view(['POST'])
#     # @permission_classes([AllowAny])
#     # @staticmethod
#     def do_auth(self, request, *args, **kwargs):
#         """
#         Finish the auth process once the access_token was retrieved
#         Get the email from ID token received from apple
#         """
#         # print(request.body)
#         # body_unicode = request.body.decode('utf-8')
#         # print(body_unicode)
#         # body = json.loads(body_unicode)
#         # print(body)
#         # access_token = body['access_token']
#         access_token = 'c0b268acca7e64c04a1a9074dbbe28718.0.ntqv.K3_ckZWPd4yGTrgkRzm7ew'
#         # access_token = 'eyJraWQiOiI4NkQ4OEtmIiwiYWxnIjoiUlMyNTYifQ.eyJpc3MiOiJodHRwczovL2FwcGxlaWQuYXBwbGUuY29tIiwiYXVkIjoiY29tLnJhLmhvdXplcy1pb3MiLCJleHAiOjE1ODUwNjgyNTcsImlhdCI6MTU4NTA2NzY1Nywic3ViIjoiMDAwMzA1LjgyODYzZjliYTBkMjRmNTZhM2VlOTRmOGI0YWZhMzFmLjA5NTkiLCJjX2hhc2giOiJJdDB2cEx6WU9Ha0p3d2NwSmdmRWhBIiwiZW1haWwiOiJ3b3Jrc3BhY2VpbmZvdGVjaEBnbWFpbC5jb20iLCJlbWFpbF92ZXJpZmllZCI6InRydWUiLCJhdXRoX3RpbWUiOjE1ODUwNjc2NTcsIm5vbmNlX3N1cHBvcnRlZCI6dHJ1ZX0.bNRvdAxsNYa0ccAFaDm1ooPw_8gb9wmiUdaxNvDeEIjMWUjR5pwgj3BiYIOYeK3Jg7NXiNWN3D4esT6FwdtwPqEo1IkUKD-FW-KM4R5ChFKA7owE8C5bKvudYFUBgoxthysFe7BaTQsrvKJNkJYSh_slgdT7OfoZZm-TxMNKoI8FuXLwu5oSzXIa5s1KRwir4qQXlXUpRRif1T5kX-iXRP_pNeakn7bmzgjn2OtA_BlYDxwNhkjzqSgrkEFdcppvxTMAhsBpQJhWoUm0eO2g0SPRmBPKkNxbieg_f5HJlmhnY_YS1ntMTcM7d_A2ybO8uxPLVoxdCt-wRTfrPBYVug'
#         print(':::::::::::::::::::PRINTING ACCESS TOKEN:::::::::::::::::::')
#         print(access_token)
#         response_data = {}
#         client_id = settings.SOCIAL_AUTH_APPLE_ID_CLIENT
#         client_secret = AppleOAuth2.get_key_and_secret(self)
#
#         headers = {'content-type': "application/x-www-form-urlencoded"}
#         data = {
#             'client_id': client_id,
#             'client_secret': client_secret,
#             'code': access_token,
#             'grant_type': 'authorization_code',
#             'redirect_uri': 'https://houzes.com/'
#         }
#
#         res = requests.post(AppleOAuth2.ACCESS_TOKEN_URL, data=data, headers=headers)
#         print(res)
#         response_dict = res.json()
#         print('::::::::::::::::APPLE RESPONSE:::::::::::::::')
#         print(response_data)
#         id_token = response_dict.get('id_token', None)
#
#         if id_token:
#             decoded = jwt.decode(id_token, '', verify=False)
#             response_data.update({'email': decoded['email']}) if 'email' in decoded else None
#             response_data.update({'uid': decoded['sub']}) if 'sub' in decoded else None
#
#         response = kwargs.get('response') or {}
#         response.update(response_data)
#         response.update({'access_token': access_token}) if 'access_token' not in response else None
#
#         kwargs.update({'response': response, 'backend': self})
#         print('KAM KORE AI PORJONTO')
#
#         return self.strategy.authenticate(*args, **kwargs)
#
#     def get_user_details(self, response):
#         email = response.get('email', None)
#         details = {
#             'email': email,
#         }
#         return details
#
#     def get_key_and_secret(self):
#         print("::::::::::::::GET KEY & SECRET:::::::::::::::")
#         headers = {
#             'kid': settings.SOCIAL_AUTH_APPLE_ID_KEY,
#             'alg': 'ES256'
#         }
#         print('::::::::PRINTING HEADERS:::::::')
#         print(headers)
#         payload = {
#             'iss': settings.SOCIAL_AUTH_APPLE_ID_TEAM,
#             'iat': timezone.now() - datetime.timedelta(days=1),
#             'exp': timezone.now() + datetime.timedelta(days=180),
#             'aud': 'https://appleid.apple.com',
#             'sub': settings.SOCIAL_AUTH_APPLE_ID_CLIENT,
#         }
#         print(":::::::::::PRINTING PAYLOAD::::::::::::::::")
#         print(payload)
#
#         client_secret = jwt.encode(
#             payload,
#             settings.SOCIAL_AUTH_APPLE_ID_KEY,
#             # algorithm='ES256',
#             headers=headers
#         ).decode("utf-8")
#
#         print('::::::::::::PRINTING CLIENT SECRET::::::::::::::::')
#         print(client_secret)
#
#         return client_secret
#
#
# @csrf_exempt
# @permission_classes([AllowAny])
# def token_conversion(request, *args, **kwargs):
#     print(':::::::::::::PRINTING REQUEST::::::::::::')
#     json_response = {
#         'name': 'Nadim'
#     }
#     AppleOAuth2.do_auth(AppleOAuth2, request, *args, **kwargs)
#     return JsonResponse(json_response)


@csrf_exempt
@permission_classes([AllowAny])
def apple_jwt(request, *args, **kwargs):
    user_id = request.GET.get('user_id')
    if user_id != None:
        if len(AppleUserId.objects.filter(user_id=user_id)) > 0:
            tuser = AppleUserId.objects.filter(user_id=user_id)[0]
            tuser.jwt_token = AppleEmail.get_one_random_text(20)
            tuser.save()
        else:
            tuser = AppleUserId()
            tuser.user_id = user_id
            tuser.code = ""
            tuser.jwt_token = AppleEmail.get_one_random_text(20)
            while True:
                te = AppleEmail.generate_random_emails()
                if len(User.objects.filter(email=te)) == 0:
                    tuser.email = te
                    break;
            tuser.save()
        return JsonResponse({"status": True, "data": tuser.jwt_token, "message": "Success"})
    return JsonResponse({"status": False, "data": None, "message": "Invalid user data"})


@csrf_exempt
@permission_classes([AllowAny])
def apple_login(request, *args, **kwargs):
    res_message = "Something went wrong"
    try:
        code = request.POST.get('code')
        user_id = request.POST.get('user_id')
        jwt_token = request.POST.get('jwt_token')
        user_type = request.POST.get('type')
        if user_id != None:
            aui = AppleUserId.objects.get(user_id=user_id)
            if aui.jwt_token == jwt_token:
                aui.code = code
                aui.save()
                if user_type == "UP":
                    return JsonResponse(create_account(aui.email))
                elif user_type == "IN":
                    user = User.objects.filter(email=aui.email).first()
                    if not user:
                        res_message = "User doesn't exist"
                    else:
                        return JsonResponse(create_account(aui.email))
            else:
                res_message = "Invalid credentials"
    except Exception as ex:
        print(str(ex))
        res_message = "User not found"
    return JsonResponse({"status": False, "data": None, "message": res_message})


def create_account(email, first_name='Unknown', last_name='User'):
    try:
        user = User.objects.filter(email=email).first()
        application = oauth2_provider.models.get_application_model().objects.all().first()
        if not user:
            print("::::::::::::USER DOESN'T EXIST::::::::::::")
            user = User.objects.create(
                first_name='N/A',
                last_name='',
                email=email,
                password=make_password(generate_shortuuid()),
                invited_by=None,
                photo=None,
                photo_thumb=None,
                is_active=True,
                is_team_admin=True
            )

        access_token = oauth2_provider.models.get_access_token_model().objects.create(
            token=generate_shortuuid(),
            expires=timezone.now() + datetime.timedelta(days=7),
            scope='read write groups introspection',
            application_id=application.id,
            user_id=user.id,
            created=timezone.now(),
            updated=timezone.now()
        )
        data = {
            'access_token': access_token.token,
            'expires_in': str(access_token.expires),
            'token_type': 'Bearer',
            'scope': access_token.scope,
            'refresh_token': None
        }
        return {'status': True, 'data': data, 'message': 'log in successful'}
    except Exception as exc:
        print(':::::::::::::EXCEPTION OCCURED:::::::::::::')
        print('exception :' + str(exc))
        print(traceback.print_exc())
        return {'status': False, 'data': None, 'message': 'Invalid credentials'}


# def subscription_checking(user):
#     upgrade_profile = UpgradeProfile.objects.filter(user=user).first()
#
#     try:
#         print('::::::::::USER ID :::::::::::::::::')
#         if upgrade_profile:
#             if upgrade_profile.subscriptionId != None:
#                 print(upgrade_profile.subscriptionId)
#                 if not cs.get_subscription_status(AppleOAuth2, upgrade_profile.subscriptionId):
#                     # IF SUBSCRIPTION STATUS IS FALSE DOWNGRADE PROFILE
#                     dp.downgrade(AppleOAuth2, upgrade_profile, user)
#
#
#
#         else:
#             print("::::::::::INVALID USER::::::::::")
#     except:
#         print('EXCEPTION OCCURED WHILE CHECKING SUBSCRIPTION')
#
#     try:
#         print('::::::::::::::CHECKING FOR EXPIRATION DATE::::::::::::::::')
#         if upgrade_profile:
#             if upgrade_profile.expire_at != None:
#                 utc = pytz.UTC
#                 if utc.localize(datetime.datetime.now()) >= upgrade_profile.expire_at:
#                     dp.downgrade(AppleOAuth2, upgrade_profile, user)
#
#     except:
#         print(traceback.print_exc())


# for validating an Email
def is_email_vaild(email):
    regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
    if (re.search(regex, email)):
        return True
    else:
        return False
