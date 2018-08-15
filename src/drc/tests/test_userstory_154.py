"""
Test filtering ZaakInformatieObject on Zaak.

See:
* https://github.com/VNG-Realisatie/gemma-zaken/issues/154 (us)
* https://github.com/VNG-Realisatie/gemma-zaken/issues/239 (mapping)
"""
from rest_framework import status
from rest_framework.test import APITestCase
from zds_schema.tests import TypeCheckMixin, get_operation_url

from drc.datamodel.tests.factories import ZaakInformatieObjectFactory


class US154Tests(TypeCheckMixin, APITestCase):

    def test_informatieobjecttype_filter(self):
        zaak_url = 'http://www.example.com/zrc/api/v1/zaken/1'

        ZaakInformatieObjectFactory.create_batch(2, zaak=zaak_url)
        ZaakInformatieObjectFactory.create(zaak='http://www.example.com/zrc/api/v1/zaken/2')

        url = get_operation_url('zaakinformatieobject_list')

        response = self.client.get(url, {'zaak': zaak_url})

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())

        response_data = response.json()
        self.assertEqual(len(response_data), 2)

        for zio in response_data:
            self.assertEqual(zio['zaak'], zaak_url)
