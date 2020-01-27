import json

import requests
from django.http import JsonResponse
from rest_framework.decorators import api_view

from api.models import UserFirebase


@api_view(['GET'])
def send_update_notification(request):
    length = 0;
    fcm_users = UserFirebase.objects.all()
    for fcm_user in fcm_users:
        length = length + 1
        data = {'to': fcm_user.firebase_token,
                'data': {
                    'title': 'Update',
                    'body': request.GET.get("message"),
                    'icon': '',
                    'id': '2',
                    'data': '{"open":"SplashActivity","data":[{"id","1"}]}',
                }}
        headers = {'Content-type': 'application/json', 'Authorization': 'key=AIzaSyB9XX-kyinohetvgBdn0KnLHb915_TgdG8'}
        requests.post(url="https://fcm.googleapis.com/fcm/send", data=json.dumps(data), headers=headers)
    return JsonResponse({'status': True, "data": length, "message": "success"})
