from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path
from django.views.generic.base import TemplateView

from vng_api_common.views import ViewConfigView

from .views import HTTP413View, HTTP500View

handler500 = 'drc.utils.views.server_error'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('drc.api.urls')),

    # dynamic backend URLs for nginx error pages
    path("413.json", HTTP413View.as_view()),
    path("500.json", HTTP500View.as_view()),

    # Simply show the index template.
    path('', TemplateView.as_view(template_name='index.html')),
    path('view-config/', ViewConfigView.as_view(), name='view-config'),
    path('ref/', include('vng_api_common.urls')),
    path('ref/', include('vng_api_common.notifications.urls')),
]

# NOTE: The staticfiles_urlpatterns also discovers static files (ie. no need to run collectstatic). Both the static
# folder and the media folder are only served via Django if DEBUG = True.
urlpatterns += staticfiles_urlpatterns() + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.PRIVATE_MEDIA_URL, document_root=settings.PRIVATE_MEDIA_ROOT)

if settings.DEBUG and 'debug_toolbar' in settings.INSTALLED_APPS:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
