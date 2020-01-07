from django.http import JsonResponse
from rest_framework.decorators import api_view
from notifications.models import Notification as Notifier
from api.serializers import *


@api_view(['GET'])
def get_all_notifications(request):
    user = User.objects.get(id=request.user.id)
    notifications = Notifier.objects.filter(actor_object_id = user.id)
    notification_serializer = NotificationSerializer(notifications,many = True)
    return JsonResponse(notification_serializer.data, safe = False)