import datetime

from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework import viewsets, status, pagination
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.utils import json
import time
from houzes_api import settings
from django.forms.models import model_to_dict

from api.serializers import *
from api.models import *
from houzes_api.util.file_upload import file_upload

class CustomPagination(pagination.PageNumberPagination):
    def get_paginated_response(self, data):
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.page.paginator.count,
            'results': data,
        })


class HistoryViewSet(viewsets.ModelViewSet):
    queryset = History.objects.all()
    serializer_class = HistorySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    ordering = ['-id']

    def retrieve(self, request, *args, **kwargs):
        history_id = self.kwargs['pk']
        history = History.objects.get(id=history_id)
        historyDetails = HistoryDetail.objects.filter(history=history)
        ids = list(historyDetails.values_list('property', flat=True))
        property = list(Property.objects.filter(id__in=ids)[:10])
        listPropertiesSerializer = PropertySerializer(property,many=True)

        data = {
            'id' : history.id,
            'start_point_latitude' : history.start_point_latitude,
            'start_point_longitude' : history.end_point_longitude,
            "end_point_latitude": history.end_point_latitude,
            "end_point_longitude": history.end_point_longitude,
            "image": history.image,
            "start_time": history.start_time,
            "end_time": history.end_time,
            "polylines": history.polylines,
            "length": history.length,
            "user": history.user.id,
            "property_count":  HistoryDetail.objects.filter(history = history.id).count(),
            "property" : listPropertiesSerializer.data,
            "created_at": history.created_at,
            "updated_at":history.updated_at,
        }
        return Response(data)

    def create(self, request, *args, **kwargs):
        status = False
        data = {}
        message = ""
        try:
            start_point_latitude = request.data['start_point_latitude']
            start_point_longitude = request.data['start_point_longitude']
            end_point_latitude = request.data['end_point_latitude']
            end_point_longitude = request.data['end_point_longitude']
            start_time = request.data['start_time']
            end_time = request.data['end_time']
            polylines = request.data['polylines']
            length = request.data['length']
        except:
            start_point_latitude = request.body['start_point_latitude']
            start_point_longitude = request.body['start_point_longitude']
            end_point_latitude = request.body['end_point_latitude']
            end_point_longitude = request.body['end_point_longitude']
            start_time = request.body['start_time']
            end_time = request.body['end_time']
            polylines = request.body['polylines']
            length = request.body['length']

        user_id = request.user.id
        user = User.objects.get(id=user_id)
        # polylines = json.loads(polylines)

        if 'image' in request.FILES:
            file = request.FILES['image']
            file_path = "photos/history/{}/{}".format(str(user_id), str(time.time()) + '.jpg')
            s3_url = "https://s3.{}.amazonaws.com/{}/{}".format(settings.AWS_REGION, settings.S3_BUCKET_NAME, file_path)
            file_upload(file, file_path)

        try :
            history = History(start_point_latitude=start_point_latitude,start_point_longitude = start_point_longitude,end_point_latitude = end_point_latitude, end_point_longitude = end_point_longitude,start_time=start_time,end_time=end_time,polylines=polylines,user=user,image=s3_url)
            history.save()
            historySerializer = HistorySerializer(history)
        except:
            message = 'Error uploading visited place'
            return Response({'status': status, 'data': data, 'message': message})
        status = True
        data = historySerializer.data
        message = "Successfully uploaded visited place"
        return Response({'status': status, 'data': data, 'message': message})

    @action(detail=False,methods=['POST'],url_path='start-driving')
    def start_driving(self,request,*args,**kwargs):
        status = False
        data = {}
        message = ""
        try:
            start_point_latitude = request.data['start_point_latitude']
            start_point_longitude = request.data['start_point_longitude']
        except:
            start_point_latitude = request.body['start_point_latitude']
            start_point_longitude = request.body['start_point_longitude']
        start_time = datetime.datetime.now()
        user_id = request.user.id
        user = User.objects.get(id=user_id)
        try :
            history = History(start_point_latitude=start_point_latitude,start_point_longitude = start_point_longitude,start_time=start_time,user=user)
            history.save()
            historySerializer = HistorySerializer(history)
        except:
            message = 'Error start diriving'
            return Response({'status': status, 'data': data, 'message': message})
        status = True
        data = historySerializer.data
        message = "Started driving"
        return Response({'status': status, 'data': data, 'message': message})

    @action(detail=False,methods=['POST'],url_path='(?P<pk>[\w-]+)/end-driving')
    def end_driving(self,request,*args,**kwargs):
        history_id = kwargs['pk']
        status = False
        data = {}
        message = ""
        try:
            end_point_latitude = request.data['end_point_latitude']
            end_point_longitude = request.data['end_point_longitude']
            polylines = request.data['polylines']
            length = request.data['length']
        except:
            end_point_latitude = request.body['end_point_latitude']
            end_point_longitude = request.body['end_point_longitude']
            polylines = request.body['polylines']
            length = request.body['length']
        end_time = datetime.datetime.now()
        user_id = request.user.id
        user = User.objects.get(id=user_id)
        # polylines = json.loads(polylines)
        # if isinstance(polylines[0],str):
        #     obj = []
        #     for objString in polylines:
        #         obj.append(json.loads(objString))
        #     polylines = obj
        if 'image' in request.FILES:
            file = request.FILES['image']
            file_path = "photos/history/{}/{}".format(str(user_id), str(time.time()) + '.jpg')
            s3_url = "https://s3.{}.amazonaws.com/{}/{}".format(settings.AWS_REGION, settings.S3_BUCKET_NAME, file_path)
            file_upload(file, file_path)

        history = History.objects.get(id = history_id)
        history.end_point_latitude = end_point_latitude
        history.end_point_longitude = end_point_longitude
        history.end_time = end_time
        history.polylines = polylines
        history.image = s3_url
        history.length = length
        try:
            history.save()
            historySerializer = HistorySerializer(history)
        except:
            message = 'Error end diriving'
            return Response({'status': status, 'data': data, 'message': message})
        status = True
        data = historySerializer.data
        message = "Driving ended"
        return Response({'status': status, 'data': data, 'message': message})

    @action(detail=False,methods=['GET'],url_path='complete-drives')
    def get_complete_drives(self,request,*args,**kwargs):
        page_size = request.GET.get('limit')
        user = User.objects.get(id = request.user.id)
        history = History.objects.filter(~Q(end_time=None), user=user).order_by('-id')

        paginator = CustomPagination()
        if page_size:
            paginator.page_size = page_size
        else:
            paginator.page_size = 10
        # paginator.offset = 0
        result_page = paginator.paginate_queryset(history, request)
        serializer = HistorySerializer(result_page, many=True)
        return paginator.get_paginated_response(data=serializer.data)

    @action(detail=False,methods=['GET'],url_path='(?P<id>[\w-]+)/properties')
    def get_properties_by_history(self,request,*args,**kwargs):
        page_size = request.GET.get('limit')
        history_id = self.kwargs['id']
        history = History.objects.get(id=history_id)
        historyDetails = HistoryDetail.objects.filter(history=history)
        ids = list(historyDetails.values_list('property', flat=True))
        property = list(Property.objects.filter(id__in=ids))

        paginator = CustomPagination()
        if page_size:
            paginator.page_size = page_size
        else:
            paginator.page_size = 10
        result_page = paginator.paginate_queryset(property, request)
        serializer = PropertySerializer(result_page, many=True)
        return paginator.get_paginated_response(data=serializer.data)

    @action(detail=False,methods=['GET'],url_path='user')
    def get_property_list_by_user(self,request,*args,**kwargs):
        page_size = request.GET.get('limit')
        user = User.objects.get(id = request.user.id)
        history = History.objects.filter(user = user)
        paginator = CustomPagination()
        if page_size:
            paginator.page_size = page_size
        else:
            paginator.page_size = 10
        result_page = paginator.paginate_queryset(history, request)
        serializer = HistorySerializer(result_page, many=True)
        return paginator.get_paginated_response(data=serializer.data)
