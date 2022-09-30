from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter

# Openapi query parameters for version querying
VERSIE_QUERY_PARAM = OpenApiParameter(
    name="versie",
    location=OpenApiParameter.QUERY,
    description="Het (automatische) versienummer van het INFORMATIEOBJECT.",
    type=OpenApiTypes.INT,
)
REGISTRATIE_QUERY_PARAM = OpenApiParameter(
    name="registratieOp",
    location=OpenApiParameter.QUERY,
    description="Een datumtijd in ISO8601 formaat. De versie van het INFORMATIEOBJECT die qua `begin_registratie` het "
    "kortst hiervoor zit wordt opgehaald.",
    type=OpenApiTypes.STR,
)
