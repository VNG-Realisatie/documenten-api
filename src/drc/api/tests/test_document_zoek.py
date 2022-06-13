from rest_framework import status
from rest_framework.test import APITestCase
from vng_api_common.tests import (
    JWTAuthMixin,
    TypeCheckMixin,
    get_operation_url,
    get_validation_errors,
    reverse,
)

from drc.datamodel.tests.factories import EnkelvoudigInformatieObjectFactory


class ObjectInformatieObjectZoekTests(JWTAuthMixin, TypeCheckMixin, APITestCase):
    heeft_alle_autorisaties = True

    def test_zoek_uuid_in(self):
        eio1, eio2, eio3 = EnkelvoudigInformatieObjectFactory.create_batch(3)
        # todo add to api spec
        # url = get_operation_url("enkelvoudiginformatieobject__zoek")
        data = {"uuid__in": [eio1.uuid, eio2.uuid]}
        url = "/api/v1/enkelvoudiginformatieobjecten/_zoek"
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]
        data = sorted(data, key=lambda eio: eio["identificatie"])

        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["url"], f"http://testserver{reverse(eio1)}")
        self.assertEqual(data[1]["url"], f"http://testserver{reverse(eio2)}")

    def test_zoek_without_params(self):
        # url = get_operation_url("enkelvoudiginformatieobject__zoek")
        url = "/api/v1/enkelvoudiginformatieobjecten/_zoek"

        response = self.client.post(url, {})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error = get_validation_errors(response, "nonFieldErrors")
        self.assertEqual(error["code"], "empty_search_body")
