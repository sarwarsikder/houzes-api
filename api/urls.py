from django.conf.urls import url
from django.urls import path, include
from rest_framework import routers
from rest_framework.documentation import include_docs_urls
# from.views import *

from api.views.user_view import UserViewSet
from api.views.user_location_view import UserLocationViewSet
from api.views.user_verification_view import UserVerificationsViewSet
from api.views.property_tags_view import PropertyTagsViewSet
from api.views.property_notes_view import PropertyNotesViewSet
from api.views.property_photos_view import PropertyPhotosViewSet
from api.views.user_list_view import UserListViewSet
from api.views.list_properties_view import ListPropertiesViewSet
from api.views.user_driver_view import UserDriverViewSet
from api.views.user_ownership_usage_view import UserOwnershipUsageViewSet
from api.views.visited_properties_view import VisitedPropertiesViewSet
from api.views.user_socket_view import UserSocketsViewSet
from api.views.property_view import PropertyViewSet
from api.views.invitations_view import InvitationsViewSet
from api.views.scout_view import ScoutViewSet

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
router.register(r'teams',InvitationsViewSet)
router.register(r'scout',ScoutViewSet)


urlpatterns = [
]

urlpatterns += router.urls

