from drf_yasg import openapi

info = openapi.Info(
    title="Documentregistratiecomponent (drc) API",
    default_version='1',
    description="Een API om een documentregistratiecomponent te benaderen",
    contact=openapi.Contact(
        email="support@maykinmedia.nl",
        url="https://github.com/VNG-Realisatie/gemma-zaken"
    ),
    license=openapi.License(name="EUPL 1.2"),
)
