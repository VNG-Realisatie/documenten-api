from rest_framework import status
from rest_framework.test import APITestCase
from vng_api_common.tests import JWTAuthMixin, get_operation_url, get_validation_errors

from drc.datamodel.tests.factories import (
    EnkelvoudigInformatieObjectCanonicalFactory,
    EnkelvoudigInformatieObjectFactory,
    GebruiksrechtenFactory,
)

from .utils import reverse

INFORMATIEOBJECTTYPE = "https://example.com/informatieobjecttype/foo"


class GebruiksrechtenTests(JWTAuthMixin, APITestCase):
    heeft_alle_autorisaties = True

    def test_create(self):
        url = reverse("gebruiksrechten-list")
        eio = EnkelvoudigInformatieObjectCanonicalFactory.create(
            latest_version__creatiedatum="2018-12-24",
            latest_version__informatieobjecttype=INFORMATIEOBJECTTYPE,
        )
        eio_url = reverse(
            "enkelvoudiginformatieobject-detail",
            kwargs={"uuid": eio.latest_version.uuid},
        )

        eio_detail = self.client.get(eio_url)

        self.assertIsNone(eio_detail.json()["indicatieGebruiksrecht"])

        response = self.client.post(
            url,
            {
                "informatieobject": eio_url,
                "startdatum": "2018-12-24T00:00:00Z",
                "omschrijvingVoorwaarden": "Een hele set onredelijke voorwaarden",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # ensure that the indication is updated now
        eio_detail = self.client.get(eio_url)
        self.assertTrue(eio_detail.json()["indicatieGebruiksrecht"])

    def test_block_clearing_indication(self):
        """
        If gebruiksrechten exist, you cannot change the indicatieGebruiksrechten
        anymore.
        """
        gebruiksrechten = GebruiksrechtenFactory.create(
            informatieobject__latest_version__informatieobjecttype=INFORMATIEOBJECTTYPE
        )
        url = reverse(
            "enkelvoudiginformatieobject-detail",
            kwargs={"uuid": gebruiksrechten.informatieobject.latest_version.uuid},
        )

        for invalid_value in (None, False):
            data = {"indicatieGebruiksrecht": invalid_value}
            response = self.client.patch(url, data)

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            error = get_validation_errors(response, "indicatieGebruiksrecht")
            self.assertEqual(error["code"], "existing-gebruiksrechten")

    def test_block_setting_indication_true(self):
        """
        Assert that it's not possible to set the indication to true if there are
        no gebruiksrechten.
        """
        eio = EnkelvoudigInformatieObjectFactory.create(
            informatieobjecttype=INFORMATIEOBJECTTYPE
        )
        url = reverse("enkelvoudiginformatieobject-detail", kwargs={"uuid": eio.uuid})

        response = self.client.patch(url, {"indicatieGebruiksrecht": True})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error = get_validation_errors(response, "indicatieGebruiksrecht")
        self.assertEqual(error["code"], "missing-gebruiksrechten")

    def test_delete_gebruiksrechten(self):
        gebruiksrechten = GebruiksrechtenFactory.create(
            informatieobject__latest_version__informatieobjecttype=INFORMATIEOBJECTTYPE
        )
        url = reverse("gebruiksrechten-detail", kwargs={"uuid": gebruiksrechten.uuid})
        eio_url = reverse(
            "enkelvoudiginformatieobject-detail",
            kwargs={"uuid": gebruiksrechten.informatieobject.latest_version.uuid},
        )

        eio_data = self.client.get(eio_url).json()
        self.assertTrue(eio_data["indicatieGebruiksrecht"])

        # delete the gebruiksrechten
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        eio_data = self.client.get(eio_url).json()
        self.assertIsNone(eio_data["indicatieGebruiksrecht"])

    def test_validate_unknown_query_params(self):
        GebruiksrechtenFactory.create_batch(2)
        url = get_operation_url("gebruiksrechten_list")

        response = self.client.get(url, {"someparam": "somevalue"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error = get_validation_errors(response, "nonFieldErrors")
        self.assertEqual(error["code"], "unknown-parameters")

    def test_filter_invalid_resource_url(self):
        GebruiksrechtenFactory.create()
        url = get_operation_url("gebruiksrechten_list")

        bad_urls = [
            "https://google.nl",
            "https://example.com/",
            "https://example.com/404",
        ]
        for bad_url in bad_urls:
            with self.subTest(bad_url=bad_url):
                response = self.client.get(url, {"informatieobject": bad_url})

                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(len(response.data), 0)
