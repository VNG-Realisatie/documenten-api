from django.test import override_settings

from rest_framework import status
from rest_framework.test import APITestCase
from zds_schema.tests import get_validation_errors
from zds_schema.validators import URLValidator

from .utils import reverse


class EnkelvoudigInformatieObjectTests(APITestCase):

    @override_settings(LINK_FETCHER='zds_schema.mocks.link_fetcher_404')
    def test_validate_informatieobjecttype_invalid(self):
        url = reverse('enkelvoudiginformatieobject-list')

        response = self.client.post(url, {
            'informatieobjecttype': 'https://example.com/informatieobjecttype/foo',
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error = get_validation_errors(response, 'informatieobjecttype')
        self.assertEqual(error['code'], URLValidator.code)

    def test_link_fetcher_cannot_connect(self):
        url = reverse('enkelvoudiginformatieobject-list')

        response = self.client.post(url, {
            'informatieobjecttype': 'http://invalid-host/informatieobjecttype/foo',
        })

        self.assertNotEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)


class FilterValidationTests(APITestCase):
    """
    Test that incorrect filter usage results in HTTP 400.
    """

    def test_oio_invalid_filters(self):
        url = reverse('objectinformatieobject-list')

        invalid_filters = {
            'object': '123',  # must be url
            'informatieobject': '123',  # must be url
            'foo': 'bar',  # unknown
        }

        for key, value in invalid_filters.items():
            with self.subTest(query_param=key, value=value):
                response = self.client.get(url, {key: value}, HTTP_ACCEPT_CRS='EPSG:4326')
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
