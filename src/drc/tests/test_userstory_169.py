"""
Test that images can be uploaded as base64 with meta information.

See:
* https://github.com/VNG-Realisatie/gemma-zaken/issues/169 (us)
* https://github.com/VNG-Realisatie/gemma-zaken/issues/182 (mapping)
"""
import base64
from io import BytesIO

from django.test import override_settings

from PIL import Image
from rest_framework import status
from rest_framework.test import APITestCase
from zds_schema.constants import VertrouwelijkheidsAanduiding
from zds_schema.tests import TypeCheckMixin, get_operation_url


class US169Tests(TypeCheckMixin, APITestCase):

    @override_settings(LINK_FETCHER='zds_schema.mocks.link_fetcher_200')
    def test_upload_image(self):
        url = get_operation_url('enkelvoudiginformatieobject_create')

        # create dummy image in memory
        image = Image.new('RGB', (1, 1), 'red')
        image_io = BytesIO()
        image.save(image_io, format='JPEG')

        image_data = base64.b64encode(image_io.getvalue())

        data = {
            'inhoud': image_data.decode('utf-8'),
            'bronorganisatie': '715832694',
            'taal': 'dut',
            'creatiedatum': '2018-07-30',
            'titel': 'bijlage.jpg',
            'vertrouwelijkaanduiding': VertrouwelijkheidsAanduiding.openbaar,
            'auteur': 'John Doe',
            'informatieobjecttype': 'https://example.com/ztc/api/v1/catalogus/1/informatieobjecttype/1',
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.json())

        response_data = response.json()
        self.assertIn('identificatie', response_data)

        self.assertResponseTypes(response_data, (
            ('url', str),
            ('inhoud', str),
            ('bronorganisatie', str),
            ('taal', str),
            ('creatiedatum', str),
            ('titel', str),
            ('vertrouwelijkaanduiding', str),
            ('auteur', str),
            ('informatieobjecttype', str),
        ))
