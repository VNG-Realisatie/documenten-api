import os

from vng_api_common.conf.api import *  # noqa - imports white-listed

API_VERSION = "1.2.2"

REST_FRAMEWORK = BASE_REST_FRAMEWORK.copy()
REST_FRAMEWORK["PAGE_SIZE"] = 100

SECURITY_DEFINITION_NAME = "JWT-Claims"

DOCUMENTATION_INFO_MODULE = "drc.api.schema"

SPECTACULAR_SETTINGS = BASE_SPECTACULAR_SETTINGS.copy()
SPECTACULAR_SETTINGS.update(
    {
        # Optional list of servers.
        # Each entry MUST contain "url", MAY contain "description", "variables"
        # e.g. [{'url': 'https://example.com/v1', 'description': 'Text'}, ...]
        "SERVERS": [
            {
                "url": "https://documenten-api.vng.cloud/api/v1",
                "description": "Productie Omgeving",
            }
        ],
        "COMPONENT_SPLIT_REQUEST": True,
        "SORT_OPERATION_PARAMETERS": False,
    }
)

SPECTACULAR_EXTENSIONS = [
    "vng_api_common.extensions.fields.hyperlink_identity.HyperlinkedIdentityFieldExtension",
    "vng_api_common.extensions.fields.many_related.ManyRelatedFieldExtension",
    "vng_api_common.extensions.fields.read_only.ReadOnlyFieldExtension",
    "vng_api_common.extensions.filters.query.FilterExtension",
    "vng_api_common.extensions.serializers.gegevensgroep.GegevensGroepExtension",
    "vng_api_common.extensions.fields.files.FileFieldExtension",
]

DRF_EXCLUDED_ENDPOINTS.extend(["413.json", "500.json"])

GEMMA_URL_INFORMATIEMODEL_VERSIE = "1.0"

ztc_repo = "vng-Realisatie/catalogi-api"
ztc_commit = "3f672a7e1c03a2e415df4209b0e9fa7c32ce41e4"
ZTC_API_SPEC = f"https://raw.githubusercontent.com/{ztc_repo}/{ztc_commit}/src/openapi.yaml"  # noqa

zrc_repo = "vng-Realisatie/zaken-api"
zrc_commit = "8ea1950fe4ec2ad99504d345eba60a175eea3edf"
ZRC_API_SPEC = f"https://raw.githubusercontent.com/{zrc_repo}/{zrc_commit}/src/openapi.yaml"  # noqa

brc_repo = "vng-Realisatie/besluiten-api"
brc_commit = "87dde6338e6417f307d1d935983ce50466d77f48"
BRC_API_SPEC = f"https://raw.githubusercontent.com/{brc_repo}/{brc_commit}/src/openapi.yaml"  # noqa

SELF_REPO = "VNG-Realisatie/gemma-documentregistratiecomponent"
SELF_BRANCH = os.getenv("SELF_BRANCH") or API_VERSION
GITHUB_API_SPEC = f"https://raw.githubusercontent.com/{SELF_REPO}/{SELF_BRANCH}/src/openapi.yaml"  # noqa
