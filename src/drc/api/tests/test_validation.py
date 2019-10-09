import uuid
from base64 import b64encode
from copy import deepcopy
from unittest.mock import patch

from django.test import override_settings

from privates.test import temp_private_root
from rest_framework import status
from rest_framework.test import APITestCase
from vng_api_common.tests import JWTAuthMixin, get_validation_errors, reverse
from vng_api_common.validators import URLValidator
from zds_client.tests.mocks import mock_client

from drc.datamodel.constants import OndertekeningSoorten, Statussen
from drc.datamodel.models import (
    EnkelvoudigInformatieObject, ObjectInformatieObject
)
from drc.datamodel.tests.factories import EnkelvoudigInformatieObjectFactory

from .utils import reverse_lazy

INFORMATIEOBJECTTYPE = 'https://example.com/informatieobjecttype/foo'
ZAAK = 'https://zrc.nl/api/v1/zaken/1234'
BESLUIT = 'https://brc.nl/api/v1/besluiten/4321'


class EnkelvoudigInformatieObjectTests(JWTAuthMixin, APITestCase):
    heeft_alle_autorisaties = True

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

    @override_settings(LINK_FETCHER='vng_api_common.mocks.link_fetcher_404')
    def test_validate_informatieobjecttype_invalid_url(self):
        url = reverse('enkelvoudiginformatieobject-list')

        response = self.client.post(url, {
            'informatieobjecttype': INFORMATIEOBJECTTYPE,
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error = get_validation_errors(response, 'informatieobjecttype')
        self.assertEqual(error['code'], URLValidator.code)

    @override_settings(LINK_FETCHER='vng_api_common.mocks.link_fetcher_200')
    def test_validate_informatieobjecttype_invalid_resource(self):
        responses = {
            INFORMATIEOBJECTTYPE: {
                'some': 'incorrect property'
            }
        }

        url = reverse('enkelvoudiginformatieobject-list')

        with mock_client(responses):
            response = self.client.post(url, {
                'informatieobjecttype': INFORMATIEOBJECTTYPE,
            })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error = get_validation_errors(response, 'informatieobjecttype')
        self.assertEqual(error['code'], 'invalid-resource')

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

    @temp_private_root()
    @override_settings(LINK_FETCHER='vng_api_common.mocks.link_fetcher_200')
    @patch("vng_api_common.validators.fetcher")
    @patch("vng_api_common.validators.obj_has_shape", return_value=True)
    def test_inhoud_incorrect_padding(self, *mocks):
        url = reverse('enkelvoudiginformatieobject-list')
        content = {
            'identificatie': uuid.uuid4().hex,
            'bronorganisatie': '159351741',
            'creatiedatum': '2018-06-27',
            'titel': 'detailed summary',
            'auteur': 'test_auteur',
            'formaat': 'txt',
            'taal': 'eng',
            'bestandsnaam': 'dummy.txt',
            # Remove padding from the base64 data
            'inhoud': b64encode(b'some file content').decode('utf-8')[:-1],
            'link': 'http://een.link',
            'beschrijving': 'test_beschrijving',
            'informatieobjecttype': INFORMATIEOBJECTTYPE,
            'vertrouwelijkheidaanduiding': 'openbaar',
        }

        # Send to the API
        response = self.client.post(url, content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error = get_validation_errors(response, 'inhoud')
        self.assertEqual(error['code'], 'incorrect-base64-padding')

    @temp_private_root()
    @override_settings(LINK_FETCHER='vng_api_common.mocks.link_fetcher_200')
    @patch("vng_api_common.validators.fetcher")
    @patch("vng_api_common.validators.obj_has_shape", return_value=True)
    def test_inhoud_correct_padding(self, *mocks):
        url = reverse('enkelvoudiginformatieobject-list')
        content = {
            'identificatie': uuid.uuid4().hex,
            'bronorganisatie': '159351741',
            'creatiedatum': '2018-06-27',
            'titel': 'detailed summary',
            'auteur': 'test_auteur',
            'formaat': 'txt',
            'taal': 'eng',
            'bestandsnaam': 'dummy.txt',
            # Remove padding from the base64 data
            'inhoud': b64encode(b'some file content').decode('utf-8'),
            'link': 'http://een.link',
            'beschrijving': 'test_beschrijving',
            'informatieobjecttype': INFORMATIEOBJECTTYPE,
            'vertrouwelijkheidaanduiding': 'openbaar',
        }

        # Send to the API
        response = self.client.post(url, content)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


@override_settings(LINK_FETCHER='vng_api_common.mocks.link_fetcher_200')
class InformatieObjectStatusTests(JWTAuthMixin, APITestCase):

    url = reverse_lazy('enkelvoudiginformatieobject-list')
    heeft_alle_autorisaties = True

    @patch("vng_api_common.validators.fetcher")
    @patch("vng_api_common.validators.obj_has_shape", return_value=True)
    def test_ontvangen_informatieobjecten(self, *mocks):
        """
        Assert certain statuses are not allowed for received documents.

        RGBZ 2.00.02 deel II Concept 20180613: De waarden ?in bewerking?
        en ?ter vaststelling? zijn niet van toepassing op ontvangen
        informatieobjecten.
        """
        invalid_statuses = (Statussen.in_bewerking, Statussen.ter_vaststelling)
        data = {
            'bronorganisatie': '319582462',
            'creatiedatum': '2018-12-24',
            'titel': 'dummy',
            'auteur': 'dummy',
            'taal': 'nld',
            'inhoud': 'aGVsbG8gd29ybGQ=',
            'informatieobjecttype': INFORMATIEOBJECTTYPE,
            'ontvangstdatum': '2018-12-24',
        }

        for invalid_status in invalid_statuses:
            with self.subTest(status=invalid_status):
                _data = data.copy()
                _data['status'] = invalid_status

                response = self.client.post(self.url, _data)

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            error = get_validation_errors(response, 'status')
            self.assertEqual(error['code'], 'invalid_for_received')

    def test_informatieobjecten_niet_ontvangen(self):
        """
        All statusses should be allowed when the informatieobject doesn't have
        a receive date.
        """
        for valid_status, _ in Statussen.choices:
            with self.subTest(status=status):
                data = {
                    'ontvangstdatum': None,
                    'status': valid_status
                }

                response = self.client.post(self.url, data)

            error = get_validation_errors(response, 'status')
            self.assertIsNone(error)

    def test_status_set_ontvangstdatum_is_set_later(self):
        """
        Assert that setting the ontvangstdatum later, after an 'invalid' status
        has been set, is not possible.
        """
        eio = EnkelvoudigInformatieObjectFactory.create(
            ontvangstdatum=None,
            informatieobjecttype=INFORMATIEOBJECTTYPE
        )
        url = reverse('enkelvoudiginformatieobject-detail', kwargs={'uuid': eio.uuid})

        for invalid_status in (Statussen.in_bewerking, Statussen.ter_vaststelling):
            with self.subTest(status=invalid_status):
                eio.status = invalid_status
                eio.save()
                data = {'ontvangstdatum': '2018-12-24'}

                response = self.client.patch(url, data)

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                error = get_validation_errors(response, 'status')
                self.assertEqual(error['code'], 'invalid_for_received')

    @patch("vng_api_common.validators.fetcher")
    @patch("vng_api_common.validators.obj_has_shape", return_value=True)
    def test_update_eio_status_definitief_forbidden(self, *mocks):
        eio = EnkelvoudigInformatieObjectFactory.create(
            beschrijving='beschrijving1',
            informatieobjecttype=INFORMATIEOBJECTTYPE,
            status=Statussen.definitief
        )

        eio_url = reverse('enkelvoudiginformatieobject-detail', kwargs={
            'uuid': eio.uuid,
        })

        eio_response = self.client.get(eio_url)
        eio_data = eio_response.data

        lock = self.client.post(f'{eio_url}/lock').data['lock']
        eio_data.update({
            'beschrijving': 'beschrijving2',
            'inhoud': b64encode(b'aaaaa'),
            'lock': lock
        })

        for i in ['integriteit', 'ondertekening']:
            eio_data.pop(i)

        response = self.client.put(eio_url, eio_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error = get_validation_errors(response, "nonFieldErrors")
        self.assertEqual(error["code"], "modify-status-definitief")

    @patch("vng_api_common.validators.fetcher")
    @patch("vng_api_common.validators.obj_has_shape", return_value=True)
    def test_update_eio_old_version_forbidden_if_latest_version_is_definitief(self, *mocks):
        eio = EnkelvoudigInformatieObjectFactory.create(
            beschrijving='beschrijving1',
            informatieobjecttype=INFORMATIEOBJECTTYPE,
        )

        eio2 = EnkelvoudigInformatieObjectFactory.create(
            canonical=eio.canonical,
            versie=2,
            beschrijving='beschrijving1',
            informatieobjecttype=INFORMATIEOBJECTTYPE,
            status=Statussen.definitief
        )

        eio_url = reverse('enkelvoudiginformatieobject-detail', kwargs={
            'uuid': eio.uuid,
        })

        eio_response = self.client.get(eio_url)
        eio_data = eio_response.data

        lock = self.client.post(f'{eio_url}/lock').data['lock']
        eio_data.update({
            'beschrijving': 'beschrijving2',
            'inhoud': b64encode(b'aaaaa'),
            'lock': lock
        })

        for i in ['integriteit', 'ondertekening']:
            eio_data.pop(i)

        response = self.client.put(eio_url, eio_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error = get_validation_errors(response, "nonFieldErrors")
        self.assertEqual(error["code"], "modify-status-definitief")

class FilterValidationTests(JWTAuthMixin, APITestCase):
    """
    Test that incorrect filter usage results in HTTP 400.
    """
    heeft_alle_autorisaties = True

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


@override_settings(
    LINK_FETCHER='vng_api_common.mocks.link_fetcher_200',
)
class ObjectInformatieObjectValidationTests(JWTAuthMixin, APITestCase):
    heeft_alle_autorisaties = True

    list_url = reverse(ObjectInformatieObject)

    @patch('vng_api_common.validators.obj_has_shape', return_value=False)
    def test_create_oio_invalid_resource_zaak(self, *mocks):

        eio = EnkelvoudigInformatieObjectFactory.create()
        eio_url = reverse('enkelvoudiginformatieobject-detail', kwargs={
            'uuid': eio.uuid
        })

        response = self.client.post(self.list_url, {
            'object': ZAAK,
            'informatieobject': f'http://testserver{eio_url}',
            'objectType': 'zaak'
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error = get_validation_errors(response, 'object')
        self.assertEqual(error['code'], 'invalid-resource')

    @patch('vng_api_common.validators.obj_has_shape', return_value=False)
    def test_create_oio_invalid_resource_besluit(self, *mocks):

        eio = EnkelvoudigInformatieObjectFactory.create()
        eio_url = reverse('enkelvoudiginformatieobject-detail', kwargs={
            'uuid': eio.uuid
        })

        response = self.client.post(self.list_url, {
            'object': BESLUIT,
            'informatieobject': f'http://testserver{eio_url}',
            'objectType': 'besluit'
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error = get_validation_errors(response, 'object')
        self.assertEqual(error['code'], 'invalid-resource')
