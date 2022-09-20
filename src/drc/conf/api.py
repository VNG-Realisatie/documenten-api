import os

from vng_api_common.conf.api import *  # noqa - imports white-listed

API_VERSION = "1.2.0-rc3"

REST_FRAMEWORK = BASE_REST_FRAMEWORK.copy()
REST_FRAMEWORK["PAGE_SIZE"] = 100

SECURITY_DEFINITION_NAME = "JWT-Claims"

SPECTACULAR_SETTINGS = BASE_SPECTACULAR_SETTINGS.copy()
SPECTACULAR_SETTINGS.update(
    {
        "COMPONENT_SPLIT_REQUEST": True,
        "POSTPROCESSING_HOOKS": [
            "drf_spectacular.hooks.postprocess_schema_enums",
            "drf_spectacular.contrib.djangorestframework_camel_case.camelize_serializer_fields",
        ],
        "SCHEMA_PATH_PREFIX": "/api/v1",
        "SERVERS": [{"url": "/api/v1"}],
        "EXTENSIONS_INFO": {},
        "PREPROCESSING_HOOKS": ["vng_api_common.utils.preprocessing_filter_spec"],
        "APPEND_COMPONENTS": {
            "securitySchemes": {
                "JWT-Claims": {
                    "type": "http",
                    "bearerFormat": "JWT",
                    "scheme": "bearer",
                }
            },
        },
        "SECURITY": [
            {
                "JWT-Claims": [],
            }
        ],
    }
)

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
