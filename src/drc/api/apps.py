from django.apps import AppConfig


class DRCApiConfig(AppConfig):
    name = "drc.api"

    def ready(self):
        # ensure that the metaclass for every viewset has run
        from . import viewsets  # noqa
