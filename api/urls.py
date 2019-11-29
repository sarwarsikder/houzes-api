from django.conf.urls import url
from django.urls import path, include
from rest_framework import routers
from rest_framework.documentation import include_docs_urls
# from.views import *
from api.views import power_trace_view, photos_view, scout_form_view
from api.views.assign_member_to_list_view import AssignMemberToListViewSet
from api.views.forget_password_view import ForgetPasswordViewSet
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
from api.views.scout_user_list_view import ScoutUserListViewSet

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
router.register(r'scout-user-list', ScoutUserListViewSet)
router.register(r'assign-member-to-list', AssignMemberToListViewSet)
router.register(r'history',HistoryViewSet)
router.register(r'history-detail', HistoryDetailViewSet)
router.register(r'forget-password', ForgetPasswordViewSet)


urlpatterns = [
    path('power-trace/create/', power_trace_view.create),
    path('power-trace/getAllRequestByUserId/<int:user_id>/', power_trace_view.get_all_request_by_user_id),
    path('power-trace/getResultById/<int:trace_id>/', power_trace_view.get_result_by_id),
    path('photos/property/<int:id>/original/', photos_view.original_single_property_photo_by_propertyId,  name='original-photo-by-property'),
    path('photos/property/<int:id>/thumb/', photos_view.thumb_single_property_photo_by_propertyId,  name='original-photo-by-property'),
    path('scout-form/check-url/', scout_form_view.check_url ,name='check-url'),
    path('scout-form/tags/', scout_form_view.get_tags, name='get-tags'),
    path('scout-form/create-property/', scout_form_view.create_property, name='create-property'),
    path('scout-form/property/<int:id>/photo/multiple-upload/', scout_form_view.photo_multiple_upload, name='photo-multiple-upload'),
    path('scout-form/property/<int:id>/note/multiple-upload/', scout_form_view.note_multiple_upload, name='note-multiple-upload'),

]

urlpatterns += router.urls
