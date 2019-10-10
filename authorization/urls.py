from django.conf.urls import url
from django.urls import path, include
from rest_framework import routers
from rest_framework.documentation import include_docs_urls

from authorization import views
# from.views import *



urlpatterns = [
    path('log-in/', views.login, name='log-in'),
    path('sign-in-with-facebook/', views.facebook_login, name='sign-in-with-facebook'),

]

