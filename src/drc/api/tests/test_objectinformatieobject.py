from unittest import skip

from django.test import override_settings

from rest_framework import status
from rest_framework.test import APITestCase
from vng_api_common.tests import JWTAuthMixin
from zds_client.tests.mocks import mock_client

from drc.datamodel.tests.factories import EnkelvoudigInformatieObjectFactory

from .utils import reverse

ZAAK = 'https://zrc.nl/api/v1/zaken/1234'

ZAAK_RESPONSE = {
    ZAAK: {
        'url': ZAAK
    }
}

@override_settings(
    LINK_FETCHER='vng_api_common.mocks.link_fetcher_200',
    ZDS_CLIENT_CLASS='vng_api_common.mocks.ZaakInformatieObjectClient'
)
class ObjectInformatieObjectTests(JWTAuthMixin, APITestCase):
    heeft_alle_autorisaties = True

    def test_create(self):
        eio = EnkelvoudigInformatieObjectFactory.create()
        eio_url = reverse('enkelvoudiginformatieobject-detail', kwargs={
            'uuid': eio.uuid,
        })

        url = reverse('objectinformatieobject-list')

        # with mock_client(ZAAK_RESPONSE):
        response = self.client.post(url, {
            'object': ZAAK,
            'informatieobject': f'http://testserver{eio_url}',
            'objectType': 'zaak'
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        zio = eio.objectinformatieobject_set.get()
        self.assertEqual(zio.object, ZAAK)

    @skip('HTTP DELETE is currently not supported')
    def test_delete(self):
        oio = ObjectInformatieObjectFactory.create()
        object = oio.object
        url = reverse('objectinformatieobject-detail', kwargs={
            'zaak_uuid': object.uuid,
            'uuid': oio.uuid
        })

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(zaak.objectinformatieobject_set.exists())
