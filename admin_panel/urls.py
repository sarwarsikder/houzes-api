from django.conf.urls import url
from django.urls import path, include
from rest_framework import routers
from rest_framework.documentation import include_docs_urls

from admin_panel import views
# from.views import *



urlpatterns = [
    path('', views.Index, name='index'),
    path('user-detail/<str:user_id>', views.User_detail, name ='user-detail'),
    path('user-detail-update/<str:user_id>', views.User_detail_update, name='user-detail-update'),
    path('user-detail-create/', views.User_detail_create, name='user-detail-create'),
    path('user-list/', views.User_list, name='user-list'),
    path('property-list/', views.Property_list, name='property-list'),
    path('property-detail/<str:property_id>', views.Property_detail, name='property-detail'),
    path('property-detail-update/<str:property_id>', views.Property_detail_update, name='user-detail-update'),
    path('property-detail-create/', views.Property_detail_create, name='property-detail-create'),
    path('active-user-list/', views.Active_user_list, name='active-user-list'),
    path('active-user-list/user-block/<str:user_id>', views.User_block, name='user-block'),

]

