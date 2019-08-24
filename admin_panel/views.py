from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from api.models import *


# Create your views here.
def Index(request):
    users = User.objects.all()
    user_count = User.objects.all().count()
    active_user_count = User.objects.filter(is_active=True).count()
    admin_user_count = User.objects.filter(is_admin= True).count()

    propertyInfo = Property.objects.all()
    propertyInfo_count = propertyInfo.count()

    print(users.values())

    template = loader.get_template('index.html')
    context = {
        'users': users,
        'user_count' : user_count,
        'active_user_count' : active_user_count,
        'propertyInfo' : propertyInfo,
        'propertyInfo_count' : propertyInfo_count,
        'admin_user_count' : admin_user_count,
    }
    return HttpResponse(template.render(context, request))

    # { % csrf_token %}

def User_detail(request,user_id):
    print(user_id)
    template = loader.get_template('user-detail.html')

    user = User.objects.get(id=int(user_id))
    propertyNotes = PropertyNotes.objects.filter(user = user)
    propertyPhotos = PropertyPhotos.objects.filter(user = user)

    context = {
        'user': user,
        'propertyNotes' : propertyNotes,
        'propertyPhotos' : propertyPhotos,
    }
    return HttpResponse(template.render(context, request))

def Property_detail(request,property_id):
    template = loader.get_template('property-detail.html')
    propertyInfo = Property.objects.get(id = property_id)
    propertyNotes = PropertyNotes.objects.filter(property = propertyInfo)
    propertyPhotos = PropertyPhotos.objects.filter(property = propertyInfo)

    print(propertyInfo.property_tags.values())

    context = {
        'propertyInfo':propertyInfo,
        'propertyNotes':propertyNotes,
        'propertyPhotos':propertyPhotos,
    }
    return HttpResponse(template.render(context, request))

def User_detail_update(request,user_id):
    if request.POST:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        is_admin = False
        if request.POST.get('is_admin') == 'admin':
            is_admin = True
        print(first_name+' '+last_name+' '+' '+email+' '+phone_number+' '+str(is_admin))
        user = User.objects.get(id=user_id)
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.phone_number = phone_number
        user.is_admin = is_admin
        user.save()
        # User_detail(request,user_id)

    template = loader.get_template('user-detail-update.html')
    user = User.objects.get(id=user_id)
    context = {
        'user':user,
    }
    return HttpResponse(template.render(context,request))

def User_detail_create(request):
    if request.POST:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        is_admin = False
        if request.POST.get('is_admin') == 'admin':
            is_admin = True
        print(first_name+' '+last_name+' '+' '+email+' '+phone_number+' '+str(is_admin))
        user = User.objects.create(first_name=first_name,last_name=last_name,email=email,phone_number=phone_number,is_admin=is_admin)
        user.save()

    template = loader.get_template('user-detail-create.html')
    context = {
    }
    return HttpResponse(template.render(context,request))

def Property_detail_update(request,property_id):
    if request.POST:
        cad_acct = request.POST.get('cad_acct')
        gma_tag = request.POST.get('gma_tag')
        property_address = request.POST.get('property_address')
        owner_name = request.POST.get('owner_name')
        owner_address = request.POST.get('owner_address')
        lat = request.POST.get('lat')
        lon = request.POST.get('lon')

        propertyInfo = Property.objects.get(id = property_id)
        propertyInfo.cad_acct = cad_acct
        propertyInfo.gma_tag = gma_tag
        propertyInfo.property_address = property_address
        propertyInfo.owner_name = owner_name
        propertyInfo.owner_address = owner_address
        propertyInfo.lat = lat
        propertyInfo.lon = lon
        propertyInfo.save()

    template = loader.get_template('property-detail-update.html')
    propertyInfo = Property.objects.get(id = property_id)
    context ={
        'propertyInfo':propertyInfo
    }
    return HttpResponse(template.render(context,request))


def Property_detail_create(request):
    if request.POST:
        cad_acct = request.POST.get('cad_acct')
        gma_tag = request.POST.get('gma_tag')
        property_address = request.POST.get('property_address')
        owner_name = request.POST.get('owner_name')
        owner_address = request.POST.get('owner_address')
        lat = request.POST.get('lat')
        lon = request.POST.get('lon')
        propertyInfo = Property.objects.create(cad_acct=cad_acct, gma_tag=gma_tag, property_address=property_address, owner_name=owner_name, owner_address = owner_address, lat=lat, lon=lon)
        propertyInfo.save()

    template = loader.get_template('property-detail-create.html')
    context = {
    }
    return HttpResponse(template.render(context,request))

def User_list(request):
    template = loader.get_template('user-list.html')
    users = User.objects.all()
    context ={
        'users':users,
    }
    return HttpResponse(template.render(context,request))

def Active_user_list(request):
    template = loader.get_template('active-user-list.html')
    users = User.objects.filter(is_active=True)
    context = {
        'users' : users,
    }
    return HttpResponse(template.render(context,request))

def User_block(request,user_id):
    user = User.objects.get(id = user_id)
    user.is_active = False
    user.save()

    return redirect('/admin-panel/active-user-list')

def Property_list(request):
    template = loader.get_template('property-list.html')
    propertyInfo = Property.objects.all()
    context ={
        'propertyInfos':propertyInfo,
    }
    return HttpResponse(template.render(context,request))

