from django.apps import AppConfig

from vng_api_common.api import register_extensions


class DRCApiConfig(AppConfig):
    name = "drc.api"

    def ready(self):
        # ensure that the metaclass for every viewset has run
        from . import views  # noqa

        register_extensions()
