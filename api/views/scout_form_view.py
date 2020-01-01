from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import pagination
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.utils import json
from api.models import *
from api.serializers import *
from houzes_api import settings
from houzes_api.util.file_upload import file_upload
from resizeimage import resizeimage
from PIL import Image
from io import BytesIO
import time


@csrf_exempt
def check_url(request):
    url = request.GET.get('url')
    scout = Scout.objects.filter(url=url)[0]
    scoutUserList = ScoutUserList.objects.filter(scout=scout)[0]
    userList = UserList.objects.get(id=scoutUserList.user_list.id)
    userListSerializer = UserListSerializer(userList)
    return JsonResponse(userListSerializer.data)


@csrf_exempt
def get_tags(request):
    queryset = PropertyTags.objects.all().order_by('-id')
    serializer = PropertyTagsSerializer(queryset, many=True)
    return JsonResponse(serializer.data, safe=False)


@csrf_exempt
def create_property(request):
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
    url = ''
    history = None

    status = False
    data = {}
    message = ""

    try:  # when passing json
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        if 'street' in body:
            street = body['street']
        if 'city' in body:
            city = body['city']
        if 'state' in body:
            state = body['state']
        if 'zip' in body:
            zip = body['zip']
        if 'property_tags' in body:
            property_tags = body['property_tags']
        if 'owner_info' in body:
            owner_info = body['owner_info']
        if 'url' in body:
            url = body['url']

    except:  # when passing form data
        if 'street' in request.POST:
            street = request.POST['street']
        if 'city' in request.POST:
            city = request.POST['city']
        if 'state' in request.POST:
            state = request.POST['state']
        if 'zip' in request.POST:
            zip = request.POST['zip']
        if 'property_tags' in request.POST:
            property_tags = request.POST['property_tags']
            property_tags = json.loads(property_tags)
        if 'owner_info' in request.POST:
            owner_info = request.POST['owner_info']
        if 'url' in request.POST:
            url = request.POST['url']

    try:
        scout = Scout.objects.filter(url=url)[0]
        scoutUserList = ScoutUserList.objects.filter(scout=scout)[0]
        user_list = UserList.objects.get(id=scoutUserList.user_list.id)

        property = Property(street=street, city=city, state=state, zip=zip, property_tags=property_tags,
                            owner_info=owner_info, user_list=user_list)
        property.save()

        status = True
        data = PropertySerializer(property).data
        message = "Successfully created property"
    except:
        status = False
        data = {}
        message = "Failed to create property"
    return JsonResponse({'status': status, 'data': data, 'message': message})


@csrf_exempt
def photo_multiple_upload(request, id):
    property_id = id
    url = request.POST['url']
    scout = Scout.objects.filter(url=url)[0]
    scoutUserList = ScoutUserList.objects.filter(scout=scout)[0]
    user = UserList.objects.get(id=scoutUserList.user_list.id).user
    property = Property.objects.get(id=property_id)
    images_data = request.FILES
    propertyPhotos = []
    for image_data in images_data.values():
        print(image_data)
        print(image_data.__dict__)
        file_path = "photos/property_photos/{}/{}/{}".format(str(user.id), property_id,
                                                             str(time.time()).replace('.', '_') + '.jpg')
        s3_url = "https://s3.{}.amazonaws.com/{}/{}".format(settings.AWS_REGION, settings.S3_BUCKET_NAME, file_path)
        file_upload(image_data, file_path)

        thumb_file_path = "photos/property_photos/{}/{}/{}".format(str(user.id), property_id,
                                                                   str(time.time()).replace('.', '_') + '_thumb.jpg')
        thumb_s3_url = "https://s3.{}.amazonaws.com/{}/{}".format(settings.AWS_REGION, settings.S3_BUCKET_NAME,
                                                                  thumb_file_path)
        with Image.open(image_data) as image:
            thumb = resizeimage.resize_cover(image, [150, 150])
            thumb_byte = BytesIO()
            thumb.save(thumb_byte, format=thumb.format)
            thumb_image = thumb_byte.getvalue()
            file_upload(thumb_image, thumb_file_path)
        propertyPhoto = PropertyPhotos()
        propertyPhoto.user = user
        propertyPhoto.property = property
        propertyPhoto.photo_url = s3_url
        propertyPhoto.thumb_photo_url = thumb_s3_url
        propertyPhotos.append(propertyPhoto)
    PropertyPhotos.objects.bulk_create(propertyPhotos, batch_size=50)
    return JsonResponse({'status': True, 'message': 'Property photos uploaded'})


@csrf_exempt
def note_multiple_upload(request, id):
    property = Property.objects.get(id=id)
    try:
        body_unicode = request.body.decode('utf-8')
        requestData = json.loads(body_unicode)
    except:
        requestData = request.POST
    if 'url' in requestData:
        url = requestData['url']
        scout = Scout.objects.filter(url=url)[0]
        scoutUserList = ScoutUserList.objects.filter(scout=scout)[0]
        user = UserList.objects.get(id=scoutUserList.scout.id).user

    print(requestData)
    objs = []

    for it in requestData:
        property_note = PropertyNotes()
        property_note.title = it['title']
        property_note.notes = it['notes']
        url = it['url']
        scout = Scout.objects.filter(url=url)[0]
        scoutUserList = ScoutUserList.objects.filter(scout=scout)[0]
        user = UserList.objects.get(id=scoutUserList.scout.id).user
        property_note.user = User.objects.get(id=user.id)
        property_note.property = property

        objs.append(property_note)

    PropertyNotes.objects.bulk_create(objs, batch_size=50)
    return JsonResponse({'status': True, 'message': 'Property notes created'})


@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def scout_properties(request):
    url = request.GET.get('url')
    scout = Scout.objects.filter(url=url)[0]
    scout_user_list = ScoutUserList.objects.filter(scout=scout)[0]
    user_list = UserList.objects.get(id=scout_user_list.user_list.id)
    properties = Property.objects.filter(user_list=user_list).order_by('-created_at')
    page_size = request.GET.get('limit')

    paginator = PageNumberPagination()
    if page_size:
        paginator.page_size = page_size
    else:
        paginator.page_size = 10

    result_page = paginator.paginate_queryset(properties, request)
    serializer = PropertySerializer(result_page, many=True)
    return paginator.get_paginated_response(data=serializer.data)

@csrf_exempt
def scout_property_details(request,id):
    data = {}
    url = request.GET.get('url')
    try:
        scout = Scout.objects.filter(url=url)[0]
        scoutUserList = ScoutUserList.objects.filter(scout=scout)[0]
        userList = UserList.objects.get(id = scoutUserList.user_list.id)
        property = Property.objects.get(id = id)
        if property.user_list == userList:
            data = PropertySerializer(property).data
    except:
        data = {}

    return JsonResponse(data)




