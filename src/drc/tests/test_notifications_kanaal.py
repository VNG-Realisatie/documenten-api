from io import StringIO
from unittest.mock import call, patch

from django.core.management import call_command
from django.test import override_settings

from notifications_api_common.kanalen import Kanaal
from rest_framework.test import APITestCase

from drc.api.tests.mixins import NotificationsConfigMixin
from drc.datamodel.models import EnkelvoudigInformatieObject


@override_settings(IS_HTTPS=True)
class CreateNotifKanaalTestCase(NotificationsConfigMixin, APITestCase):
    @patch("notifications_api_common.models.NotificationsConfig.get_client")
    def test_kanaal_create_with_name(self, mock_client):
        """
        Test is request to create kanaal is send with specified kanaal name
        """
        client = mock_client.return_value
        client.list.return_value = []
        # ensure this is added to the registry
        Kanaal(label="kanaal_test", main_resource=EnkelvoudigInformatieObject)

        stdout = StringIO()
        call_command(
            "register_kanalen",
            kanalen=["kanaal_test"],
            stdout=stdout,
        )

        client.create.assert_called_once_with(
            "kanaal",
            {
                "naam": "kanaal_test",
                "documentatieLink": "https://example.com/ref/kanalen/#kanaal_test",
                "filters": [],
            },
        )

    @patch("notifications_api_common.models.NotificationsConfig.get_client")
    def test_kanaal_create_without_name(self, mock_client):
        """
        Test is request to create kanaal is send with default kanaal name
        """
        client = mock_client.return_value
        client.list.return_value = []

        # ensure this is added to the registry
        Kanaal(label="dummy-kanaal", main_resource=EnkelvoudigInformatieObject)

        stdout = StringIO()
        call_command("register_kanalen", stdout=stdout)

        client.create.assert_has_calls(
            [
                call(
                    "kanaal",
                    {
                        "naam": "documenten",
                        "documentatieLink": "https://example.com/ref/kanalen/#documenten",
                        "filters": [
                            "bronorganisatie",
                            "informatieobjecttype",
                            "vertrouwelijkheidaanduiding",
                        ],
                    },
                ),
                call(
                    "kanaal",
                    {
                        "naam": "dummy-kanaal",
                        "documentatieLink": "https://example.com/ref/kanalen/#dummy-kanaal",
                        "filters": [],
                    },
                ),
            ]
        )
