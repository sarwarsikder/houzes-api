import datetime
import json
import traceback

import pytz
import requests
from braces.views import CsrfExemptMixin
from django.http.response import JsonResponse
from oauth2_provider.models import AccessToken
from oauth2_provider.settings import oauth2_settings
from oauth2_provider.views.mixins import OAuthLibMixin
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_social_oauth2.oauth2_backends import KeepRequestCore
from rest_framework_social_oauth2.oauth2_endpoints import SocialTokenServer
from authorization.views.checkSubscription import CheckSubscription as cs
from authorization.views.downgradeProfile import DowngradeProfile as dp
from api.models import UpgradeProfile,User


class CustomConvertTokenView2(CsrfExemptMixin, OAuthLibMixin, APIView):
    """
    Implements an endpoint to convert a provider token to an access token

    The endpoint is used in the following flows:

    * Authorization code
    * Client credentials
    """
    server_class = SocialTokenServer
    validator_class = oauth2_settings.OAUTH2_VALIDATOR_CLASS
    oauthlib_backend_class = KeepRequestCore
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        print("::::::::::SOCIAL LOGIN IS WORKING::::::::::::::::::")
        token = request.data['token']
        user = None
        res = { "status" : False, "data" : None, "message" : ""}

        if request.data['backend']=='google-oauth2':
            result = requests.get("https://www.googleapis.com/oauth2/v3/userinfo?access_token=" + token)
            if result.status_code == 200:
                text = json.loads(result.text)
                user = User.objects.filter(email=text['email']).first()
        elif request.data['backend']=='facebook':
            result = requests.get("https://graph.facebook.com/me?fields=id,name,email&access_token=" + token)
            if result.status_code == 200:
                text = json.loads(result.text)
                print(text['email'])
                user = User.objects.filter(email=text['email']).first()
        else:
            print('NOTHING HAPPENED')

        if not user:
            res["message"] = "User does not exist"
            return JsonResponse(res)
        # Use the rest framework `.data` to fake the post body of the django request.
        request._request.POST = request._request.POST.copy()
        for key, value in request.data.items():
            request._request.POST[key] = value
        # print(request.backend.do_auth(request.data.))
        url, headers, body, status = self.create_token_response(request._request)
        response = Response(data=json.loads(body), status=status)
        for k, v in headers.items():
            response[k] = v

        if status==200:
            user = AccessToken.objects.filter(token=response.data['access_token']).first().user
            upgrade_profile = UpgradeProfile.objects.filter(user=user).first()

            try:
                if upgrade_profile:
                    print('::::::::::IF UPGRADE PROFILE:::::::::::::')
                    if upgrade_profile.subscriptionId != None:
                        print(upgrade_profile.subscriptionId)
                        if not cs.get_subscription_status(self, upgrade_profile.subscriptionId):
                            # IF SUBSCRIPTION STATUS IS FALSE DOWNGRADE PROFILE
                            dp.downgrade(self, upgrade_profile, user)

                else:
                    print("::::::::::INVALID USER::::::::::")
            except:
                print('EXCEPTION OCCURED WHILE CHECKING SUBSCRIPTION')
            try:
                print('::::::::::::::CHECKING FOR EXPIRATION DATE::::::::::::::::')
                if upgrade_profile:
                    if upgrade_profile.expire_at != None:
                        utc = pytz.UTC
                        if utc.localize(datetime.datetime.now()) >= upgrade_profile.expire_at:
                            dp.downgrade(self, upgrade_profile, user)

            except Exception as exc:
                print(':::::::::::::EXCEPTION OCCURED WHILE CHECKING EXPIRATION DATE:::::::::::::')
                print('exception :' + str(exc))
                print(traceback.print_exc())
            print(response)
            res["status"] = True
            res["data"] = response.data
            res["message"] = "Sign in successful"
        else:
            res["status"] = False
            res['data'] = json.loads(body)
            res['message'] = 'Error signing in'
        return JsonResponse(res)
