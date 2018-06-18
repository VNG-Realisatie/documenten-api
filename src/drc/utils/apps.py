from django.apps import AppConfig


class UtilsConfig(AppConfig):
    name = 'drc.utils'

    def ready(self):
        from . import checks  # noqa
