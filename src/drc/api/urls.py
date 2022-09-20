from django.conf.urls import url
from django.urls import include, path

from vng_api_common import routers
from vng_api_common.views import SchemaViewAPI, SchemaViewRedoc

from .views import (
    BestandsDeelViewSet,
    EnkelvoudigInformatieObjectAuditTrailViewSet,
    EnkelvoudigInformatieObjectViewSet,
    GebruiksrechtenViewSet,
    ObjectInformatieObjectViewSet,
    VerzendingViewSet,
)

router = routers.DefaultRouter()
router.register(
    "enkelvoudiginformatieobjecten",
    EnkelvoudigInformatieObjectViewSet,
    [
        routers.nested("audittrail", EnkelvoudigInformatieObjectAuditTrailViewSet)
    ],  # TODO: uncomment this for testing, this should be fixed though
    basename="enkelvoudiginformatieobject",
)
router.register("gebruiksrechten", GebruiksrechtenViewSet)
router.register("objectinformatieobjecten", ObjectInformatieObjectViewSet)
router.register("bestandsdelen", BestandsDeelViewSet)
router.register("verzendingen", VerzendingViewSet)

# TODO: the EndpointEnumerator seems to choke on path and re_path

urlpatterns = [
    url(
        r"^v(?P<version>\d+)/",
        include(
            [
                # API documentation
                url(
                    r"^schema/openapi.yaml",
                    SchemaViewAPI.as_view(),
                    name="schema-json",
                ),
                url(
                    r"^schema/$",
                    SchemaViewRedoc.as_view(),
                    name="schema-redoc",
                ),
                # actual API
                url(r"^", include(router.urls)),
                # should not be picked up by drf-yasg
                path("", include("vng_api_common.api.urls")),
                path("", include("vng_api_common.notifications.api.urls")),
            ]
        ),
    )
]
