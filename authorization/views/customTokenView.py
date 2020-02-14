import json
from django.http.response import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic.base import View
from oauth2_provider.models import get_access_token_model
from oauth2_provider.settings import oauth2_settings
from oauth2_provider.signals import app_authorized
from oauth2_provider.views.mixins import OAuthLibMixin
from api.models import *
from authorization.views import *
from authorization.views.checkSubscription import CheckSubscription as cs
from authorization.views.downgradeProfile import DowngradeProfile as dp

@method_decorator(csrf_exempt, name="dispatch")
class CustomTokenView(OAuthLibMixin, View):
    """
    Implements an endpoint to provide access tokens

    The endpoint is used in the following flows:
    * Authorization code
    * Password
    * Client credentials
    """
    server_class = oauth2_settings.OAUTH2_SERVER_CLASS
    validator_class = oauth2_settings.OAUTH2_VALIDATOR_CLASS
    oauthlib_backend_class = oauth2_settings.OAUTH2_BACKEND_CLASS

    @method_decorator(sensitive_post_parameters("password"))
    def post(self, request, *args, **kwargs):
        print(":::::::::SIGN IN IS WORKING:::::::::::::::::")
        url, headers, body, status = self.create_token_response(request)
        if status == 200:
            access_token = json.loads(body).get("access_token")
            if access_token is not None:
                token = get_access_token_model().objects.get(
                    token=access_token)
                app_authorized.send(
                    sender=self, request=request,
                    token=token)
        response = HttpResponse(content=body, status=status)

        for k, v in headers.items():
            response[k] = v
        print('::::::::::USER ID :::::::::::::::::')
        user = User.objects.get(id=token.user.id)
        upgrade_profile = UpgradeProfile.objects.filter(user=user).first()
        if upgrade_profile:
            if upgrade_profile.subscriptionId != None:
                print(upgrade_profile.subscriptionId)
                if not cs.get_subscription_status(self,upgrade_profile.subscriptionId):
                    # IF SUBSCRIPTION STATUS IS FALSE DOWNGRADE PROFILE
                    dp.downgrade(self,upgrade_profile, user)



        else:
            print("::::::::::INVALID USER::::::::::")
        return response
