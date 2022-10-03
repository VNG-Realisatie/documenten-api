from notifications_api_common.models import NotificationsConfig
from zgw_consumers.constants import APITypes, AuthTypes
from zgw_consumers.models import Service


class NotificationsConfigMixin:
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls._configure_notifications()

    @staticmethod
    def _configure_notifications(api_root=None):
        svc, _ = Service.objects.update_or_create(
            api_root=api_root or "https://notificaties-api.vng.cloud/api/v1/",
            defaults=dict(
                label="Notifications API",
                api_type=APITypes.nrc,
                client_id="some-client-id",
                secret="some-secret",
                auth_type=AuthTypes.zgw,
            ),
        )
        config = NotificationsConfig.get_solo()
        config.notifications_api_service = svc
        config.save()
