from copy import deepcopy

from django.test import override_settings

from rest_framework import status
from rest_framework.test import APITestCase
from zds_schema.tests import get_validation_errors
from zds_schema.validators import URLValidator

from drc.datamodel.constants import OndertekeningSoorten

from .utils import reverse


class EnkelvoudigInformatieObjectTests(APITestCase):

    def assertGegevensGroepRequired(self, url: str, field: str, base_body: dict, cases: tuple):
        for key, code in cases:
            with self.subTest(key=key, expected_code=code):
                body = deepcopy(base_body)
                del body[key]
                response = self.client.post(url, {field: body})

                error = get_validation_errors(response, f'{field}.{key}')
                self.assertEqual(error['code'], code)

    def assertGegevensGroepValidation(self, url: str, field: str, base_body: dict, cases: tuple):
        for key, code, blank_value in cases:
            with self.subTest(key=key, expected_code=code):
                body = deepcopy(base_body)
                body[key] = blank_value
                response = self.client.post(url, {field: body})

                error = get_validation_errors(response, f'{field}.{key}')
                self.assertEqual(error['code'], code)

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

    def test_integriteit(self):
        url = reverse('enkelvoudiginformatieobject-list')

        base_body = {
            'algoritme': 'MD5',
            'waarde': 'foobarbaz',
            'datum': '2018-12-13',
        }

        cases = (
            ('algoritme', 'required'),
            ('waarde', 'required'),
            ('datum', 'required'),
        )

        self.assertGegevensGroepRequired(url, 'integriteit', base_body, cases)

    def test_integriteit_bad_values(self):
        url = reverse('enkelvoudiginformatieobject-list')

        base_body = {
            'algoritme': 'MD5',
            'waarde': 'foobarbaz',
            'datum': '2018-12-13',
        }

        cases = (
            ('algoritme', 'invalid_choice', ''),
            ('waarde', 'blank', ''),
            ('datum', 'null', None),
        )

        self.assertGegevensGroepValidation(url, 'integriteit', base_body, cases)

    def test_ondertekening(self):
        url = reverse('enkelvoudiginformatieobject-list')

        base_body = {
            'soort': OndertekeningSoorten.analoog,
            'datum': '2018-12-13',
        }

        cases = (
            ('soort', 'required'),
            ('datum', 'required'),
        )

        self.assertGegevensGroepRequired(url, 'ondertekening', base_body, cases)

    def test_ondertekening_bad_values(self):
        url = reverse('enkelvoudiginformatieobject-list')

        base_body = {
            'soort': OndertekeningSoorten.digitaal,
            'datum': '2018-12-13',
        }
        cases = (
            ('soort', 'invalid_choice', ''),
            ('datum', 'null', None),
        )

        self.assertGegevensGroepValidation(url, 'ondertekening', base_body, cases)


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
