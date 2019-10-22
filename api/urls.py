from django.conf.urls import url
from django.urls import path, include
from rest_framework import routers
from rest_framework.documentation import include_docs_urls
# from.views import *
from api.views.assign_member_to_list_view import AssignMemberToListViewSet
from api.views.history_view import HistoryViewSet
from api.views.history_detail_view import HistoryDetailViewSet
from api.views.user_view import UserViewSet
from api.views.user_location_view import UserLocationViewSet
from api.views.user_verification_view import UserVerificationsViewSet
from api.views.property_tags_view import PropertyTagsViewSet
from api.views.property_notes_view import PropertyNotesViewSet
from api.views.property_photos_view import PropertyPhotosViewSet
from api.views.user_list_view import UserListViewSet
from api.views.user_driver_view import UserDriverViewSet
from api.views.user_ownership_usage_view import UserOwnershipUsageViewSet
from api.views.visited_properties_view import VisitedPropertiesViewSet
from api.views.user_socket_view import UserSocketsViewSet
from api.views.property_view import PropertyViewSet
from api.views.invitations_view import InvitationsViewSet
from api.views.scout_view import ScoutViewSet
from api.views.scouts_list_property_view import ScoutsListPropertyViewSet

router = routers.DefaultRouter()
router.register(r'user', UserViewSet)
router.register(r'user-location', UserLocationViewSet)
router.register(r'user-verification', UserVerificationsViewSet)
router.register(r'tag', PropertyTagsViewSet)
router.register(r'note', PropertyNotesViewSet)
router.register(r'photo', PropertyPhotosViewSet)
router.register(r'list', UserListViewSet)
router.register(r'property', PropertyViewSet)
router.register(r'user-driver', UserDriverViewSet)
router.register(r'user-ownership-usage', UserOwnershipUsageViewSet)
router.register(r'visited-properties', VisitedPropertiesViewSet)
router.register(r'user-sockets', UserSocketsViewSet)
router.register(r'team', InvitationsViewSet)
router.register(r'scout', ScoutViewSet)
router.register(r'scouts-list-property', ScoutsListPropertyViewSet)
router.register(r'assign-member-to-list', AssignMemberToListViewSet)
router.register(r'history',HistoryViewSet)
router.register(r'history-detail', HistoryDetailViewSet)



urlpatterns = [
]

urlpatterns += router.urls
