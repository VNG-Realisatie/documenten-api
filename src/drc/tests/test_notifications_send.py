import base64
from unittest.mock import patch

from django.test import override_settings

from freezegun import freeze_time
from rest_framework import status
from rest_framework.test import APITestCase
from vng_api_common.constants import VertrouwelijkheidsAanduiding
from vng_api_common.tests import JWTAuthMixin, get_operation_url

from drc.api.scopes import SCOPE_DOCUMENTEN_AANMAKEN, SCOPE_DOCUMENTEN_ALLES_VERWIJDEREN

INFORMATIEOBJECTTYPE = (
    "https://example.com/ztc/api/v1/catalogus/1/informatieobjecttype/1"
)


@freeze_time("2012-01-14")
@override_settings(
    LINK_FETCHER="vng_api_common.mocks.link_fetcher_200", NOTIFICATIONS_DISABLED=False
)
class SendNotifTestCase(JWTAuthMixin, APITestCase):

    scopes = [SCOPE_DOCUMENTEN_AANMAKEN, SCOPE_DOCUMENTEN_ALLES_VERWIJDEREN]
    informatieobjecttype = INFORMATIEOBJECTTYPE

    @patch("vng_api_common.validators.fetcher")
    @patch("vng_api_common.validators.obj_has_shape", return_value=True)
    @patch("zds_client.Client.from_url")
    def test_send_notif_create_enkelvoudiginformatieobject(self, mock_client, *mocks):
        """
        Registreer een ENKELVOUDIGINFORMATIEOBJECT
        """
        client = mock_client.return_value
        url = get_operation_url("enkelvoudiginformatieobject_create")
        data = {
            "identificatie": "AMS20180701001",
            "bronorganisatie": "159351741",
            "creatiedatum": "2018-07-01",
            "titel": "text_extra.txt",
            "auteur": "ANONIEM",
            "formaat": "text/plain",
            "taal": "dut",
            "inhoud": base64.b64encode(b"Extra tekst in bijlage").decode("utf-8"),
            "informatieobjecttype": INFORMATIEOBJECTTYPE,
            "vertrouwelijkheidaanduiding": VertrouwelijkheidsAanduiding.openbaar,
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

        data = response.json()
        client.create.assert_called_once_with(
            "notificaties",
            {
                "kanaal": "documenten",
                "hoofdObject": data["url"],
                "resource": "enkelvoudiginformatieobject",
                "resourceUrl": data["url"],
                "actie": "create",
                "aanmaakdatum": "2012-01-14T00:00:00Z",
                "kenmerken": {
                    "bronorganisatie": "159351741",
                    "informatieobjecttype": "https://example.com/ztc/api/v1/catalogus/1/informatieobjecttype/1",
                    "vertrouwelijkheidaanduiding": VertrouwelijkheidsAanduiding.openbaar,
                },
            },
        )
