from django.conf.urls import url
from django.urls import path, include
from rest_framework import routers
from rest_framework.documentation import include_docs_urls
# from.views import *
from api.views import power_trace_view, photos_view, scout_form_view, payment_gateway_view, microservice_endpoint_view, \
    notifications_view, fcm_notification, user_token_view, apple_payment_gateway_view, apple_upgrade_profile_view, \
    export_csv_view
from api.views.activity_log_view import ActivityLogViewSet
from api.views.assign_member_to_list_view import AssignMemberToListViewSet
from api.views.forget_password_view import ForgetPasswordViewSet
from api.views.get_neighborhood_view import GetNeighborhoodViewSet
from api.views.history_view import HistoryViewSet
from api.views.history_detail_view import HistoryDetailViewSet
from api.views.mail_wizard_subs_type_view import MailWizardSubsTypeViewSet
from api.views.mail_wizard_user_info_view import MailWizardUserInfoViewSet
from api.views.payment_plan_view import PaymentPlanViewSet
from api.views.payment_transaction_view import PaymentTransactionViewSet
from api.views.plan_view import PlanViewSet
from api.views.upgrade_history_view import UpgradeHistoryViewSet
from api.views.upgrade_profile_view import UpgradeProfileViewSet
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
from api.views import ownership_info_view
from api.views.mail_wizard_view import MailWizardInfoViewSet
from api.views.billing_card_info_view import BillingCardInfoViewSet

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
router.register(r'history', HistoryViewSet)
router.register(r'history-detail', HistoryDetailViewSet)
router.register(r'forget-password', ForgetPasswordViewSet)
router.register(r'activity-log', ActivityLogViewSet)
router.register(r'get-neighborhood', GetNeighborhoodViewSet)
router.register(r'plan', PlanViewSet)
router.register(r'payment-plan', PaymentPlanViewSet)
router.register(r'upgrade-profile', UpgradeProfileViewSet)
router.register(r'payment-transaction', PaymentTransactionViewSet)
router.register(r'upgrade-history', UpgradeHistoryViewSet)
router.register(r'mail-wizard', MailWizardInfoViewSet)
router.register(r'billing-card', BillingCardInfoViewSet)
router.register(r'mail-wizard-subscriptions', MailWizardSubsTypeViewSet)
router.register(r'mail-wizard-user-info', MailWizardUserInfoViewSet)

urlpatterns = [
    path('power-trace/create/', power_trace_view.create),
    path('power-trace/getAllRequestByUserId/<int:user_id>/', power_trace_view.get_all_request_by_user_id),
    path('power-trace/getResultById/<int:trace_id>/', power_trace_view.get_result_by_id),
    path('photos/property/<int:id>/original/', photos_view.original_single_property_photo_by_propertyId,
         name='original-photo-by-property'),
    path('photos/property/<int:id>/thumb/', photos_view.thumb_single_property_photo_by_propertyId,
         name='original-photo-by-property'),
    path('scout-form/check-url/', scout_form_view.check_url, name='check-url'),
    path('scout-form/tags/', scout_form_view.get_tags, name='get-tags'),
    path('scout-form/create-property/', scout_form_view.create_property, name='create-property'),
    path('scout-form/property/<int:id>/photo/multiple-upload/', scout_form_view.photo_multiple_upload,
         name='photo-multiple-upload'),
    path('scout-form/property/<int:id>/note/multiple-upload/', scout_form_view.note_multiple_upload,
         name='note-multiple-upload'),
    path('scout-form/properties/', scout_form_view.scout_properties, name='scout-properties'),
    path('scout-form/property/<int:id>', scout_form_view.scout_property_details, name='scout-property-details'),
    path('scout-form/property/<int:id>/update/', scout_form_view.scout_property_update, name='scout-property-update'),
    path('scout-form/property/<int:id>/assign-tag/', scout_form_view.assign_tag_to_property,
         name='scout-property-assign-tag'),
    path('scout-form/photo/<int:id>/delete/', scout_form_view.delete_property_photo, name='delete-property-photo'),
    path('scout-form/property/<int:id>/photo/upload/', scout_form_view.note_upload, name='property-note-upload'),
    path('scout-form/note/<int:id>/update/', scout_form_view.update_note, name='update-note'),
    path('scout-form/note/<int:id>/delete/', scout_form_view.delete_property_note, name='delete-note'),
    path('scout-form/property/<int:id>/delete/', scout_form_view.delete_property, name='delete-property'),

    path('ownership-info/get-owner-info-by-address/', ownership_info_view.get_owner_info_by_address,
         name='get-ownership-info-by-address'),
    path('payment-gateway/charge-card/', payment_gateway_view.charge_credit_card, name='charge-credit-card'),
    path('provide-ownership-info/<int:id>/', microservice_endpoint_view.provide_ownership_info, name='ownership-endpoint'),
    path('provide-power-trace/<int:id>/', microservice_endpoint_view.provide_power_trace,name='powertrace-endpoint'),
    path('notifications/', notifications_view.get_all_notifications, name='notifications'),
    path('fcm/update-notification', fcm_notification.send_update_notification),
    path('login/token', user_token_view.get_token),
    path('apple-payment-gateway/', apple_payment_gateway_view.apple_payment_gateway, name='apple-payment-gateway'),
    path('apple-upgrade-profile/', apple_upgrade_profile_view.apple_upgrade_profile, name='apple-upgrade-profile'),
    path('export-csv/csv-properties/', export_csv_view.get_csv_properties, name='get-csv-properties'),
    path('export-csv/download-csv/', export_csv_view.download_CSV, name='download-csv')

]

urlpatterns += router.urls
