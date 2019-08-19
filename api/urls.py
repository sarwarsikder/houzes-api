from django.conf.urls import url
from django.urls import path, include
from rest_framework import routers
from rest_framework.documentation import include_docs_urls
from.views import *

router = routers.DefaultRouter()
router.register(r'user', UserViewSet)
router.register(r'user_location', UserLocationViewSet)
router.register(r'user_verification', UserVerificationsViewSet)
router.register(r'property_tags', PropertyTagsViewSet)
router.register(r'property_notes', PropertyNotesViewSet)
router.register(r'property_photos', PropertyPhotosViewSet)
router.register(r'user_list', UserListViewSet)
router.register(r'list_properties', ListPropertiesViewSet)
router.register(r'user_driver', UserDriverViewSet)
router.register(r'user_ownership_usage', UserOwnershipUsageViewSet)
router.register(r'visited_properties', VisitedPropertiesViewSet)
router.register(r'user_sockets', UserSocketsViewSet)
router.register(r'property_info', PropertyViewSet)


urlpatterns = [
]

urlpatterns += router.urls

