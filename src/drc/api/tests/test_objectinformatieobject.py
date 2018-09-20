import uuid
from unittest.mock import patch

from django.test import override_settings
from django.urls import reverse, reverse_lazy

from freezegun import freeze_time
from rest_framework import status
from rest_framework.test import APITestCase
from zds_schema.constants import ObjectTypes
from zds_schema.tests import get_validation_errors
from zds_schema.validators import UntilNowValidator

from drc.datamodel.models import ObjectInformatieObject
from drc.datamodel.tests.factories import (
    EnkelvoudigInformatieObjectFactory, ObjectInformatieObjectFactory
)

ZAAK = f'http://example.com/zrc/api/v1/zaak/{uuid.uuid4().hex}'


@override_settings(LINK_FETCHER='zds_schema.mocks.link_fetcher_200')
class ObjectInformatieObjectAPITests(APITestCase):

    list_url = reverse_lazy('objectinformatieobject-list', kwargs={'version': '1'})

    def setUp(self):
        patcher = patch('drc.sync.signals.sync_create')
        self.mocked_sync_create = patcher.start()
        self.addCleanup(patcher.stop)

    def test_create(self):
        enkelvoudig_informatie = EnkelvoudigInformatieObjectFactory.create()
        enkelvoudig_informatie_url = reverse('enkelvoudiginformatieobject-detail', kwargs={
            'version': '1',
            'uuid': enkelvoudig_informatie.uuid,
        })

        content = {
            'informatieobject': 'http://testserver' + enkelvoudig_informatie_url,
            'object': ZAAK,
            'objectType': ObjectTypes.zaak,
            'registratiedatum': '2018-09-19T12:25:19+0200',
        }

        # Send to the API
        response = self.client.post(self.list_url, content)

        # Test response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

        # Test database
        self.assertEqual(ObjectInformatieObject.objects.count(), 1)
        stored_object = ObjectInformatieObject.objects.get()
        self.assertEqual(stored_object.object, ZAAK)
        self.assertEqual(stored_object.object_type, ObjectTypes.zaak)

        expected_url = reverse('objectinformatieobject-detail', kwargs={
            'version': '1',
            'uuid': stored_object.uuid,
        })

        expected_response = content.copy()
        expected_response.update({
            'url': f'http://testserver{expected_url}',
            'titel': '',
            'beschrijving': '',
            'registratiedatum': '2018-09-19T10:25:19Z',
        })
        self.assertEqual(response.json(), expected_response)

    @freeze_time('2018-09-19T12:25:19+0200')
    def test_future_registratiedatum(self):
        content = {
            'registratiedatum': '2018-09-19T12:25:20+0200',
        }

        # Send to the API
        response = self.client.post(self.list_url, content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)
        error = get_validation_errors(response, 'registratiedatum')
        self.assertEqual(error['code'], UntilNowValidator.code)

    def test_duplicate_object(self):
        """
        Test the (informatieobject, object) unique together validation.
        """
        oio = ObjectInformatieObjectFactory.create()
        enkelvoudig_informatie_url = reverse('enkelvoudiginformatieobject-detail', kwargs={
            'version': '1',
            'uuid': oio.informatieobject.uuid,
        })

        content = {
            'informatieobject': f'http://testserver{enkelvoudig_informatie_url}',
            'object': oio.object,
            'objectType': ObjectTypes.zaak,
            'registratiedatum': '2018-09-19T12:25:19+0200',
        }

        # Send to the API
        response = self.client.post(self.list_url, content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)
        error = get_validation_errors(response, 'nonFieldErrors')
        self.assertEqual(error['code'], 'unique')

    def test_read(self):
        zio = ObjectInformatieObjectFactory.create(is_besluit=True)
        # Retrieve from the API

        zio_detail_url = reverse('objectinformatieobject-detail', kwargs={
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
            'url': f'http://testserver{zio_detail_url}',
            'informatieobject': f'http://testserver{eo_detail_url}',
            'object': zio.object,
            'objectType': ObjectTypes.besluit,
            'titel': '',
            'beschrijving': '',
            'registratiedatum': zio.registratiedatum.strftime('%Y-%m-%dT%H:%M:%SZ'),
        }

        self.assertEqual(response.json(), expected)
