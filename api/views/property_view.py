import json
import traceback

import requests
from django.db.models import Count, Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, pagination, filters
from rest_framework.decorators import action
from django.http import HttpResponse, JsonResponse
from api.serializers import *
from api.models import *
from rest_framework.response import Response
from houzes_api import settings

POWER_TRACE_HOST = getattr(settings, "POWER_TRACE_HOST", None)
POWER_TRACE_CLIENT_ID = getattr(settings, "POWER_TRACE_CLIENT_ID", None)
POWER_TRACE_CLIENT_SECRET = getattr(settings, "POWER_TRACE_CLIENT_SECRET", None)
power_trace_headers = {'client_id': POWER_TRACE_CLIENT_ID,
                       'client_secret': POWER_TRACE_CLIENT_SECRET}


class CustomPagination(pagination.PageNumberPagination):
    def get_paginated_response(self, data):
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.page.paginator.count,
            'results': data,
        })


class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    filterset_fields = ["street"]
    ordering = ['-id']

    def retrieve(self, request, *args, **kwargs):
        property_id = kwargs['pk']
        property = Property.objects.get(id=property_id)
        tags = []
        try:
            user_list_id = property.user_list.id
        except:
            user_list_id = None
        try:
            history = HistoryDetail.objects.filter(property__id=property.id)[0].history.id
        except:
            history =None
        for tag in property.property_tags:
            property_tags = PropertyTags.objects.get(id=tag['id'])
            print(PropertyTagsSerializer(property_tags).data)
            tags.append(PropertyTagsSerializer(property_tags).data)

        property_representation = {
            'id': property.id,
            'user_list': user_list_id,
            'street': property.street,
            'city': property.city,
            'state': property.state,
            'zip': property.zip,
            'cad_acct': property.cad_acct,
            'gma_tag': property.gma_tag,
            'latitude': property.latitude,
            'longitude': property.longitude,
            'property_tags': tags,
            'owner_info': property.owner_info,
            'photos': PropertyPhotosSerializer(PropertyPhotos.objects.filter(property=property), many=True).data,
            'notes': PropertyNotesSerializer(PropertyNotes.objects.filter(property=property), many=True).data,
            'history' : history,
            'created_at': property.created_at,
            'updated_at': property.updated_at,
            'power_trace_request_id': property.power_trace_request_id
        }
        return Response(property_representation)

    def create(self, request, *args, **kwargs):
        street = ""
        city = ""
        state = ""
        zip = ""
        cad_acct = ""
        gma_tag = None
        latitude = None
        longitude = None
        property_tags = []
        owner_info = []
        user_list = None
        history = None

        status = False
        data = {}
        message = ""

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
            if 'history' in request.data:
                history_id = request.data['history']
                history = History.objects.get(id=history_id)

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
                if gma_tag == '':
                    gma_tag = None
            if 'latitude' in request.body:
                latitude = request.body['latitude']
                if latitude == '':
                    latitude = None
            if 'longitude' in request.body:
                longitude = request.body['longitude']
                if longitude == '':
                    longitude = None
            if 'property_tags' in request.body:
                property_tags = request.body['property_tags']
            if 'owner_info' in request.body:
                owner_info = request.body['owner_info']
            if 'user_list' in request.body:
                user_list = request.body['user_list']
                user_list = UserList.objects.get(id=user_list)
            if 'history' in request.body:
                history_id = request.body['history']
                history = History.objects.get(id=history_id)
        try:
            property = Property(street=street, city=city, state=state, zip=zip, cad_acct=cad_acct, gma_tag=gma_tag,
                                latitude=latitude, longitude=longitude, property_tags=property_tags,
                                owner_info=owner_info, user_list=user_list)
            property.save()

            if history != None:
                historyDetail = HistoryDetail(history=history, property=property)
                historyDetail.save()

            status = True
            data = PropertySerializer(property).data
            message = "Successfully created property"
        except:
            status = False
            data = {}
            message = "Failed to create property"
        return Response({'status': status, 'data': data, 'message': message})

    @action(detail=False, url_path='info/(?P<pk>[\w-]+)')
    def get_details_by_google_place_id(self, request, *args, **kwargs):
        property_id = kwargs['pk']
        property = Property.objects.get(id=property_id)
        property_with_notes = property.propertynotes_set.all()
        property_with_photos = property.propertyphotos_set.all()
        property = PropertySerializer(property).data
        property['notes'] = PropertyNotesSerializer(property_with_notes, many=True).data
        property['photos'] = PropertyPhotosSerializer(property_with_photos, many=True).data
        return HttpResponse(content=json.dumps(property), status=200, content_type="application/json")

    @action(detail=False, url_path='google-place/(?P<id>[\w-]+)')
    def get_info(self, request, *args, **kwargs):
        google_place_id = kwargs['id']
        property = Property.objects.get(google_place_id=google_place_id)
        if property:
            property_with_notes = property.propertynotes_set.all()
            property_with_photos = property.propertyphotos_set.all()
            property = PropertySerializer(property).data
            property['notes'] = PropertyNotesSerializer(property_with_notes, many=True).data
            property['photos'] = PropertyPhotosSerializer(property_with_photos, many=True).data
            return HttpResponse(content=json.dumps(property), status=200, content_type="application/json")

        else:
            return super().create(request, *args, **kwargs)

    @action(detail=False, methods=['post'], url_path='bulk-create')
    def property_bulk_create(self, request, *args, **kwargs):
        try:
            requestData = request.data
        except:
            requestData = request.body
        print(requestData)
        objs = []
        iterator = 0
        while iterator < len(requestData['cities']):
            property = Property()
            property.owner_info = json.loads(
                '[{"ownerName" : "' + requestData['ownerName'][iterator] + '","ownerAddress" : "' +
                requestData['ownerAddress'][iterator] + '"}]')
            property.street = requestData['streets'][iterator]
            property.zip = requestData['zips'][iterator]
            property.city = requestData['cities'][iterator]
            property.state = requestData['states'][iterator]
            property.user_list_id = requestData['user_list']

            objs.append(property)

            iterator += 1

        Property.objects.bulk_create(objs, batch_size=50)
        return JsonResponse({'status': True, 'message': 'Properties created'})

    # @action(detail=False, methods=['GET'], url_path='tag/(?P<id>[\w-]+)')
    # def get_property_by_tag(self, request, *args, **kwargs):
    #     tagId = kwargs['id']
    #     property = Property.objects.filter(property_tags__id = tagId)
    #     propertySerializer = PropertySerializer(property, many=True).data
    #     return HttpResponse(content=json.dumps(propertySerializer), status=200, content_type="application/json")

    @action(detail=False, url_path='list/(?P<pk>[\w-]+)')
    def get_properties_by_user_list(self, request, *args, **kwargs):
        listId = kwargs['pk']
        page_size = request.GET.get('limit')
        list = UserList.objects.get(id=listId)
        property = Property.objects.filter(user_list=list).annotate(photo_count=Count('propertyphotos'),
                                                                    note_count=Count('propertynotes')).order_by('-id')

        paginator = CustomPagination()
        if page_size:
            paginator.page_size = page_size
        else:
            paginator.page_size = 10

        result_page = paginator.paginate_queryset(property, request)
        serializer = PropertySerializer(result_page, many=True)
        return paginator.get_paginated_response(data=serializer.data)

    @action(detail=False, methods=['GET'], url_path='tag/(?P<id>[\w-]+)')
    def get_property_by_tag(self, request, *args, **kwargs):
        tagId = kwargs['id']
        page_size = request.GET.get('limit')
        user = User.objects.get(id=request.user.id)
        property = Property.objects.filter(property_tags__contains=[{'id': int(tagId, 10)}], user_list__user=user)
        paginator = CustomPagination()
        if page_size:
            paginator.page_size = page_size
        else:
            paginator.page_size = 10

        result_page = paginator.paginate_queryset(property, request)

        serializer = PropertySerializer(result_page, many=True)
        return paginator.get_paginated_response(data=serializer.data)

    def destroy(self, request, *args, **kwargs):
        property_id = kwargs['pk']
        try:
            Property.objects.get(id=property_id).delete()
            status = True
            message = "Property deleted"
        except:
            status = False
            message = "Error deleting property or property does not exist"
        return Response({'status': status, 'message': message})

    def partial_update(self, request, *args, **kwargs):
        status = False
        data = {}
        message = ""

        # res = super().partial_update(request, *args, **kwargs)
        property = Property.objects.get(id=kwargs['pk'])
        try:
            if 'street' in request.data:
                property.street = request.data['street']
            if 'city' in request.data:
                property.city = request.data['city']
            if 'state' in request.data:
                property.state = request.data['state']
            if 'zip' in request.data:
                property.zip = request.data['zip']
            if 'cad_acct' in request.data:
                property.cad_acct = request.data['cad_acct']
            if 'gma_tag' in request.data:
                property.gma_tag = request.data['gma_tag']
            if 'latitude' in request.data:
                property.latitude = request.data['latitude']
            if 'longitude' in request.data:
                property.longitude = request.data['longitude']
            if 'property_tags' in request.data:
                property.property_tags = request.data['property_tags']
            if 'owner_info' in request.data:
                property.owner_info = request.data['owner_info']
        except:
            if 'street' in request.body:
                property.street = request.body['street']
            if 'city' in request.body:
                property.city = request.body['city']
            if 'state' in request.body:
                property.state = request.body['state']
            if 'zip' in request.body:
                property.zip = request.body['zip']
            if 'cad_acct' in request.body:
                property.cad_acct = request.body['cad_acct']
            if 'gma_tag' in request.body:
                property.gma_tag = request.body['gma_tag']
            if 'latitude' in request.body:
                property.latitude = request.body['latitude']
            if 'longitude' in request.body:
                property.longitude = request.body['longitude']
            if 'property_tags' in request.body:
                property.property_tags = request.body['property_tags']
            if 'owner_info' in request.body:
                property.owner_info = request.body['owner_info']
        try:
            property.save()
            status = True
            data = PropertySerializer(property).data
            message = "Property updated successfully"
        except:
            status = False
            data = {}
            message = "Please provide all the field correctly"
        return Response({'status': status, 'data': data, 'message': message})

    @action(detail=False, methods=['GET'], url_path='filter/user/(?P<id>[\w-]+)')
    def get_property_filtered_by_tag_team_member_list(self, request, *args, **kwargs):
        tagIds = None
        listId = None

        user = User.objects.get(id=kwargs['id'])
        property = Property.objects.filter(user_list__user=user)
        tagIds = request.GET.getlist('tag')
        listId = request.GET.get('list')

        print(tagIds)

        print('working')
        page_size = request.GET.get('limit')
        if tagIds != None:
            for tagId in tagIds:
                property = property.filter(
                    Q(property_tags__contains=[{'id': tagId}]) | Q(property_tags__contains=[{'id': int(tagId, 10)}]))
        if listId != None:
            property = property.filter(user_list__id=listId)
        paginator = CustomPagination()
        if page_size:
            paginator.page_size = page_size
        else:
            paginator.page_size = 10

        result_page = paginator.paginate_queryset(property, request)

        serializer = PropertySerializer(result_page, many=True)
        return paginator.get_paginated_response(data=serializer.data)

    @action(detail=False, methods=['GET'], url_path='(?P<id>[\w-]+)/fetch-owner-info')
    def fetch_owner_info(self, request, *args, **kwargs):
        property = Property.objects.get(id=kwargs['id'])
        address = property.street + ', ' + property.city + ', ' + property.state + ' ' + property.zip
        print(address)

        objectResponse = None
        message = ""
        data = []
        status = False
        url = 'http://172.18.1.11:8080/ownership-micro-service/api/owner-info/get-owner-info-by-address'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'client_id': 'ZDPLLBHQARK3QWSMVY0X2B15YQJSIYC5UJ2',
            'client_secret': 'RBVUBV6VJVBKJBDDJ2E2JEBJEO84594T54GB'
        }
        PARAMS = {'address': address}

        try:
            r = requests.post(url=url, data=PARAMS, headers=headers)
            jsonResponse = r.json()
            objectResponse = json.loads(json.dumps(jsonResponse))

        except:
            status = False
            message = 'Micro Service Error'
            data = {}
            return JsonResponse({"status": status, 'data': data, 'message': message})

        if 'error' in r.json():
            message = 'Error'
            data = {}
            status = False
            return JsonResponse({"status": status, 'data': data, 'message': message})
        if objectResponse['status'] == 200:
            status = True
            property.owner_info = objectResponse['owner_info']
            property.save()
            data = PropertySerializer(property).data
        if objectResponse['status'] != 200:
            status = False
        message = objectResponse['message']
        return JsonResponse({"status": status, 'data': data, 'message': message})

    @action(detail=False, methods=['POST'], url_path='(?P<id>[\w-]+)/payment')
    def property_payment(self, request, *args, **kwargs):
        fetch_owner_info = 1
        power_trace = 1
        try:
            print("try")
            if 'fetch_owner_info' in request.body:
                fetch_owner_info = int(request.body['fetch_owner_info'])
            if 'power_trace' in request.body:
                power_trace = int(request.body['power_trace'])
        except:
            print("ex")
            if 'fetch_owner_info' in request.data:
                fetch_owner_info = int(request.data['fetch_owner_info'])
            if 'power_trace' in request.data:
                power_trace = int(request.data['power_trace'])

        package_type = 2
        property = Property.objects.get(id=kwargs['id'])
        fetch_ownership_info_response = {}
        create_power_trace_response = {}
        power_trace_response = {}
        print(type(fetch_owner_info))
        print(power_trace)
        if fetch_owner_info:
            fetch_ownership_info_response = json.loads(PropertyViewSet.fetch_ownership_info(self, property))
            print("f1")
        if power_trace:
            if len(property.owner_info)>0 :
                create_power_trace_response = json.loads(PropertyViewSet.create_power_trace(self, package_type, request.user.id, property.id))
                print("f2")
                if create_power_trace_response['status']:
                    power_trace_response = PropertyViewSet.get_power_trace_result_by_id(self, property)
                    print("f2")
                else :
                    power_trace_response = {'status': False, 'data': {}, 'message': create_power_trace_response['message']}
            else:
                power_trace_response = {'status' : False, 'data' : {}, 'message' : 'Ownership info is not fetched'}
        return JsonResponse({"fetch_ownership_info": fetch_ownership_info_response,'power_trace' : power_trace_response})

    def fetch_ownership_info(self,property):
        address = property.street + ', ' + property.city + ', ' + property.state + ' ' + property.zip
        print('property address --> '+address )
        objectResponse = None
        message = ""
        status = False
        data = []
        url = 'http://58.84.34.65:8080/ownership-micro-service/api/owner-info/get-owner-info-by-address'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'client_id': 'ZDPLLBHQARK3QWSMVY0X2B15YQJSIYC5UJ2',
            'client_secret': 'RBVUBV6VJVBKJBDDJ2E2JEBJEO84594T54GB'
        }
        PARAMS = {'address': address}

        try:
            r = requests.post(url=url, data=PARAMS, headers=headers)
            jsonResponse = r.json()
            objectResponse = json.loads(json.dumps(jsonResponse))

        except:
            status = False
            message = 'Fetch owner info micro service error'
            return JsonResponse({"status": status, "data": [], 'message': message})

        if 'error' in r.json():
            message = 'Error in fetch ownership'
            status = False
            return json.dumps({"status": status,'data' : [], 'message': message})
        if objectResponse['status'] == 200:
            status = True
            print(objectResponse['owner_info'])
            data = objectResponse['owner_info']
            property.owner_info = objectResponse['owner_info']
            property.save()
        if objectResponse['status'] != 200:
            status = False
            data = []
        message = objectResponse['message']
        return json.dumps({"status": status,'data' : data, 'message': message})

    def create_power_trace(self, package_type, user_id, property_id):
        trace_name = generate_shortuuid()
        try:
            power_trace_request_url = POWER_TRACE_HOST + 'api/powertrace/createRequest'
            power_trace_start_by_data_url = POWER_TRACE_HOST + 'api/powertrace/save-powertrace-info-by-data'

            owner_counter = 0
            power_trace_request_pload = {'trace_name': trace_name,
                                         'package_type': package_type,
                                         'user_id': user_id,
                                         'countId' : owner_counter}
            power_trace_start_by_data_pload = {}
            property = Property.objects.get(id=property_id)
            owner_info = property.owner_info[0]
            power_trace_start_by_data_pload['owner_name' + str(owner_counter)] = owner_info['full_name']
            power_trace_start_by_data_pload['owner_address' + str(owner_counter)] = owner_info['full_address']
            power_trace_start_by_data_pload['property_id' + str(owner_counter)] = property_id

            ## Powertrace request
            power_trace_request_res = requests.post(power_trace_request_url, data=power_trace_request_pload,
                                                    headers=power_trace_headers)
            if power_trace_request_res.json()['code'] == 200:
                power_trace_request_id = int(power_trace_request_res.json()['data']['id'])
                power_trace_start_by_data_pload['trace_request_id'] = power_trace_request_id
                power_trace_start_by_data_pload['count_id'] = 1
                power_trace_start_by_data_pload['property_id0'] = property_id
                power_trace_start_by_data_res = requests.post(power_trace_start_by_data_url,
                                                              data=power_trace_start_by_data_pload,
                                                              headers=power_trace_headers)
                # print(power_trace_start_by_data_res.json())
                if power_trace_start_by_data_res.json()['code'] == 200:
                    info_list = power_trace_start_by_data_res.json()['data']
                    update_property_power_trace_info(info_list)

                    return json.dumps({'status': True, 'data' : power_trace_request_res.json()['data'], 'message' : power_trace_request_res.json()['message']})
                else:
                    return json.dumps({'status': False, 'data': {},'message': 'PowerTrace Failed due to Information parsing failure!'})
            else:
                return json.dumps(
                    {'status': False, 'data' : {}, 'message': 'Trace name is already exists!'})
        except:
            traceback.print_exc()
            return json.dumps({'status': False, 'data': {}, 'message': 'Failed to create request! Server Error!'})

    def get_power_trace_result_by_id(self,property):
        trace_id = Property.objects.get(id = property.id).power_trace_request_id
        print(trace_id)
        try:
            url = POWER_TRACE_HOST + 'api/powertrace/trace-result-by-info-id?request_info_id=' + str(trace_id)
            power_trace_result_by_id_res = requests.post(url, headers=power_trace_headers)
            print('GET POWER TRACE BY ID')
            print(power_trace_result_by_id_res.json())
            if power_trace_result_by_id_res.json()['code'] == 200 :
                return {'status' : True, 'data' : power_trace_result_by_id_res.json()['data'][0], 'message' : power_trace_result_by_id_res.json()['message']}
                # return json.dumps({'status' : True, 'data' : power_trace_result_by_id_res.json()['data'][0], 'message' : power_trace_result_by_id_res.json()['message']})
            else :
                return {'status' : False, 'data' : {}, 'message' : power_trace_result_by_id_res.json()['message']}
        except:
            traceback.print_exc()
            return {'status': False, 'data': {}, 'message': 'Server Error!'}

    def generate_shortuuid(self):
        shortuuid.set_alphabet("abcdefghijklmnopqrstuvwxyz0123456789")
        gUid = str(shortuuid.random(length=16))
        return gUid

def update_property_power_trace_info(info_list):
    for info in info_list:
        try:
            property_id = int(info['client_lead_info_id'])
            info_id = int(info['id'])
            Property.objects.filter(id=property_id).update(
                power_trace_request_id=info_id)
        except:
            traceback.print_exc()

