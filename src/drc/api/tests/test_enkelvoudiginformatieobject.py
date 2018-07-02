import os
import uuid
from base64 import b64encode
from datetime import datetime

from django.urls import reverse

from freezegun import freeze_time
from rest_framework import status
from rest_framework.test import APITestCase

from drc.datamodel.models import EnkelvoudigInformatieObject
from drc.datamodel.tests.factories import EnkelvoudigInformatieObjectFactory


@freeze_time('2018-06-27')
class EnkelvoudigInformatieObjectAPITests(APITestCase):

    def setUp(self):

        self.API_VERSION = 1

        self.test_object = EnkelvoudigInformatieObjectFactory.create()

        self.enkelvoudiginformatieobject_list_url = reverse('enkelvoudiginformatieobject-list', kwargs={
            'version': self.API_VERSION,
        })

        self.file_path = 'dummy.txt'
        with open(self.file_path, 'w') as tmp:
            tmp.write('some file content')
        self.file = open(self.file_path, 'rb')

    def tearDown(self):
        os.remove(self.file_path)

    def test_create(self):

        byte_content = self.file.read()
        base64_bytes = b64encode(byte_content)
        base64_string = base64_bytes.decode('utf-8')

        content = {
            'identificatie': uuid.uuid4().hex,
            'bronorganisatie': '2',
            'creatiedatum': '2018-06-27',
            'titel': 'detailed summary',
            'auteur': 'test_auteur',
            'formaat': 'txt',
            'taal': 'english',
            'inhoud': base64_string,
        }

        # Send to the API

        response = self.client.post(
            self.enkelvoudiginformatieobject_list_url,
            content,
            format='json')

        # Test database

        self.assertEqual(EnkelvoudigInformatieObject.objects.count(), 2)
        stored_object = EnkelvoudigInformatieObject.objects.get(pk=2)

        self.assertEqual(stored_object.identificatie, content['identificatie'])
        self.assertEqual(stored_object.bronorganisatie, content['bronorganisatie'])
        self.assertEqual(stored_object.creatiedatum, datetime.strptime(content['creatiedatum'], '%Y-%m-%d').date())
        self.assertEqual(stored_object.titel, content['titel'])
        self.assertEqual(stored_object.auteur, content['auteur'])
        self.assertEqual(stored_object.formaat, content['formaat'])
        self.assertEqual(stored_object.taal, content['taal'])
        self.assertEqual(stored_object.inhoud.read(), byte_content)

        # Test response

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        expected_url = reverse('enkelvoudiginformatieobject-detail', kwargs={
            'version': self.API_VERSION,
            'pk': 2,
        })

        expected_response = content
        expected_response['url'] = 'http://testserver' + expected_url
        expected_response['inhoud'] = 'http://testserver' + stored_object.inhoud.url

        self.assertIsInstance(response.json(), dict)
        self.assertEqual(response.json(), expected_response)

    def test_read(self):

        # Retrieve from the API

        test_object_detail_url = reverse('enkelvoudiginformatieobject-detail', kwargs={
            'version': self.API_VERSION,
            'pk': self.test_object.pk,
        })
        response = self.client.get(test_object_detail_url)

        # Test response

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.json(), dict)

        expected = {
            'identificatie': self.test_object.identificatie,
            'bronorganisatie': '1',
            'creatiedatum': '2018-06-27',
            'titel': 'some titel',
            'auteur': 'some auteur',
            'formaat': 'some formaat',
            'taal': 'some taal',
            'inhoud': 'http://testserver' + self.test_object.inhoud.url,
            'url': 'http://testserver' + test_object_detail_url,
        }

        self.assertEqual(response.json(), expected)
