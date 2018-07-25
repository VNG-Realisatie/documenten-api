import uuid

from django.urls import reverse, reverse_lazy

from rest_framework import status
from rest_framework.test import APITestCase

from drc.datamodel.models import ZaakInformatieObject
from drc.datamodel.tests.factories import (
    EnkelvoudigInformatieObjectFactory, ZaakInformatieObjectFactory
)

ZAAK = f'http://example.com/zrc/api/v1/zaak/{uuid.uuid4().hex}'


class ZaakInformatieObjectAPITests(APITestCase):

    list_url = reverse_lazy('zaakinformatieobject-list', kwargs={'version': '1'})

    def test_create(self):
        enkelvoudig_informatie = EnkelvoudigInformatieObjectFactory.create()
        enkelvoudig_informatie_url = reverse('enkelvoudiginformatieobject-detail', kwargs={
            'version': '1',
            'uuid': enkelvoudig_informatie.uuid,
        })

        content = {
            'zaak': ZAAK,
            'informatieobject': 'http://testserver' + enkelvoudig_informatie_url,
        }

        # Send to the API
        response = self.client.post(self.list_url, content)

        # Test response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Test database
        self.assertEqual(ZaakInformatieObject.objects.count(), 1)
        stored_object = ZaakInformatieObject.objects.get()
        self.assertEqual(stored_object.zaak, ZAAK)

        expected_url = reverse('zaakinformatieobject-detail', kwargs={
            'version': '1',
            'uuid': stored_object.uuid,
        })

        expected_response = content.copy()
        expected_response['url'] = f'http://testserver{expected_url}'
        self.assertEqual(response.json(), expected_response)

    def test_read(self):
        zio = ZaakInformatieObjectFactory.create(zaak=ZAAK)
        # Retrieve from the API

        zio_detail_url = reverse('zaakinformatieobject-detail', kwargs={
            'version': '1',
            'uuid': zio.uuid,
        })
        response = self.client.get(zio_detail_url)

        # Test response
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        eo_detail_url = reverse('enkelvoudiginformatieobject-detail', kwargs={
            'version': '1',
            'uuid': zio.informatieobject.uuid,
        })

        expected = {
            'zaak': zio.zaak,
            'informatieobject': f'http://testserver{eo_detail_url}',
            'url': f'http://testserver{zio_detail_url}',
        }

        self.assertEqual(response.json(), expected)
