from django.conf.urls import url
from houzes_api.admin import admin_site
from django.urls import path, include
from rest_framework.documentation import include_docs_urls
from api.views import error_handler
import notifications.urls

from authorization.views.customTokenView import CustomTokenView
from authorization.views.customConvertTokenView import CustomConvertTokenView

urlpatterns = [
    path('admin/', admin_site.urls),
    path('api/', include('api.urls')),
    url(r'^docs/', include_docs_urls(title='HOUZES API',
                                     authentication_classes=[],
                                     permission_classes=[])),
    url(r'^o/token', CustomTokenView.as_view()),
    url(r'^auth/convert-token/?$', CustomConvertTokenView.as_view(), name="convert_token"),

    url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    url('admin-panel/', include(('admin_panel.urls', 'admin_panel'), namespace='admin_panel')),
    url('recurring-bill/', include(('recurring_bill.urls', 'recurring_bill'), namespace='recurring_bill')),
    url('authorization/', include(('authorization.urls', 'authorization'), namespace='authorization')),
    url('auth/', include('rest_framework_social_oauth2.urls')),
    url('^inbox/notifications/', include(notifications.urls, namespace='notifications')),
]

handler404 = error_handler.handler404
handler500 = error_handler.handler500
