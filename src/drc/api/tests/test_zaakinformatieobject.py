from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from drc.datamodel.models import ZaakInformatieObject
from drc.datamodel.tests.factories import (
    EnkelvoudigInformatieObjectFactory, ZaakInformatieObjectFactory
)

ZAAK = 'http://example.com/zrc/api/v1/zaak/1'


class ZaakInformatieObjectAPITests(APITestCase):

    def setUp(self):

        self.API_VERSION = 1

        self.test_zaak_informatie = ZaakInformatieObjectFactory.create(
            zaak=ZAAK)

        self.zaakinformatieobject_list_url = reverse('zaakinformatieobject-list', kwargs={
            'version': self.API_VERSION,
        })

    def test_create(self):

        enkelvoudig_informatie = EnkelvoudigInformatieObjectFactory.create()

        enkelvoudig_informatie_url = reverse('enkelvoudiginformatieobject-detail', kwargs={
            'version': self.API_VERSION,
            'pk': enkelvoudig_informatie.pk,
        })

        content = {
            'zaak': ZAAK,
            'informatieobject': 'http://testserver' + enkelvoudig_informatie_url,
        }

        # Send to the API

        response = self.client.post(
            self.zaakinformatieobject_list_url,
            content,
            format='json')

        # Test database

        self.assertEqual(ZaakInformatieObject.objects.count(), 2)
        stored_object = ZaakInformatieObject.objects.get(pk=2)

        self.assertEqual(stored_object.zaak, content['zaak'])

        # Test response

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        expected_url = reverse('zaakinformatieobject-detail', kwargs={
            'version': self.API_VERSION,
            'pk': 2,
        })

        expected_response = content
        expected_response['url'] = 'http://testserver' + expected_url

        self.assertIsInstance(response.json(), dict)
        self.assertEqual(response.json(), expected_response)

    def test_read(self):

        # Retrieve from the API

        test_zaak_informatie_detail_url = reverse('zaakinformatieobject-detail', kwargs={
            'version': self.API_VERSION,
            'pk': self.test_zaak_informatie.pk,
        })
        response = self.client.get(test_zaak_informatie_detail_url)

        # Test response

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.json(), dict)

        expected_enkelvoudig_informatie_url = reverse('enkelvoudiginformatieobject-detail', kwargs={
            'version': self.API_VERSION,
            'pk': self.test_zaak_informatie.informatieobject.pk,
        })

        expected = {
            'zaak': self.test_zaak_informatie.zaak,
            'informatieobject': 'http://testserver' + expected_enkelvoudig_informatie_url,
            'url': 'http://testserver' + test_zaak_informatie_detail_url,
        }

        self.assertEqual(response.json(), expected)
