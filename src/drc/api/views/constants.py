from drf_yasg import openapi

# Openapi query parameters for version querying
VERSIE_QUERY_PARAM = openapi.Parameter(
    "versie",
    openapi.IN_QUERY,
    description="Het (automatische) versienummer van het INFORMATIEOBJECT.",
    type=openapi.TYPE_INTEGER,
)
REGISTRATIE_QUERY_PARAM = openapi.Parameter(
    "registratieOp",
    openapi.IN_QUERY,
    description="Een datumtijd in ISO8601 formaat. De versie van het INFORMATIEOBJECT die qua `begin_registratie` het "
    "kortst hiervoor zit wordt opgehaald.",
    type=openapi.TYPE_STRING,
)
