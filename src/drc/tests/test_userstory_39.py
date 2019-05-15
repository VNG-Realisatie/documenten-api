"""
Test the flow described in https://github.com/VNG-Realisatie/gemma-zaken/issues/39
"""

import base64
import tempfile
from datetime import date
from urllib.parse import urlparse

from django.conf import settings
from django.test import override_settings

from rest_framework import status
from rest_framework.test import APITestCase
from vng_api_common.constants import VertrouwelijkheidsAanduiding
from vng_api_common.tests import JWTAuthMixin, get_operation_url

from drc.api.scopes import (
    SCOPE_DOCUMENTEN_AANMAKEN, SCOPE_DOCUMENTEN_ALLES_LEZEN
)
from drc.datamodel.models import EnkelvoudigInformatieObject
from drc.datamodel.tests.factories import EnkelvoudigInformatieObjectFactory

INFORMATIEOBJECTTYPE = 'https://example.com/ztc/api/v1/catalogus/1/informatieobjecttype/1'


@override_settings(PRIVATE_STORAGE_ROOT=tempfile.mkdtemp())
class US39TestCase(JWTAuthMixin, APITestCase):

    scopes = [SCOPE_DOCUMENTEN_AANMAKEN]
    informatieobjecttype = INFORMATIEOBJECTTYPE

    @override_settings(LINK_FETCHER='vng_api_common.mocks.link_fetcher_200')
    def test_create_enkelvoudiginformatieobject(self):
        """
        Registreer een ENKELVOUDIGINFORMATIEOBJECT
        """
        url = get_operation_url('enkelvoudiginformatieobject_create')
        data = {
            'identificatie': 'AMS20180701001',
            'bronorganisatie': '159351741',
            'creatiedatum': '2018-07-01',
            'titel': 'text_extra.txt',
            'auteur': 'ANONIEM',
            'formaat': 'text/plain',
            'taal': 'dut',
            'inhoud': base64.b64encode(b'Extra tekst in bijlage').decode('utf-8'),
            'informatieobjecttype': INFORMATIEOBJECTTYPE,
            'vertrouwelijkheidaanduiding': VertrouwelijkheidsAanduiding.openbaar
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        data = response.json()
        self.assertIn('identificatie', data)

        eio = EnkelvoudigInformatieObject.objects.get()
        self.assertEqual(eio.identificatie, 'AMS20180701001')
        self.assertEqual(eio.creatiedatum, date(2018, 7, 1))

        # should be a URL
        download_url = urlparse(response.data['inhoud'])
        self.assertTrue(download_url.path.startswith('/private-media/'))
        self.assertTrue(download_url.path.endswith('.bin'))

    def test_read_file_success(self):
        self.autorisatie.scopes = [SCOPE_DOCUMENTEN_ALLES_LEZEN]
        self.autorisatie.save()

        test_object = EnkelvoudigInformatieObjectFactory.create()
        detail_url = get_operation_url('enkelvoudiginformatieobject_read', uuid=test_object.uuid)

        response = self.client.get(detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_file = self.client.get(response.data['inhoud'])

        self.assertEqual(response_file.status_code, status.HTTP_200_OK)
        self.assertEqual(list(response_file.streaming_content)[0].decode("utf-8"), 'some data')

    def test_read_file_incorrect_scope(self):
        self.autorisatie.scopes = [SCOPE_DOCUMENTEN_ALLES_LEZEN]
        self.autorisatie.save()

        test_object = EnkelvoudigInformatieObjectFactory.create()
        detail_url = get_operation_url('enkelvoudiginformatieobject_read', uuid=test_object.uuid)

        response = self.client.get(detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.autorisatie.scopes = [SCOPE_DOCUMENTEN_AANMAKEN]
        self.autorisatie.save()

        response_file = self.client.get(response.data['inhoud'])

        self.assertEqual(response_file.status_code, status.HTTP_403_FORBIDDEN)
