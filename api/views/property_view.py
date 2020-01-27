import json
import threading
import traceback
import datetime

import requests
from django.db.models import Count, Q
from django.http import HttpResponse, JsonResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, pagination, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from notifications.signals import notify

from api.serializers import *
from houzes_api import settings

POWER_TRACE_HOST = getattr(settings, "POWER_TRACE_HOST", None)
POWER_TRACE_CLIENT_ID = getattr(settings, "POWER_TRACE_CLIENT_ID", None)
POWER_TRACE_CLIENT_SECRET = getattr(settings, "POWER_TRACE_CLIENT_SECRET", None)
power_trace_headers = {'client_id': POWER_TRACE_CLIENT_ID,
                       'client_secret': POWER_TRACE_CLIENT_SECRET}

FETCH_OWNER_INFO_CLIENT_ID = getattr(settings, "FETCH_OWNER_INFO_CLIENT_ID", None)
FETCH_OWNER_INFO_CLIENT_SECRET = getattr(settings, "FETCH_OWNER_INFO_CLIENT_SECRET", None)

class doubleQuoteDict(dict):
    def __str__(self):
        return json.dumps(self)

    def __repr__(self):
        return json.dumps(self)


class CustomPagination(pagination.PageNumberPagination):
    def get_paginated_response(self, data):
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.page.paginator.count,
            'results': data,
        })

class PropertiesFilterPagination(pagination.PageNumberPagination):
    def get_paginated_response(self, data,lat_long):
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.page.paginator.count,
            'results': data,
            'lat_long' : lat_long
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
            history = None
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
            'history': history,
            'created_at': property.created_at,
            'updated_at': property.updated_at,
            'power_trace_request_id': property.power_trace_request_id,
            'user_list_details' : UserListSerializer(property.user_list).data,
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
            message = "Property created sucessfully"
            try:
                user = User.objects.get(id = request.user.id)
                notify.send(user, recipient=user, verb='uploaded property information', action_object=property)
            except:
                print('Error in notification')
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
        for entry in requestData['property_data']:
            print(entry)
            property_info = Property()
            try:
                owner_name = entry['owner_firstname'] + " " + entry['owner_lastname']
                owner_address = entry['owner_street'] + " " + entry['owner_city'] + " " + entry['owner_state'] + " " + entry['owner_zip']
            except:
                owner_name = None
                owner_address = None
            # property_info.owner_info = json.loads(
            #     '[{"ownerName" : "' + owner_name + '","ownerAddress" : "' + owner_address
            #     + '","ownerLandLine" : "' + entry['land_line']
            #     + '","ownerMobilePhone" : "' + entry['mobile_phone']
            #     + '","ownerEmail" : "' + entry['email_address'] + '"}]'
            # )

            if owner_name == None or owner_name.strip() == "":
                property_info.owner_info = []
            else:
                property_info.owner_info = json.loads(
                    '[{"company_name" : "' + '",'
                    + '"estate" : "'
                    + '","formatted_address" : {'
                        + '"city" : '+ '""'
                        +',"state" :'+'""'
                        +',"street" : {}'
                        +',"zip_code" :'+'""'+'}'
                    +',"formatted_name" : {}'+
                    ',"full_address" : "'+owner_address+
                    '","full_name" : "'+owner_name+
                    '","other_info" : "'+''+'"}]'
                )
            property_info.street = entry['property_street']
            property_info.zip = entry['property_zip']
            property_info.city = entry['property_city']
            property_info.state = entry['property_state']
            property_info.user_list_id = requestData['user_list']


            # iterator = 0
            # while iterator < len(requestData['cities']):
            # property.owner_info = json.loads(
            #     '[{"ownerName" : "' + requestData['ownerName'][iterator] + '","ownerAddress" : "' +
            #     requestData['ownerAddress'][iterator] + '"}]')
            # property.street = requestData['streets'][iterator]
            # property.zip = requestData['zips'][iterator]
            # property.city = requestData['cities'][iterator]
            # property.state = requestData['states'][iterator]
            # property.user_list_id = requestData['user_list']
            # iterator+=1
            objs.append(property_info)

        print(objs)
        Property.objects.bulk_create(objs, batch_size=10000)
        threading.Thread(target=PropertyViewSet.update_property_lat_lng, args=(requestData['user_list'],)).start()
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

        search = request.GET.get('search')
        print(search)
        if search:
            property = property.filter(Q(street__icontains=search) | Q(city__icontains=search) | Q(state__icontains=search) | Q(zip__icontains=search))

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
            message = "Successfully deleted "
            try:
                user = User.objects.get(id=request.user.id)
                notify.send(user, recipient=user, verb='deleted a property')
            except:
                print('Error in notification')
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
            message = "Successfully updated"
        except:
            status = False
            data = {}
            message = "Please provide all the field correctly"
        return Response({'status': status, 'data': data, 'message': message})

    @action(detail=False, methods=['GET'], url_path='filter')
    def get_property_filtered_by_tag_team_member_list(self, request, *args, **kwargs):
        tagIds = None
        members = None
        listId = None

        try:
            members = [int(x) for x in request.GET.get('members').split(',')]
        except:
            return Response({'status': False, 'message': 'Please provide a valid data'})
        try:
            tagIds = [int(x) for x in request.GET.get('tags').split(',')]
        except:
            print('invalid tag format')

        property = Property.objects.filter(user_list__user__in=members)
        listId = request.GET.get('list')

        print(tagIds)
        print(members)
        print(property)

        print('working')
        page_size = request.GET.get('limit')
        if tagIds != None:
            for tagId in tagIds:
                property = property.filter(
                    Q(property_tags__contains=[{'id': str(tagId)}]) | Q(property_tags__contains=[{'id': tagId}]))
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

    @action(detail=False, methods=['GET'], url_path='(?P<id>[\w-]+)/get-existing-power-trace')
    def get_existing_power_trace_by_property_id(self, request, *args, **kwargs):
        property = Property.objects.get(id=kwargs['id'])
        power_trace_response = PropertyViewSet.get_power_trace_result_by_id(self, property)
        return JsonResponse(power_trace_response)

    @action(detail=False, methods=['GET'], url_path='filter/user/(?P<id>[\w-]+)')
    def get_property_filtered(self, request, *args, **kwargs):
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
        property = property.order_by('-created_at')
        property_lat_lon = property.filter(~Q(latitude=None) | ~Q(longitude=None))
        property_lat_lon_serializer = PropertyLatLongSerializer(property_lat_lon,many=True)
        paginator = PropertiesFilterPagination()
        if page_size:
            paginator.page_size = page_size
        else:
            paginator.page_size = 10

        result_page = paginator.paginate_queryset(property, request)

        serializer = PropertySerializer(result_page, many=True)
        return paginator.get_paginated_response(data=serializer.data, lat_long=property_lat_lon_serializer.data)

    @action(detail=False, methods=['POST'], url_path='(?P<id>[\w-]+)/payment')
    def property_payment(self, request, *args, **kwargs):
        fetch_owner_info = 1
        power_trace = 1
        property_payment_message = []
        try:
            print("try")
            if 'fetch_owner_info' in request.body:
                fetch_owner_info = int(request.body['fetch_owner_info'])
            if 'power_trace' in request.body:
                power_trace = int(request.body['power_trace'])
        except:
            if 'fetch_owner_info' in request.data:
                fetch_owner_info = int(request.data['fetch_owner_info'])
            if 'power_trace' in request.data:
                power_trace = int(request.data['power_trace'])

        user = User.objects.get(id = request.user.id)
        original_user = user
        if user.is_admin == False :
            user = User.objects.get(id = user.invited_by)
        upgrade_profile = UpgradeProfile.objects.filter(user=user).first()
        if not upgrade_profile :
            messages= []
            messages.append('Profile is not upgraded')
            return JsonResponse({"status":False,
                                 "data": { "payment" : False,
                                           "upgrade_info": UserSerializer(user).data['upgrade_info']
                                    },
                                 'message': json.dumps(messages)})
        coin_required = 0
        fetch_owner_info_coin_required = 0
        power_trace_coin_required = 0
        property = Property.objects.get(id=kwargs['id'])

        if upgrade_profile :
            if fetch_owner_info == 1 :
                try:
                    # user = User.objects.get(id=request.user.id)
                    notify.send(original_user, recipient=original_user, verb='requested to fetch ownership information of a property', action_object=property)
                except:
                    print('Error in notification')
                payment_plan = PaymentPlan.objects.filter(payment_plan_name = 'fetch-ownership-info', plan = upgrade_profile.plan).first()
                if payment_plan :
                    fetch_owner_info_coin_required = payment_plan.payment_plan_coin
            if power_trace == 1 :
                try:
                    # user = User.objects.get(id=request.user.id)
                    notify.send(original_user, recipient=original_user, verb='requested to power trace on a property', action_object=property)
                except:
                    print('Error in notification')
                payment_plan = PaymentPlan.objects.filter(payment_plan_name = 'power-trace', plan = upgrade_profile.plan).first()
                if payment_plan :
                    power_trace_coin_required =  payment_plan.payment_plan_coin
            if upgrade_profile.coin < fetch_owner_info_coin_required+power_trace_coin_required :
                messages = []
                messages.append('Sorry! Insufficient balance')
                return JsonResponse({"status": False,
                                     "data": {"payment" : False,
                                              "upgrade_info" : UserSerializer(user).data['upgrade_info']
                                      },
                                     'message': json.dumps(messages)})


        package_type = 2
        # property = Property.objects.get(id=kwargs['id'])
        property_address = ' '.join([property.street, property.city, property.state, property.zip])
        fetch_ownership_info_response = {"status": False, 'data': {}, 'message' : ''}
        power_trace_response = {"status": False, 'data': {}, 'message' : ''}
        if fetch_owner_info:
            fetch_ownership_info_response = PropertyViewSet.fetch_ownership_info(self, property)
            if fetch_ownership_info_response['status']:
                upgrade_profile.coin = upgrade_profile.coin - fetch_owner_info_coin_required
                upgrade_profile.save()

                payment_plan = PaymentPlan.objects.filter(payment_plan_name = 'fetch-ownership-info').first()
                payment_transaction = PaymentTransaction()
                payment_transaction.property = property
                payment_transaction.payment_plan = payment_plan
                payment_transaction.transaction_coin = fetch_owner_info_coin_required
                payment_transaction.created_by = original_user
                payment_transaction.save()
                property_payment_message.append('Ownership data collected')
            else:
                property_payment_message.append(fetch_ownership_info_response['message'])
        if power_trace:
            if len(property.owner_info) > 0:
                create_power_trace_response = PropertyViewSet.create_power_trace(self, package_type, request.user.id,
                                                                                 property.id, property_address)
                if create_power_trace_response['status']:
                    upgrade_profile.coin = upgrade_profile.coin - power_trace_coin_required
                    upgrade_profile.save()

                    payment_plan = PaymentPlan.objects.filter(payment_plan_name='power-trace').first()

                    payment_transaction = PaymentTransaction()
                    payment_transaction.property = property
                    payment_transaction.payment_plan = payment_plan
                    payment_transaction.transaction_coin = power_trace_coin_required
                    payment_transaction.created_by = original_user
                    payment_transaction.save()

                    power_trace_response = PropertyViewSet.get_power_trace_result_by_id(self, property)
                else:
                    power_trace_response = {'status': False, 'data': {},
                                            'message': create_power_trace_response['message']}
            else:
                power_trace_response = {'status': False, 'data': {}, 'message': 'Power trace data is not collected'}

            property_payment_message.append(power_trace_response['message'])
        return JsonResponse({"status": fetch_ownership_info_response['status'] or power_trace_response['status'],
                             "data": {"fetch_ownership_info": fetch_ownership_info_response,
                                      'power_trace': power_trace_response,
                                      "payment": True,
                                      "upgrade_info": UserSerializer(user).data['upgrade_info']
                                    },
                             'message': json.dumps(property_payment_message)})

    def fetch_ownership_info(self, property):
        address = property.street + ', ' + property.city + ', ' + property.state + ' ' + property.zip
        print('property address --> ' + address)
        objectResponse = None
        message = ""
        status = False
        data = []
        url = 'http://58.84.34.65:8080/ownership-micro-service/api/owner-info/get-owner-info-by-address'
        headers = {
            'Content-Type': 'application/json',
            'client_id': FETCH_OWNER_INFO_CLIENT_ID,
            'client_secret': FETCH_OWNER_INFO_CLIENT_SECRET
        }
        PARAMS = {
            "address": address,
            "latitude": str(property.latitude) if property.latitude else "",
            "longitude": str(property.longitude) if property.longitude else "",
            "property_id": property.id
        }
        try:
            r = requests.post(url=url, json=PARAMS, headers=headers)
            jsonResponse = r.json()
            # objectResponse = json.loads(json.dumps(jsonResponse))
            objectResponse = jsonResponse
            print(objectResponse)
        except:
            print('ex')
            status = False
            message = 'Oops! An error has occured while fetching ownership data.'
            return JsonResponse({"status": status, "data": [], 'message': message})

        if 'error' in r.json():
            message = 'Error in fetch ownership'
            status = False
            return {"status": status, 'data': [], 'message': message}
        if objectResponse['status'] == 200:
            status = True
            print('---------------------')
            print(objectResponse['data']['owner_info'])
            data.append(objectResponse['data']['owner_info'])
            property.owner_info = data
            property.save()
        if objectResponse['status'] != 200:
            status = False
            data = []
        message = objectResponse['message']
        return {"status": status, 'data': data, 'message': message}

    def create_power_trace(self, package_type, user_id, property_id, property_address):
        trace_name = generate_shortuuid()
        try:
            power_trace_request_url = POWER_TRACE_HOST + 'api/powertrace/createRequest'
            power_trace_start_by_data_url = POWER_TRACE_HOST + 'api/powertrace/save-powertrace-info-by-data'

            owner_counter = 0
            power_trace_request_pload = {'trace_name': trace_name,
                                         'package_type': package_type,
                                         'user_id': user_id,
                                         'countId': 1}
            power_trace_start_by_data_pload = {}
            property = Property.objects.get(id=property_id)
            owner_info = property.owner_info[0]
            power_trace_start_by_data_pload['owner_name' + str(owner_counter)] = owner_info['full_name']
            power_trace_start_by_data_pload['owner_address' + str(owner_counter)] = property_address
            power_trace_start_by_data_pload['property_id' + str(owner_counter)] = property_id

            ## Powertrace request
            power_trace_request_res = requests.post(power_trace_request_url, data=power_trace_request_pload,
                                                    headers=power_trace_headers)
            if power_trace_request_res.json()['code'] == 200:
                power_trace_request_id = int(power_trace_request_res.json()['data']['id'])
                power_trace_start_by_data_pload['trace_request_id'] = power_trace_request_id
                power_trace_start_by_data_pload['count_id'] = 1
                power_trace_start_by_data_pload['property_id0'] = property_id
                power_trace_start_by_data_pload['async'] = 'false'
                power_trace_start_by_data_res = requests.post(power_trace_start_by_data_url,
                                                              data=power_trace_start_by_data_pload,
                                                              headers=power_trace_headers)
                # print(power_trace_start_by_data_res.json())
                if power_trace_start_by_data_res.json()['code'] == 200:
                    info_list = power_trace_start_by_data_res.json()['data']
                    update_property_power_trace_info(info_list)

                    return {'status': True, 'data': power_trace_request_res.json()['data'],
                            'message': power_trace_request_res.json()['message']}
                else:
                    return {'status': False, 'data': {},
                            'message': 'PowerTrace Failed due to Information parsing failure!'}
            else:
                return {'status': False, 'data': {}, 'message': 'Trace name is already exists!'}
        except:
            traceback.print_exc()
            return {'status': False, 'data': {}, 'message': 'Failed to create request!!'}

    def get_power_trace_result_by_id(self, property):
        trace_id = Property.objects.get(id=property.id).power_trace_request_id
        print(trace_id)
        try:
            url = POWER_TRACE_HOST + 'api/powertrace/trace-result-by-info-id?request_info_id=' + str(trace_id)
            power_trace_result_by_id_res = requests.post(url, headers=power_trace_headers)
            print('GET POWER TRACE BY ID')
            print(power_trace_result_by_id_res.json())
            if power_trace_result_by_id_res.json()['code'] == 200:
                print('--------------')
                print(power_trace_result_by_id_res.json())
                print('--------------')
                return {'status': True, 'data': power_trace_result_by_id_res.json()['data'][0],
                        'message': 'Power trace data is collected'}
            else:
                return {'status': False, 'data': {}, 'message': power_trace_result_by_id_res.json()['message']}
        except:
            traceback.print_exc()
            return {'status': False, 'data': {}, 'message': 'Information not available'}

    def generate_shortuuid(self):
        shortuuid.set_alphabet("abcdefghijklmnopqrstuvwxyz0123456789")
        gUid = str(shortuuid.random(length=16))
        return gUid

    @action(detail=False, methods=['POST'], url_path='(?P<id>[\w-]+)/assign-multiple-tags')
    def assign_multiple_tags_to_property(self, request, *args, **kwargs):
        status = False
        data = {}
        message = ""
        try:
            property = Property.objects.get(id=kwargs['id'])
        except:
            status = False
            data = {}
            message = 'Property does not exist'
        try:
            requestData = request.data['tags']
        except:
            requestData = request.body['tags']

        property_tags = []
        if requestData !="":
            tags = [int(x) for x in requestData.split(',')]

            for tag in tags:
                property_tags.append({'id': tag})
                try:
                    propertyTag = PropertyTags.objects.get(id=tag)

                except:
                    status = False
                    data = {}
                    message = 'Invalid tag given'
                    return Response({'status': status, 'data': data, 'message': message})
        try:
            property.property_tags = property_tags
            property.save()
            propertySerializer = PropertySerializer(property)
            status = True
            data = propertySerializer.data
            message = 'Successfully added tags to property'
        except:
            status = False
            data = {}
            message = 'Failed to update Property'
        return Response({'status': status, 'data': data, 'message': message})

    @action(detail=False, methods=['POST'], url_path='(?P<pk>[\w-]+)/get-neighborhood/request')
    def request_neighborhood(self, request, *args, **kwargs):
        property = Property.objects.get(id=kwargs['pk'])
        status = False
        data = {}
        message = ''
        url = 'http://58.84.34.65:8080/ownership-micro-service/api/owner-info/get-owner-info-by-address-list'
        headers = {
            'Content-Type': 'application/json',
            'client_id': FETCH_OWNER_INFO_CLIENT_ID,
            'client_secret': FETCH_OWNER_INFO_CLIENT_SECRET
        }
        try:
            print('try')
            requestData = request.data
        except:
            print('exc')
            requestData = request.body
        print(requestData)
        try:
            r = requests.post(url=url, json=requestData, headers=headers)
            objectResponse = r.json()
            print(objectResponse)
        except:
            print('ex')
            status = False
            message = 'Oops! An error has occured while requesting neighborhood data.'
            return Response({"status": status, "data": {}, 'message': message})
        if (objectResponse['status']) == 200:
            status = True
            message = objectResponse['message']
            data = objectResponse['request_id']
            get_neighborhood = GetNeighborhood(property=property, request_id=objectResponse['request_id'])
            get_neighborhood.save()
        else:
            status = False
            message = objectResponse['message']
            data = {}
        return Response({'status': status, 'data': data, 'message': message})

    @action(detail=False, methods=['GET'], url_path='get-neighborhood/request/(?P<id>[\w-]+)')
    def get_neighborhood_by_request_id(self, request, *args, **kwargs):
        request_id = kwargs['id']
        status = False
        data = {}
        message = ''
        url = 'http://58.84.34.65:8080/ownership-micro-service/api/owner-info/get-owner-info-from-request-id'
        headers = {
            'client_id': FETCH_OWNER_INFO_CLIENT_ID,
            'client_secret': FETCH_OWNER_INFO_CLIENT_SECRET
        }
        PARAMS = {
            "id": request_id
        }
        try:
            r = requests.post(url=url, data=PARAMS, headers=headers)
            objectResponse = r.json()
            print(objectResponse)
        except:
            print('ex')
            status = False
            message = 'Oops! An error has occured while requesting neighborhood.'
            return Response({"status": status, "data": {}, 'message': message})
        if (objectResponse['status']) == 200:
            status = True
            message = objectResponse['message']
            data = objectResponse['data']
            get_neighborhood = GetNeighborhood.objects.filter(request_id=request_id)[0]
            get_neighborhood.ownership_info = objectResponse['data']
            get_neighborhood.save()
        else:
            status = False
            message = objectResponse['message']
            data = {}
        return Response({'status': status, 'data': data, 'message': message})

    @action(detail=False, methods=['POST'], url_path='(?P<pk>[\w-]+)/get-neighborhood')
    def get_neighborhood_in_one_call(self, request, *args, **kwargs):
        respone_data = {"status": False, "data": {"ownership_info": None, "power_trace": None}, "message": ""}
        fetch_ownership_respone_data = {"status": True, "message": "", "data": None}
        property_data = Property.objects.get(id=kwargs['pk'])
        request_body = request.data

        try:
            user = User.objects.get(id=request.user.id)
            notify.send(user, recipient=user, verb='requested neighborhood information', action_object=property_data)
        except:
            print('Error in notification')

        fetch_ownership_respone_data = PropertyViewSet.request_neighborhood_method(self, request,request_body,
                                                                                       property_data)
        return JsonResponse(fetch_ownership_respone_data)

    def create_multiple_power_trace(self, get_neighborhood, request):
        print(get_neighborhood)
        try:
            power_trace_request_url = POWER_TRACE_HOST + 'api/powertrace/createRequest'
            power_trace_start_by_data_url = POWER_TRACE_HOST + 'api/powertrace/save-powertrace-info-by-data'

            trace_name = generate_shortuuid()
            package_type = 2
            user_id = request.user.id
            countId = len(get_neighborhood.ownership_info)

            power_trace_request_pload = {'trace_name': trace_name,
                                         'package_type': package_type,
                                         'user_id': user_id}
            power_trace_start_by_data_pload = {}
            total = 0
            total = countId
            power_trace_request_pload['countId'] = total

            for idx, val in enumerate(get_neighborhood.ownership_info):
                try:
                    power_trace_start_by_data_pload['owner_name' + str(idx)] = val['owner_info']['full_name']
                    power_trace_start_by_data_pload['owner_address' + str(idx)] = val['owner_info']['full_address']
                    power_trace_start_by_data_pload['property_id' + str(idx)] = idx
                except:
                    print('ex')
                    return {'code': 500,
                            'message': 'Failed to create request! owner_name/owner_address/property_id is missing.'}

            power_trace_request_res = requests.post(power_trace_request_url, data=power_trace_request_pload,
                                                    headers=power_trace_headers)
            if power_trace_request_res.json()['code'] == 200:
                power_trace_request_id = int(power_trace_request_res.json()['data']['id'])
                power_trace_start_by_data_pload['trace_request_id'] = power_trace_request_id
                power_trace_start_by_data_pload['count_id'] = total
                power_trace_start_by_data_pload['async'] = "false"

                power_trace_start_by_data_res = requests.post(power_trace_start_by_data_url,
                                                              data=power_trace_start_by_data_pload,
                                                              headers=power_trace_headers)
                # print(power_trace_start_by_data_res.json())
                if power_trace_start_by_data_res.json()['code'] == 200:
                    info_list = power_trace_start_by_data_res.json()['data']
                    # update_property_power_trace_info(info_list)
                    return (power_trace_request_res.json())
                else:
                    return {'code': 400, 'message': 'PowerTrace Failed due to Information parsing failure!',
                            'data': power_trace_start_by_data_res.json()}
            else:
                return {'code': 400, 'message': 'Trace name is already exists!', 'data': power_trace_request_res.json()}
        except:
            traceback.print_exc()
            return {'code': 500, 'message': 'Failed to create request! Server Error!'}

    def get_power_trace_by_power_trace_request_id(self, get_neighborhood, request):
        try:
            url = POWER_TRACE_HOST + 'api/powertrace/trace-result-by-info-id?request_info_id=' + str(
                get_neighborhood.power_trace_request_id)
            power_trace_result_by_id_res = requests.post(url, headers=power_trace_headers)
            return power_trace_result_by_id_res.json()
        except:
            traceback.print_exc()
            return {'code': 500, 'message': 'Server Error!'}

    def request_neighborhood_method(self, request, requestData, property):
        user = User.objects.get(id=request.user.id)
        original_user =user
        if not user.is_admin:
            user = User.objects.get(id = user.invited_by)
        upgrade_profile = UpgradeProfile.objects.filter(user = user).first()

        status = False
        data = {}
        message = ''
        formatted_request_data= []
        fetch_owner_info = 0
        power_trace = 0
        url = 'http://58.84.34.65:8080/ownership-micro-service/api/owner-info/get-owner-info-by-address-list'
        headers = {
            'Content-Type': 'application/json',
            'client_id': FETCH_OWNER_INFO_CLIENT_ID,
            'client_secret': FETCH_OWNER_INFO_CLIENT_SECRET
        }
        try:
            if 'fetch_owner_info' in requestData:
                fetch_owner_info = int(requestData['fetch_owner_info'])
            if 'power_trace' in requestData:
                power_trace = int(requestData['power_trace'])
            if 'address' in requestData:
                for data in requestData['address']:
                    try:
                        get_neighborhood = GetNeighborhood()
                        get_neighborhood.property = property
                        get_neighborhood.neighbor_address = data['address']
                        get_neighborhood.street = data['street']
                        get_neighborhood.city = data['city']
                        get_neighborhood.state = data['state']
                        get_neighborhood.zip = data['zip']
                        get_neighborhood.requested_by = User.objects.get(id = request.user.id)
                        if power_trace == 1:
                            get_neighborhood.is_owner_info_requested = True
                            get_neighborhood.is_power_trace_requested = True
                        elif power_trace == 0 and fetch_owner_info == 1:
                            get_neighborhood.is_owner_info_requested = True
                        elif power_trace == 0 and fetch_owner_info == 0 :
                            return {'status': False, 'data': {}, 'message': 'Invalid request'}
                        get_neighborhood.latitude = data['latitude']
                        get_neighborhood.longitude = data['longitude']
                        get_neighborhood.save()
                        formatted_data = {
                            "address" : data['address'],
                            "latitude" : data['latitude'],
                            "longitude": data['longitude'],
                            "property_id": get_neighborhood.id
                        }
                        formatted_request_data.append(formatted_data)
                    except:
                        print('EXCEPTION IN REQUEST')
                required_coin = 0.0
                if fetch_owner_info == 1:
                    required_coin = required_coin + float(PaymentPlan.objects.filter(payment_plan_name='fetch-ownership-info', plan=upgrade_profile.plan).first().payment_plan_coin)
                if power_trace == 1:
                    required_coin = required_coin + float(PaymentPlan.objects.filter(payment_plan_name='power-trace', plan=upgrade_profile.plan).first().payment_plan_coin)
                if upgrade_profile.coin < required_coin :
                    status = False
                    message = 'Sorry! Insufficient balance'
                    return ({"status": status, "data": {}, 'message': message})
                upgrade_profile.coin = float(upgrade_profile.coin)-required_coin
                upgrade_profile.save()

                r = requests.post(url=url, json=formatted_request_data, headers=headers)
                objectResponse = r.json()
                GetNeighborhood.objects.filter(property=property, status = None).update(ownership_info_request_id = objectResponse['request_id'], owner_status = 'requested', status='requested')

                if (objectResponse['status']) == 200:
                    # get_neighborhoods = GetNeighborhood.objects.filter(property=property)
                    status = True
                    message = objectResponse['message']
                    data = objectResponse['request_id']

                else:
                    status = False
                    message = objectResponse['message']
                    data = {}
            if 'neighbor_id' in requestData:
                neighbors_id = requestData['neighbor_id']
                neighbors = GetNeighborhood.objects.filter(id__in = neighbors_id)
                for neighbor in neighbors:
                    formatted_data = {
                        "address": neighbor.neighbor_address,
                        "latitude": neighbor.latitude,
                        "longitude": neighbor.longitude,
                        "property_id": neighbor.id
                    }
                    formatted_request_data.append(formatted_data)

                neighbors.update(is_owner_info_requested = False, is_power_trace_requested = False)
                if fetch_owner_info == 1:
                    r = requests.post(url=url, json=formatted_request_data, headers=headers)
                    objectResponse = r.json()
                    print('932')
                    print(objectResponse)
                    if objectResponse['status']==200 :
                        status = True
                        data = {}
                        message = objectResponse['message']
                        neighbors.update(ownership_info_request_id = objectResponse['request_id'], owner_status = 'requested', status='requested', is_owner_info_requested = True)
                        if power_trace == 1:
                            neighbors.update(is_power_trace_requested = True, power_trace_status = 'requested')
                    else:
                        status = False
                        data = objectResponse['data']
                        message = objectResponse['message']

                if power_trace == 1 and fetch_owner_info == 0:
                    neighbors.update(is_power_trace_requested = True)
                    responseData = PropertyViewSet.request_power_trace_again(self,neighbors)

                    status = responseData['status']
                    data = responseData['data']
                    message = responseData ['message']

        except:
            status = False
            message = 'Oops! An error has occured while requesting neighborhood data.'
            return ({"status": status, "data": {}, 'message': message})

        return ({"status": status, "data": {}, 'message': message})

    def get_neighborhood_by_request_id_method(self, request_id):
        status = False
        data = {}
        message = ''
        url = 'http://58.84.34.65:8080/ownership-micro-service/api/owner-info/get-owner-info-from-request-id'
        headers = {
            'client_id': FETCH_OWNER_INFO_CLIENT_ID,
            'client_secret': FETCH_OWNER_INFO_CLIENT_SECRET
        }
        PARAMS = {
            "id": request_id
        }
        try:
            r = requests.post(url=url, data=PARAMS, headers=headers)
            objectResponse = r.json()
            print(objectResponse)
        except:
            print('ex')
            status = False
            message = 'Oops! An error has occured while requesting neighborhood data.'
            return Response({"status": status, "data": {}, 'message': message})
        if (objectResponse['status']) == 200:
            status = True
            message = objectResponse['message']
            data = objectResponse['data']
            get_neighborhood = GetNeighborhood.objects.filter(ownership_info_request_id=request_id)[0]
            get_neighborhood.ownership_info = objectResponse['data']
            get_neighborhood.owner_status = "complete"
            get_neighborhood.save()
        else:
            status = False
            message = objectResponse['message']
            data = {}
        return {'status': status, 'data': data, 'message': message}

    def request_power_trace_again(self, get_neighborhoods):
        print('REQUEST POWER TRACE')
        print(generate_shortuuid())
        try:
            power_trace_request_url = POWER_TRACE_HOST + 'api/powertrace/createRequest'
            power_trace_start_by_data_url = POWER_TRACE_HOST + 'api/powertrace/save-powertrace-info-by-data'

            power_trace_request_pload = {'trace_name': generate_shortuuid(),
                                         'package_type': 2,
                                         'user_id': get_neighborhoods.first().requested_by.id}
            power_trace_start_by_data_pload = {}
            total = 0

            total = get_neighborhoods.count()
            power_trace_request_pload['countId'] = total
            i = 0
            for neighbor in get_neighborhoods:
                try:
                    power_trace_start_by_data_pload['owner_name' + str(i)] = neighbor.ownership_info['owner_info'][
                        'full_name']
                    power_trace_start_by_data_pload['owner_address' + str(i)] = neighbor.ownership_info['owner_info'][
                        'full_address']
                    power_trace_start_by_data_pload['property_id' + str(i)] = int(
                        neighbor.ownership_info['property_id'])
                except:
                    return (
                        {'status': False, 'data' : {},
                         'message': 'Request failed! Ownership info is mandatory/required.'})
                i = i + 1
            ## Powertrace request
            power_trace_request_res = requests.post(power_trace_request_url, data=power_trace_request_pload,
                                                    headers=power_trace_headers)
            if power_trace_request_res.json()['code'] == 200:
                power_trace_request_id = int(power_trace_request_res.json()['data']['id'])
                power_trace_start_by_data_pload['trace_request_id'] = power_trace_request_id
                power_trace_start_by_data_pload['count_id'] = total

                power_trace_start_by_data_res = requests.post(power_trace_start_by_data_url,
                                                              data=power_trace_start_by_data_pload,
                                                              headers=power_trace_headers)
                # print(power_trace_start_by_data_res.json())
                if power_trace_start_by_data_res.json()['code'] == 200:
                    get_neighborhoods.update(
                        power_trace_request_id=power_trace_start_by_data_res.json()['data'][0]['trace_requests_id'],
                        power_trace_status='requested')
                    return { 'status' : True, 'data' :power_trace_request_res.json()['data'], 'message' : power_trace_request_res.json()['message'] }
                else:
                    return {'status': False, 'message': 'PowerTrace Failed due to Information parsing failure!',
                            'data': power_trace_start_by_data_res.json()}
            else:
                return {'status': False, 'message': 'Trace name is already exists!', 'data': power_trace_request_res.json()}
        except:
            traceback.print_exc()
            return {'status': False, 'message': 'Failed to create request! Server Error!'}

    @action(detail=False, methods=['DELETE'], url_path='(?P<pk>[\w-]+)/tag/(?P<id>[\w-]+)')
    def delete_property_tag(self, request, *args, **kwargs):
        try:
            property = Property.objects.get(id=kwargs['pk'])
            tag_list = property.property_tags
            for i in range(len(tag_list)):
                if tag_list[i]['id'] == kwargs['id']:
                    print(tag_list[i])
                    del tag_list[i]
                    break
                if tag_list[i]['id'] == int(kwargs['id']):
                    del tag_list[i]
                    break
            property.property_tags = tag_list
            property.save()
            return Response({'status' : True, 'data': PropertySerializer(property).data, 'message' : 'Successfully deleted tag'})
        except:
            return Response({'status' : False, 'data': {}, 'message' : 'Error deleting tag'})

    # @action(detail=False, methods=['GET'], url_path='fetch-missing-lat-lng/(?P<pk>[\w-]+)')
    # def fetch_lat_lng(self, request, *args, **kwargs):
    #     try:
    #         list_id = kwargs['pk']
    #         # update_property_lat_lng(list_id)
    #         threading.Thread(target=PropertyViewSet.update_property_lat_lng, args=(list_id,)).start()
    #         return Response({'code': 200, 'message': 'Updating Lat/Lng...'})
    #     except:
    #         traceback.print_exc()
    #         return Response({'code': 500, 'message': 'Server Error!'})

    def get_property_info_by_address(address):
        print(address)
        url = 'https://www.mapdevelopers.com/data.php?operation=geocode'
        data = {'address': address,
                'region': 'USA',
                'code': '9jw1wi8'}
        res = requests.post(url, data=data)
        print(res.json())
        return res.json()

    def update_property_lat_lng(list_id):
        print("Started...list_id: " + str(list_id))
        property_list = list(Property.objects.filter(latitude__isnull=True, user_list_id=list_id))
        for property_info in property_list:
            try:
                address = property_info.street + ' ' + property_info.city + ' ' + property_info.state + ' ' + property_info.zip
                print(address)
                fetched_data = PropertyViewSet.get_property_info_by_address(address)
                if 'response' in fetched_data and fetched_data['response'] and fetched_data['data']['zip']:
                    lat = float(fetched_data['data']['lat'])
                    lng = float(fetched_data['data']['lng'])
                    print(lat, lng)
                    property_info.latitude = lat
                    property_info.longitude = lng
                    Property.objects.filter(id=property_info.id).update(latitude=lat, longitude=lng)
            except:
                traceback.print_exc()
                # return Response({'code': 500, 'message': 'Server Error!'})
        print("Completed...list_id: " + str(list_id))

def update_property_power_trace_info(info_list):
    for info in info_list:
        try:
            property_id = int(info['client_lead_info_id'])
            info_id = int(info['id'])
            Property.objects.filter(id=property_id).update(
                power_trace_request_id=info_id)
        except:
            traceback.print_exc()
