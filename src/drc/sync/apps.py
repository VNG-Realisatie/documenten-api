from django.apps import AppConfig


class SyncConfig(AppConfig):
    name = 'drc.sync'

    def ready(self):
        from . import signals  # noqa
