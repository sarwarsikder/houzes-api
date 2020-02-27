import json

import requests
from django.contrib.auth.hashers import check_password
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from api.models import User


@api_view(['POST'])
@permission_classes([AllowAny])
def get_token(request):
    try:
        email = request.data["username"]
        password = request.data["password"]

        user = User.objects.filter(email=email)
        if len(user) >= 1 and check_password(password, user[0].password):
            if user[0].is_active == True:
                url="https://"+request.META['HTTP_HOST'] + "/o/token/"
                res = requests.post(url=url, data=request.data)
                if res.status_code >= 200 & res.status_code < 300:
                    data = json.loads(res.text)
                    return JsonResponse({'status': True, "data": data, "message": "Success"})
                else:
                    return JsonResponse({'status': False, "data": None,
                                         "message": "Your account is in critical situation. Contact with support team"})
            else:
                return JsonResponse({'status': False, "data": None, "message": "Your account is not active"})
        else:
            return JsonResponse({'status': False, "data": None, "message": "Email or password not match"})
    except:
        return JsonResponse({'status': False, "data": None, "message": "Something went wrong"})
