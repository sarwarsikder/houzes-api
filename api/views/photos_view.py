from PIL import Image
from django.http import HttpResponse, HttpResponsePermanentRedirect

from api.models import *


def original_single_property_photo_by_propertyId(request, id):
    image_url = ""
    try:
        photos = PropertyPhotos.objects.filter(property__id=id)[0]
        image_url = photos.photo_url
    except:
        image_url = 'https://triplezeroproperty.com.au/wp-content/uploads/2019/06/newhompepage3.jpg'
    return HttpResponsePermanentRedirect(image_url)


def thumb_single_property_photo_by_propertyId(request, id):
    image_url = ""
    try:
        photos = PropertyPhotos.objects.filter(property__id=id)[0]
        image_url = photos.thumb_photo_url
    except:
        image_url = 'https://triplezeroproperty.com.au/wp-content/uploads/2019/06/newhompepage3.jpg'
    return HttpResponsePermanentRedirect(image_url)
