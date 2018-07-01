from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

info = openapi.Info(
    title="Documentregistratiecomponent (drc) API documentatie",
    default_version='1',
    description="Referentieimplementatie van de documentregistratiecomponent",
    contact=openapi.Contact(email="support@maykinmedia.nl"),
    license=openapi.License(name="EUPL 1.2"),
)

schema_view = get_schema_view(
    # validators=['flex', 'ssv'],
    public=True,
    permission_classes=(permissions.AllowAny,),
)
