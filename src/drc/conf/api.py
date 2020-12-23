import os

from vng_api_common.conf.api import *  # noqa - imports white-listed

API_VERSION = "1.0.1"

REST_FRAMEWORK = BASE_REST_FRAMEWORK.copy()
REST_FRAMEWORK["PAGE_SIZE"] = 100

SECURITY_DEFINITION_NAME = "JWT-Claims"

SWAGGER_SETTINGS = BASE_SWAGGER_SETTINGS.copy()
SWAGGER_SETTINGS.update(
    {
        "DEFAULT_INFO": "drc.api.schema.info",
        "SECURITY_DEFINITIONS": {
            SECURITY_DEFINITION_NAME: {
                # OAS 3.0
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                # not official...
                # 'scopes': {},  # TODO: set up registry that's filled in later...
                # Swagger 2.0
                # 'name': 'Authorization',
                # 'in': 'header'
                # 'type': 'apiKey',
            }
        },
        # no geo things here
        "DEFAULT_FIELD_INSPECTORS": (
            "vng_api_common.inspectors.files.FileFieldInspector",
        )
        + BASE_SWAGGER_SETTINGS["DEFAULT_FIELD_INSPECTORS"],
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
