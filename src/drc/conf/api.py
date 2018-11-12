import os

from zds_schema.conf.api import *  # noqa - imports white-listed

REST_FRAMEWORK = BASE_REST_FRAMEWORK.copy()


SWAGGER_SETTINGS = BASE_SWAGGER_SETTINGS.copy()
SWAGGER_SETTINGS.update({
    'DEFAULT_INFO': 'drc.api.schema.info',
    # no geo things here
    'DEFAULT_FIELD_INSPECTORS': (
        'zds_schema.inspectors.files.FileFieldInspector',
    ) + BASE_SWAGGER_SETTINGS['DEFAULT_FIELD_INSPECTORS'][1:]
})

GEMMA_URL_INFORMATIEMODEL_VERSIE = '1.0'

ZTC_JWT_CLIENT_ID = 'drc'
ZTC_JWT_SECRET = os.getenv('ZTC_JWT_SECRET')

ZRC_JWT_CLIENT_ID = 'drc'
ZRC_JWT_SECRET = os.getenv('ZRC_JWT_SECRET')
