import csv
import traceback

from django.db.models import Count, Q
from rest_framework.decorators import api_view
from django.http import HttpResponse, JsonResponse
from api.models import *


@api_view(['GET'])
def export_CSV(request,**kwargs):
    tagIds = None
    listId = None

    user = User.objects.get(id=kwargs['id'])
    properties = Property.objects.filter(user_list__user=user)
    tagIds = request.GET.getlist('tag')
    listId = request.GET.get('list')

    print(tagIds)

    print('working')
    # page_size = request.GET.get('limit')
    if tagIds != None:
        for tagId in tagIds:
            properties = properties.filter(
                Q(property_tags__contains=[{'id': tagId}]) | Q(property_tags__contains=[{'id': int(tagId, 10)}]))
    if listId != None:
        properties = properties.filter(user_list__id=listId)
    properties = properties.order_by('-created_at')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'

    writer = csv.writer(response)
    writer.writerow(
        ['Street', 'City', 'State', 'Zip', 'Owner first name', 'Owner last name', 'Owner street', 'Owner city',
         'Owner state', 'Owner zip'])
    for property in properties:
        owner_first_name = ""
        owner_last_name = ""
        owner_street = ""
        owner_city = ""
        owner_state = ""
        owner_zip = ""
        try:
            if len(property.owner_info) > 0:
                owner_first_name = "" if property.owner_info[0]['formatted_name'] == None else \
                property.owner_info[0]['formatted_name']['first_name']
                owner_last_name = "" if property.owner_info[0]['formatted_name'] == None else \
                property.owner_info[0]['formatted_name']['last_name']
        except:
            traceback.print_exc()
        try:
            if len(property.owner_info) > 0:
                owner_city = "" if property.owner_info[0]["formatted_address"] == None else \
                property.owner_info[0]["formatted_address"]["city"]
                owner_state = "" if property.owner_info[0]["formatted_address"] == None else \
                property.owner_info[0]["formatted_address"]["state"]
                owner_zip = "" if property.owner_info[0]["formatted_address"] == None else \
                property.owner_info[0]["formatted_address"]["zip_code"]
                owner_street = "" if property.owner_info[0]["formatted_address"] == None else \
                property.owner_info[0]["formatted_address"]["street"]["formatted_full_street_name"]


        except:
            traceback.print_exc()
        writer.writerow(
            [property.street, property.city, property.state, property.zip, owner_first_name, owner_last_name,
             owner_street, owner_city, owner_state, owner_zip])

    return response

@api_view(['GET'])
def get_csv_properties(request, **kwargs):
    tagIds = None
    listId = None

    # user = User.objects.get(id=kwargs['id'])
    properties = Property.objects.all()
    tagIds = request.GET.getlist('tag')
    listId = request.GET.get('list')

    print(tagIds)

    print('working')
    # page_size = request.GET.get('limit')
    if tagIds != None:
        for tagId in tagIds:
            properties = properties.filter(
                Q(property_tags__contains=[{'id': tagId}]) | Q(property_tags__contains=[{'id': int(tagId, 10)}]))
    if listId != None:
        properties = properties.filter(user_list__id=listId)
    properties = properties.order_by('-created_at')
    properties_response = []
    for property in properties:
        property_response = {}
        owner_first_name = ""
        owner_last_name = ""
        owner_street = ""
        owner_city = ""
        owner_state = ""
        owner_zip = ""
        try:
            if len(property.owner_info) > 0:
                owner_first_name = "" if property.owner_info[0]['formatted_name'] == None else \
                property.owner_info[0]['formatted_name']['first_name']
                owner_last_name = "" if property.owner_info[0]['formatted_name'] == None else \
                property.owner_info[0]['formatted_name']['last_name']
        except:
            traceback.print_exc()
        try:
            if len(property.owner_info) > 0:
                owner_city = "" if property.owner_info[0]["formatted_address"] == None else \
                property.owner_info[0]["formatted_address"]["city"]
                owner_state = "" if property.owner_info[0]["formatted_address"] == None else \
                property.owner_info[0]["formatted_address"]["state"]
                owner_zip = "" if property.owner_info[0]["formatted_address"] == None else \
                property.owner_info[0]["formatted_address"]["zip_code"]
                owner_street = "" if property.owner_info[0]["formatted_address"] == None else \
                property.owner_info[0]["formatted_address"]["street"]["formatted_full_street_name"]


        except:
            traceback.print_exc()
        # writer.writerow(
        #     [property.street, property.city, property.state, property.zip, owner_first_name, owner_last_name,
        #      owner_street, owner_city, owner_state, owner_zip])
        property_response ={
            "id" : property.id,
            "street" : property.street,
            "city" : property.city,
            "state" : property.state,
            "zip" : property.zip,
            "owner_first_name" : owner_first_name,
            "owner_last_name" : owner_last_name,
            "owner_street" : owner_street,
            "owner_city" : owner_city,
            "owner_state" : owner_state,
            "owner_zip" : owner_zip
        }
        properties_response.append(property_response)
    print(properties_response)
    return JsonResponse(properties_response,safe=False)