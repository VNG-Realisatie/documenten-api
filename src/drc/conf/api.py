from zds_schema.conf.api import *  # noqa - imports white-listed

REST_FRAMEWORK = BASE_REST_FRAMEWORK.copy()

SECURITY_DEFINITION_NAME = 'JWT-Claims'

SWAGGER_SETTINGS = BASE_SWAGGER_SETTINGS.copy()
SWAGGER_SETTINGS.update({
    'DEFAULT_INFO': 'drc.api.schema.info',

    'SECURITY_DEFINITIONS': {
        SECURITY_DEFINITION_NAME: {
            # OAS 3.0
            'type': 'http',
            'scheme': 'bearer',
            'bearerFormat': 'JWT',
            # not official...
            # 'scopes': {},  # TODO: set up registry that's filled in later...

            # Swagger 2.0
            # 'name': 'Authorization',
            # 'in': 'header'
            # 'type': 'apiKey',
        }
    },

    # no geo things here
    'DEFAULT_FIELD_INSPECTORS': (
        'zds_schema.inspectors.files.FileFieldInspector',
    ) + BASE_SWAGGER_SETTINGS['DEFAULT_FIELD_INSPECTORS'][1:]
})

GEMMA_URL_INFORMATIEMODEL_VERSIE = '1.0'
