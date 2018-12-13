import tempfile
import uuid
from base64 import b64encode
from datetime import date

from django.test import override_settings
from django.urls import reverse, reverse_lazy

from freezegun import freeze_time
from rest_framework import status
from rest_framework.test import APITestCase

from drc.datamodel.models import EnkelvoudigInformatieObject
from drc.datamodel.tests.factories import EnkelvoudigInformatieObjectFactory


@freeze_time('2018-06-27')
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class EnkelvoudigInformatieObjectAPITests(APITestCase):

    list_url = reverse_lazy('enkelvoudiginformatieobject-list', kwargs={'version': '1'})

    @override_settings(LINK_FETCHER='zds_schema.mocks.link_fetcher_200')
    def test_create(self):
        content = {
            'identificatie': uuid.uuid4().hex,
            'bronorganisatie': '159351741',
            'creatiedatum': '2018-06-27',
            'titel': 'detailed summary',
            'auteur': 'test_auteur',
            'formaat': 'txt',
            'taal': 'eng',
            'bestandsnaam': 'dummy.txt',
            'inhoud': b64encode(b'some file content').decode('utf-8'),
            'link': 'http://een.link',
            'beschrijving': 'test_beschrijving',
            'informatieobjecttype': 'https://example.com/ztc/api/v1/catalogus/1/informatieobjecttype/1',
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
        self.assertEqual(stored_object.bestandsnaam, 'dummy.txt')
        self.assertEqual(stored_object.inhoud.read(), b'some file content')
        self.assertEqual(stored_object.link, 'http://een.link')
        self.assertEqual(stored_object.beschrijving, 'test_beschrijving')
        self.assertEqual(
            stored_object.informatieobjecttype,
            'https://example.com/ztc/api/v1/catalogus/1/informatieobjecttype/1'
        )
        self.assertEqual(stored_object.vertrouwelijkaanduiding, '')

        expected_url = reverse('enkelvoudiginformatieobject-detail', kwargs={
            'version': '1',
            'uuid': stored_object.uuid,
        })

        expected_response = content.copy()
        expected_response.update({
            'url': f"http://testserver{expected_url}",
            'inhoud': f"http://testserver{stored_object.inhoud.url}",
            'vertrouwelijkaanduiding': '',
            'bestandsomvang': stored_object.inhoud.size,
            'integriteit': {
                'algoritme': '',
                'waarde': '',
                'datum': None,
            }
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
            'bestandsnaam': '',
            'inhoud': f'http://testserver{test_object.inhoud.url}',
            'bestandsomvang': test_object.inhoud.size,
            'link': '',
            'beschrijving': '',
            'vertrouwelijkaanduiding': '',
            'integriteit': {
                'algoritme': '',
                'waarde': '',
                'datum': None,
            },
            'informatieobjecttype': 'https://example.com/ztc/api/v1/catalogus/1/informatieobjecttype/1'
        }
        self.assertEqual(response.json(), expected)

    def test_bestandsomvang(self):
        """
        Assert that the API shows the filesize.
        """
        test_object = EnkelvoudigInformatieObjectFactory.create(
            inhoud__data=b'some content'
        )

        # Retrieve from the API
        detail_url = reverse('enkelvoudiginformatieobject-detail', kwargs={
            'version': '1',
            'uuid': test_object.uuid,
        })

        response = self.client.get(detail_url)

        # Test response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['bestandsomvang'], 12)  # 12 bytes

    @override_settings(LINK_FETCHER='zds_schema.mocks.link_fetcher_200')
    def test_integrity_empty(self):
        """
        Assert that integrity is optional.
        """
        content = {
            'identificatie': uuid.uuid4().hex,
            'bronorganisatie': '159351741',
            'creatiedatum': '2018-12-13',
            'titel': 'Voorbeelddocument',
            'auteur': 'test_auteur',
            'formaat': 'text/plain',
            'taal': 'eng',
            'bestandsnaam': 'dummy.txt',
            'inhoud': b64encode(b'some file content').decode('utf-8'),
            'informatieobjecttype': 'https://example.com/ztc/api/v1/catalogus/1/informatieobjecttype/1',
            'integriteit': None,
        }

        # Send to the API
        response = self.client.post(self.list_url, content)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        stored_object = EnkelvoudigInformatieObject.objects.get()
        self.assertEqual(stored_object.integriteit, {
            "algoritme": "",
            "waarde": "",
            "datum": None,
        })

    @override_settings(LINK_FETCHER='zds_schema.mocks.link_fetcher_200')
    def test_integrity_provided(self):
        """
        Assert that integrity is saved.
        """
        content = {
            'identificatie': uuid.uuid4().hex,
            'bronorganisatie': '159351741',
            'creatiedatum': '2018-12-13',
            'titel': 'Voorbeelddocument',
            'auteur': 'test_auteur',
            'formaat': 'text/plain',
            'taal': 'eng',
            'bestandsnaam': 'dummy.txt',
            'inhoud': b64encode(b'some file content').decode('utf-8'),
            'informatieobjecttype': 'https://example.com/ztc/api/v1/catalogus/1/informatieobjecttype/1',
            'integriteit': {
                "algoritme": "MD5",
                "waarde": "27c3a009a3cbba674d0b3e836f2d4685",
                "datum": "2018-12-13",
            },
        }

        # Send to the API
        response = self.client.post(self.list_url, content)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        stored_object = EnkelvoudigInformatieObject.objects.get()
        self.assertEqual(stored_object.integriteit, {
            "algoritme": "MD5",
            "waarde": "27c3a009a3cbba674d0b3e836f2d4685",
            "datum": date(2018, 12, 13),
        })
