import uuid
from base64 import b64encode
from datetime import date

from django.urls import reverse, reverse_lazy

from freezegun import freeze_time
from rest_framework import status
from rest_framework.test import APITestCase

from drc.datamodel.models import EnkelvoudigInformatieObject
from drc.datamodel.tests.factories import EnkelvoudigInformatieObjectFactory


@freeze_time('2018-06-27')
class EnkelvoudigInformatieObjectAPITests(APITestCase):

    list_url = reverse_lazy('enkelvoudiginformatieobject-list', kwargs={'version': '1'})

    def test_create(self):
        content = {
            'identificatie': uuid.uuid4().hex,
            'bronorganisatie': '159351741',
            'creatiedatum': '2018-06-27',
            'titel': 'detailed summary',
            'auteur': 'test_auteur',
            'formaat': 'txt',
            'taal': 'eng',
            'inhoud': b64encode(b'some file content').decode('utf-8'),
        }

        # Send to the API
        response = self.client.post(self.list_url, content)

        # Test response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

        # Test database
        self.assertEqual(EnkelvoudigInformatieObject.objects.count(), 1)
        stored_object = EnkelvoudigInformatieObject.objects.get()

        self.assertEqual(stored_object.identificatie, content['identificatie'])
        self.assertEqual(stored_object.bronorganisatie, '159351741')
        self.assertEqual(stored_object.creatiedatum, date(2018, 6, 27))
        self.assertEqual(stored_object.titel, 'detailed summary')
        self.assertEqual(stored_object.auteur, 'test_auteur')
        self.assertEqual(stored_object.formaat, 'txt')
        self.assertEqual(stored_object.taal, 'eng')
        self.assertEqual(stored_object.inhoud.read(), b'some file content')

        expected_url = reverse('enkelvoudiginformatieobject-detail', kwargs={
            'version': '1',
            'uuid': stored_object.uuid,
        })

        expected_response = content.copy()
        expected_response.update({
            'url': f"http://testserver{expected_url}",
            'inhoud': f"http://testserver{stored_object.inhoud.url}",
            'vertrouwelijkheidsaanduiding': '',
        })
        self.assertEqual(response.json(), expected_response)

    def test_read(self):
        test_object = EnkelvoudigInformatieObjectFactory.create()

        # Retrieve from the API
        detail_url = reverse('enkelvoudiginformatieobject-detail', kwargs={
            'version': '1',
            'uuid': test_object.uuid,
        })

        response = self.client.get(detail_url)

        # Test response
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected = {
            'url': f'http://testserver{detail_url}',
            'identificatie': test_object.identificatie,
            'bronorganisatie': '1',
            'creatiedatum': '2018-06-27',
            'titel': 'some titel',
            'auteur': 'some auteur',
            'formaat': 'some formaat',
            'taal': 'dut',
            'inhoud': f'http://testserver{test_object.inhoud.url}',
            'vertrouwelijkheidsaanduiding': '',
        }
        self.assertEqual(response.json(), expected)
