import datetime

import pytz
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from notifications.signals import notify
from rest_framework import filters
from rest_framework import viewsets, status, pagination
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.utils import json
import time

from api.views.user_list_view import UserListViewSet
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

class HistoriesFilterPagination(pagination.PageNumberPagination):
    def get_paginated_response(self, data, polylines, property):
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.page.paginator.count,
            'results': data,
            'polylines': polylines,
            'property' : property
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
        property = list(Property.objects.filter(id__in=ids))
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
            try:
                # user = User.objects.get(id = request.user.id)
                notify.send(user, recipient=user, verb='started driving', action_object=history)
            except:
                print('Error in notification')
        except:
            message = 'Error start diriving'
            return Response({'status': status, 'data': data, 'message': message})
        status = True
        data = historySerializer.data
        message = "Start Driving. Click & hold any property to add to list"
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
        history = History.objects.get(id=history_id)
        if 'image' in request.FILES:
            file = request.FILES['image']
            file_path = "photos/history/{}/{}".format(str(user_id), str(time.time()) + '.jpg')
            s3_url = "https://s3.{}.amazonaws.com/{}/{}".format(settings.AWS_REGION, settings.S3_BUCKET_NAME, file_path)
            file_upload(file, file_path)
            history.image = s3_url

        history.end_point_latitude = end_point_latitude
        history.end_point_longitude = end_point_longitude
        history.end_time = end_time
        history.polylines = polylines
        history.length = length
        try:
            history.save()
            historySerializer = HistorySerializer(history)
            try:
                # user = User.objects.get(id = request.user.id)
                notify.send(user, recipient=user, verb='stopped driving', action_object=history)
            except:
                print('Error in notification')
        except:
            message = 'Error end diriving'
            return Response({'status': status, 'data': data, 'message': message})
        status = True
        data = historySerializer.data
        message = "Driving ended"
        return Response({'status': status, 'data': data, 'message': message})

    @action(detail=False,methods=['POST'],url_path='(?P<pk>[\w-]+)/upload-driving-image')
    def upload_driving_image(self,request,*args,**kwargs):
        history = History.objects.get(id = kwargs['pk'])
        user_id = request.user.id
        try:
            if 'image' in request.FILES:
                file = request.FILES['image']
                file_path = "photos/history/{}/{}".format(str(user_id), str(time.time()) + '.jpg')
                s3_url = "https://s3.{}.amazonaws.com/{}/{}".format(settings.AWS_REGION, settings.S3_BUCKET_NAME, file_path)
                file_upload(file, file_path)
                history.image = s3_url
                history.save()
                status = True
                data = HistorySerializer(history).data
                message = 'History image upload successfull'
            else:
                status = False
                data = {}
                message = 'Please upload a image'
        except:
            status = False
            data = {}
            message = 'Error uploading image'
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
    def get_history_list_by_user(self,request,*args,**kwargs):
        page_size = request.GET.get('limit')
        user = User.objects.get(id = request.user.id)
        history = History.objects.filter(~Q(end_time=None),user = user).order_by('-id')
        paginator = CustomPagination()
        if page_size:
            paginator.page_size = page_size
        else:
            paginator.page_size = 10
        result_page = paginator.paginate_queryset(history, request)
        serializer = HistorySerializer(result_page, many=True)
        return paginator.get_paginated_response(data=serializer.data)

    @action(detail=False,methods=['GET'],url_path='team')
    def get_history_by_team(self,request,*args,**kwargs):
        page_size = request.GET.get('limit')
        users = User.objects.filter(invited_by = request.user.id)
        history = History.objects.filter(~Q(end_time=None),user__in = users).order_by('-id')
        paginator = CustomPagination()
        if page_size:
            paginator.page_size = page_size
        else:
            paginator.page_size = 10
        result_page = paginator.paginate_queryset(history, request)
        serializer = HistorySerializer(result_page, many=True)
        return paginator.get_paginated_response(data=serializer.data)


    @action(detail=False,methods=['GET'],url_path='team/visited-properties')
    def get_team_visited_properties(self,request,*args,**kwargs):
        page_size = request.GET.get('limit')
        users = User.objects.filter(invited_by=request.user.id)
        histories = History.objects.filter(~Q(end_time=None), user__in=users).order_by('-id')
        history_details = HistoryDetail.objects.filter(history__in=histories).values('property_id')
        properties = Property.objects.filter(id__in=history_details)
        paginator = CustomPagination()
        if page_size:
            paginator.page_size = page_size
        else:
            paginator.page_size = 10
        result_page = paginator.paginate_queryset(properties, request)
        serializer = PropertySerializer(result_page, many=True)
        return paginator.get_paginated_response(data=serializer.data)

    @action(detail=False,methods=['GET'],url_path='user/visited-properties')
    def get_user_visited_properties(self,request,*args,**kwargs):
        page_size = request.GET.get('limit')
        user = User.objects.get(id=request.user.id)
        histories = History.objects.filter(~Q(end_time=None), user=user).order_by('-id')
        print(histories)
        history_details = HistoryDetail.objects.filter(history__in=histories).values('property_id')
        print(history_details)
        properties = Property.objects.filter(id__in=history_details)
        print(properties)
        paginator = CustomPagination()
        if page_size:
            paginator.page_size = page_size
        else:
            paginator.page_size = 10
        result_page = paginator.paginate_queryset(properties, request)
        serializer = PropertySerializer(result_page, many=True)
        return paginator.get_paginated_response(data=serializer.data)

    @action(detail=False, methods=['POST'], url_path='(?P<id>[\w-]+)/add-property')
    def history_add_property(self, request, *args, **kwargs):
        history_id = kwargs['id']
        history = History.objects.get(id = history_id)
        street = ""
        city = ""
        state = ""
        zip = ""
        cad_acct = ""
        gma_tag = None
        latitude = None
        longitude = None
        property_tags = []
        owner_info =  []
        user_list = None

        status = False
        data = {}
        message =""

        try:
            if 'street' in request.data:
                street = request.data['street']
            if 'city' in request.data:
                city = request.data['city']
            if 'state' in request.data:
                state = request.data['state']
            if 'zip' in request.data:
                zip = request.data['zip']
            if 'cad_acct' in request.data:
                cad_acct = request.data['cad_acct']
            if 'gma_tag' in request.data:
                gma_tag = request.data['gma_tag']
            if 'latitude' in request.data:
                latitude = request.data['latitude']
            if 'longitude' in request.data:
                longitude = request.data['longitude']
            if 'property_tags' in request.data:
                property_tags = request.data['property_tags']
            if 'owner_info' in request.data:
                owner_info = request.data['owner_info']
            if 'user_list' in request.data:
                user_list = request.data['user_list']
                user_list = UserList.objects.get(id=user_list)

        except:
            if 'street' in request.body:
                street = request.body['street']
            if 'city' in request.body:
                city = request.body['city']
            if 'state' in request.body:
                state = request.body['state']
            if 'zip' in request.body:
                zip = request.body['zip']
            if 'cad_acct' in request.body:
                cad_acct = request.body['cad_acct']
            if 'gma_tag' in request.body:
                gma_tag = request.body['gma_tag']
            if 'latitude' in request.body:
                latitude = request.body['latitude']
            if 'longitude' in request.body:
                longitude = request.body['longitude']
            if 'property_tags' in request.body:
                property_tags = request.body['property_tags']
            if 'owner_info' in request.body:
                owner_info = request.body['owner_info']
            if 'user_list' in request.body:
                user_list = request.body['user_list']
                user_list = UserList.objects.get(id=user_list)
        try:
            property = Property(street=street,city=city,state=state,zip=zip,cad_acct=cad_acct,gma_tag=gma_tag,latitude=latitude,longitude=longitude,property_tags=property_tags,owner_info=owner_info,user_list=user_list)
            property.save()

            historyDetails = HistoryDetail.objects.create(history=history,property=property)
            historyDetails.save()

            status = True
            data = PropertySerializer(property).data
            message = "Property added successfully to this drive"
        except:
            status = False
            data = {}
            message = "Failed to create property"
        return Response({'status': status, 'data' : data, 'message' : message})


    @action(detail=False,methods=['GET'],url_path='member')
    def get_history_list_by_member(self,request,*args,**kwargs):
        try :
            members = [int(x) for x in request.GET.get('members').split(',')]
        except:
            return Response({'status': False,'message': 'Please provide a valid data'})
        page_size = request.GET.get('limit')
        history = History.objects.filter(~Q(end_time=None),user__in = members).order_by('-id')
        paginator = CustomPagination()
        if page_size:
            paginator.page_size = page_size
        else:
            paginator.page_size = 10
        result_page = paginator.paginate_queryset(history, request)
        serializer = HistorySerializer(result_page, many=True)
        return paginator.get_paginated_response(data=serializer.data)


    @action(detail=False,methods=['GET'],url_path='dashboard/team/visited-properties')
    def get_first_ten_team_visited_properties(self,request,*args,**kwargs):
        page_size = request.GET.get('limit')
        users = User.objects.filter(invited_by=request.user.id)
        print(users)
        histories = History.objects.filter(~Q(end_time=None) & Q(user__in=users)).order_by('-id')
        print(histories)
        history_details = HistoryDetail.objects.filter(history__in=histories).values('property_id')
        properties = Property.objects.filter(id__in=history_details)
        paginator = CustomPagination()
        if page_size:
            paginator.page_size = page_size
        else:
            paginator.page_size = 10
        result_page = paginator.paginate_queryset(properties, request)
        serializer = TeamVisitedPropertySerializer(result_page, many=True)
        return paginator.get_paginated_response(data=serializer.data)

    @action(detail=False,methods=['GET'],url_path='previous-drives/user/(?P<id>[\w-]+)')
    def get_previous_drives_within_my_area(self,request,*args,**kwargs):
        given_lat = request.GET.get('latitude')
        given_lng = request.GET.get('longitude')
        requested_user = User.objects.get(id = request.user.id)
        user = User.objects.get(id=kwargs['id'])

        month_count = int(request.GET.get('month'))
        end_time = datetime.datetime.today().strftime('%Y-%m-%d')

        unaware_end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d')
        aware_start_time = pytz.utc.localize(unaware_end_time) - datetime.timedelta(days=month_count*30)
        aware_end_time = pytz.utc.localize(unaware_end_time) + datetime.timedelta(days=1)

        print(aware_start_time)
        print(aware_end_time)
        histories = History.objects.filter(~Q(end_time=None)& Q(created_at__range=[aware_start_time, aware_end_time]), user=user)
        histories_filtered_id = []
        for history in histories:
            if given_lat and given_lng:
                given_lat = float(given_lat)
                given_lng = float(given_lng)
                # if UserListViewSet.check_if_within_area(self, history.start_point_longitude, history.start_point_latitude, given_lng, given_lat,0.124274):
                if UserListViewSet.check_if_within_area(self, history.start_point_longitude, history.start_point_latitude, given_lng, given_lat,3.21869):
                    histories_filtered_id.append(history.id)
        histories_filtered = History.objects.filter(id__in=histories_filtered_id).order_by('-id')
        history_serializer = HistorySerializer(histories_filtered, many=True).data

        history_details = HistoryDetail.objects.filter(history__id__in=histories_filtered_id)
        property_filtered = Property.objects.none()
        property_filtered_id = []
        for history_detail in history_details:
            property_filtered_id.append(history_detail.property.id)
        property_filtered = Property.objects.filter(id__in=property_filtered_id)
        load_list_property_serializer = LoadListPropertySerializer(property_filtered, many=True).data

        return Response({ "histories" : history_serializer,
                          "properties" : load_list_property_serializer})


    @action(detail=False,methods=['GET'],url_path='web/member')
    def get_history_list_by_member_for_web(self,request,*args,**kwargs):
        try :
            members = [int(x) for x in request.GET.get('members').split(',')]
        except:
            return Response({'status': False,'message': 'Please provide a valid data'})

        given_lat = request.GET.get('latitude')
        given_lng = request.GET.get('longitude')

        page_size = request.GET.get('limit')
        month_count = request.GET.get('month')
        polylines = []
        if month_count:
            month_count = int(month_count)
            end_time = datetime.datetime.today().strftime('%Y-%m-%d')
            unaware_end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d')
            aware_start_time = pytz.utc.localize(unaware_end_time) - datetime.timedelta(days=month_count*30)
            aware_end_time = pytz.utc.localize(unaware_end_time) + datetime.timedelta(days=1)
            histories = History.objects.filter(~Q(end_time=None) & Q(created_at__range=[aware_start_time, aware_end_time]),user__in = members).order_by('-id')
        else:
            histories = History.objects.filter(~Q(end_time=None), user__in=members).order_by('-id')
        histories_filtered_id = []
        if given_lat and given_lng:
            given_lat = float(given_lat)
            given_lng = float(given_lng)
            for history in histories:
                if UserListViewSet.check_if_within_area(self, history.start_point_longitude, history.start_point_latitude, given_lng, given_lat, 60):
                    histories_filtered_id.append(history.id)
                    if month_count:
                        polyline = {
                            'id' : history.id,
                            'polylines' : history.polylines,
                            'user': history.user.id
                        }
                        polylines.append(polyline)
            histories_filtered = History.objects.filter(id__in=histories_filtered_id).order_by('-id')
        else:
            histories_filtered = histories

        history_details = HistoryDetail.objects.filter(history__id__in=histories_filtered_id)
        property_filtered = Property.objects.none()
        property_filtered_id = []
        for history_detail in history_details:
            property_filtered_id.append(history_detail.property.id)
        property_filtered = Property.objects.filter(id__in=property_filtered_id)
        property_lat_long_serializer = PropertyLatLongSerializer(property_filtered, many=True).data


        paginator = HistoriesFilterPagination()
        if page_size:
            paginator.page_size = page_size
        else:
            paginator.page_size = 10
        result_page = paginator.paginate_queryset(histories_filtered, request)
        serializer = HistorySerializer(result_page, many=True)
        return paginator.get_paginated_response(data=serializer.data, polylines=polylines, property=property_lat_long_serializer)