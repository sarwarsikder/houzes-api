from django.db.models import Q
from django.http import JsonResponse
from rest_framework import pagination
from rest_framework.response import Response
from rest_framework.decorators import api_view
from notifications.models import Notification as Notifier
from api.serializers import *

class CustomPagination(pagination.PageNumberPagination):
    def get_paginated_response(self, data):
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.page.paginator.count,
            'results': data,
        })

@api_view(['GET'])
def get_all_notifications(request):
    user = User.objects.get(id=request.user.id)
    notifications = Notifier.objects.none()
    if user.is_admin == True:
        members = User.objects.filter(Q(Q(invited_by=user.id)|Q(id=user.id)))
        notifications = Notifier.objects.filter(recipient__in=members)
    else :
        notifications = Notifier.objects.filter(recipient = user)
    page_size = request.GET.get('limit')
    paginator = CustomPagination()
    if page_size:
        paginator.page_size = page_size
    else:
        paginator.page_size = 10
    result_page = paginator.paginate_queryset(notifications, request)
    serializer = NotificationSerializer(result_page, many=True)
    return paginator.get_paginated_response(data=serializer.data)

def querySet_to_list(qs):
    """
    this will return python list<dict>
    """
    return [dict(q) for q in qs]