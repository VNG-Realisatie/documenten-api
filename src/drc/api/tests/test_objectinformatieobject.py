from unittest import skip

from django.test import override_settings

from rest_framework import status
from rest_framework.test import APITestCase
from vng_api_common.constants import ObjectTypes
from vng_api_common.tests import JWTAuthMixin, get_validation_errors, reverse
from zds_client.tests.mocks import mock_client

from drc.datamodel.models import ObjectInformatieObject
from drc.datamodel.tests.factories import (
    EnkelvoudigInformatieObjectFactory, ObjectInformatieObjectFactory
)

ZAAK = 'https://zrc.nl/api/v1/zaken/1234'
BESLUIT = 'https://brc.nl/api/v1/besluiten/4321'

@override_settings(
    LINK_FETCHER='vng_api_common.mocks.link_fetcher_200',
    ZDS_CLIENT_CLASS='vng_api_common.mocks.RemoteInformatieObjectMockClient'
)
class ObjectInformatieObjectTests(JWTAuthMixin, APITestCase):
    heeft_alle_autorisaties = True

    list_url = reverse(ObjectInformatieObject)

    def test_create_with_objecttype_zaak(self):
        eio = EnkelvoudigInformatieObjectFactory.create()
        eio_url = reverse(eio)

        response = self.client.post(self.list_url, {
            'object': ZAAK,
            'informatieobject': f'http://testserver{eio_url}',
            'objectType': 'zaak'
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        zio = eio.objectinformatieobject_set.get()
        self.assertEqual(zio.object, ZAAK)

    def test_create_with_objecttype_besluit(self):
        eio = EnkelvoudigInformatieObjectFactory.create()
        eio_url = reverse(eio)

        response = self.client.post(self.list_url, {
            'object': BESLUIT,
            'informatieobject': f'http://testserver{eio_url}',
            'objectType': 'besluit'
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        bio = eio.objectinformatieobject_set.get()
        self.assertEqual(bio.object, BESLUIT)

    def test_delete(self):
        oio = ObjectInformatieObjectFactory.create()
        url = reverse(oio)

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ObjectInformatieObject.objects.exists())

    def test_duplicate_object(self):
        """
        Test the (informatieobject, object) unique together validation.
        """
        oio = ObjectInformatieObjectFactory.create(
            is_zaak=True,
        )
        enkelvoudig_informatie_url = reverse(oio.informatieobject)

        content = {
            'informatieobject': f'http://testserver{enkelvoudig_informatie_url}',
            'object': oio.object,
            'objectType': ObjectTypes.zaak,
        }

        # Send to the API
        response = self.client.post(self.list_url, content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)
        error = get_validation_errors(response, 'nonFieldErrors')
        self.assertEqual(error['code'], 'unique')

    def test_filter(self):
        oio = ObjectInformatieObjectFactory.create(
            is_zaak=True,
        )
        eo_detail_url = reverse(oio.informatieobject)

        response = self.client.get(self.list_url, {
            'informatieobject': f'http://testserver{eo_detail_url}',
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['informatieobject'], f'http://testserver{eo_detail_url}')
