from django.conf.urls import url
from django.urls import path, include
from rest_framework import routers
from rest_framework.documentation import include_docs_urls

from recurring_bill import views
# from.views import *



urlpatterns = [
    path('create-subscription/', views.create_subscription, name='create-subscription'),
    path('create-subscription-existing/', views.create_subscription_from_customer_profile,name='create-subscription-existing'),
    path('get-subscription-details/', views.get_subscription_details, name='get-subscription-details'),
    path('get-subscription-status/', views.get_subscription_status, name='get-subscription-status'),
    path('get-subscription-list/', views.get_list_of_subscriptions, name='get-subscription-list'),
    path('cancel-subscription/', views.cancel_subscription, name='cancel-subscription'),
    path('update-subscription/', views.update_subscription, name='update-subscription'),
    path('update-amount-subscription/', views.update_amount_of_subscription, name='update-subscription'),

]

