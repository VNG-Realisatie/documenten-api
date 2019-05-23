import uuid
from datetime import datetime

from django.test import override_settings
from django.urls import reverse, reverse_lazy
from django.utils import timezone

from freezegun import freeze_time
from rest_framework import status
from rest_framework.test import APITestCase
from vng_api_common.constants import ObjectTypes
from vng_api_common.tests import JWTAuthMixin, get_validation_errors
from vng_api_common.validators import IsImmutableValidator

from drc.datamodel.constants import RelatieAarden
from drc.datamodel.models import (
    EnkelvoudigInformatieObject, ObjectInformatieObject
)
from drc.datamodel.tests.factories import (
    EnkelvoudigInformatieObjectFactory, ObjectInformatieObjectFactory
)
from drc.sync.signals import SyncError

from .mixins import ObjectInformatieObjectSyncMixin

ZAAK = f'http://example.com/zrc/api/v1/zaak/{uuid.uuid4().hex}'
BESLUIT = f'http://example.com/brc/api/v1/besluit/{uuid.uuid4().hex}'
INFORMATIEOBJECTTYPE = 'https://example.com/informatieobjecttype/foo'


def dt_to_api(dt: datetime):
    formatted = dt.isoformat()
    if formatted.endswith('+00:00'):
        return formatted[:-6] + 'Z'
    return formatted


@override_settings(LINK_FETCHER='vng_api_common.mocks.link_fetcher_200')
class ObjectInformatieObjectAPITests(ObjectInformatieObjectSyncMixin, JWTAuthMixin, APITestCase):

    list_url = reverse_lazy('objectinformatieobject-list', kwargs={'version': '1'})

    heeft_alle_autorisaties = True

    @freeze_time('2018-09-19T12:25:19+0200')
    def test_create(self):
        enkelvoudig_informatie = EnkelvoudigInformatieObjectFactory.create(
            informatieobjecttype=INFORMATIEOBJECTTYPE,
        )
        enkelvoudig_informatie_url = reverse('enkelvoudiginformatieobject-detail', kwargs={
            'version': '1',
            'uuid': enkelvoudig_informatie.uuid,
        })

        content = {
            'informatieobject': 'http://testserver' + enkelvoudig_informatie_url,
            'object': ZAAK,
            'objectType': ObjectTypes.zaak,
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
        self.assertEqual(stored_object.aard_relatie, RelatieAarden.hoort_bij)

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
            'aardRelatieWeergave': RelatieAarden.labels[RelatieAarden.hoort_bij],
        })
        self.assertEqual(response.json(), expected_response)

    def test_create_besluitinformatieobject(self):
        enkelvoudig_informatie = EnkelvoudigInformatieObjectFactory.create(
            informatieobjecttype=INFORMATIEOBJECTTYPE,
        )
        enkelvoudig_informatie_url = reverse('enkelvoudiginformatieobject-detail', kwargs={
            'version': '1',
            'uuid': enkelvoudig_informatie.uuid,
        })

        content = {
            'informatieobject': 'http://testserver' + enkelvoudig_informatie_url,
            'object': BESLUIT,
            'objectType': ObjectTypes.besluit,
        }

        # Send to the API
        response = self.client.post(self.list_url, content)

        # Test response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

        # Test database
        self.assertEqual(ObjectInformatieObject.objects.count(), 1)
        stored_object = ObjectInformatieObject.objects.get()
        self.assertEqual(stored_object.object, BESLUIT)
        self.assertEqual(stored_object.object_type, ObjectTypes.besluit)
        self.assertEqual(stored_object.aard_relatie, RelatieAarden.legt_vast)

        expected_url = reverse('objectinformatieobject-detail', kwargs={
            'version': '1',
            'uuid': stored_object.uuid,
        })

        expected_response = content.copy()
        expected_response.update({
            'url': f'http://testserver{expected_url}',
            'aardRelatieWeergave': RelatieAarden.labels[RelatieAarden.legt_vast],
        })
        self.assertEqual(response.json(), expected_response)

    @freeze_time('2018-09-20 12:00:00')
    def test_registratiedatum_ignored(self):
        enkelvoudig_informatie = EnkelvoudigInformatieObjectFactory.create(
            informatieobjecttype=INFORMATIEOBJECTTYPE,
        )
        enkelvoudig_informatie_url = reverse('enkelvoudiginformatieobject-detail', kwargs={
            'version': '1',
            'uuid': enkelvoudig_informatie.uuid,
        })

        content = {
            'informatieobject': 'http://testserver' + enkelvoudig_informatie_url,
            'object': ZAAK,
            'objectType': ObjectTypes.zaak,
            'registratiedatum': '2018-09-19T12:25:20+0200',
        }

        # Send to the API
        self.client.post(self.list_url, content)

        oio = ObjectInformatieObject.objects.get()

        self.assertEqual(
            oio.registratiedatum,
            datetime(2018, 9, 20, 12, 0, 0).replace(tzinfo=timezone.utc)
        )

    def test_duplicate_object(self):
        """
        Test the (informatieobject, object) unique together validation.
        """
        oio = ObjectInformatieObjectFactory.create(
            is_zaak=True,
            informatieobject__informatieobjecttype=INFORMATIEOBJECTTYPE
        )
        enkelvoudig_informatie_url = reverse('enkelvoudiginformatieobject-detail', kwargs={
            'version': '1',
            'uuid': oio.informatieobject.uuid,
        })

        content = {
            'informatieobject': f'http://testserver{enkelvoudig_informatie_url}',
            'object': oio.object,
            'objectType': ObjectTypes.zaak,
            'informatieobjecttype': INFORMATIEOBJECTTYPE,
        }

        # Send to the API
        response = self.client.post(self.list_url, content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)
        error = get_validation_errors(response, 'nonFieldErrors')
        self.assertEqual(error['code'], 'unique')

    def test_read_besluit(self):
        zio = ObjectInformatieObjectFactory.create(
            is_besluit=True,
            informatieobject__informatieobjecttype=INFORMATIEOBJECTTYPE
        )
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
            'aardRelatieWeergave': RelatieAarden.labels[RelatieAarden.legt_vast],
            'titel': '',
            'beschrijving': '',
            'registratiedatum': dt_to_api(zio.registratiedatum),
        }

        self.assertEqual(response.json(), expected)

    def test_update_besluit(self):
        eo = EnkelvoudigInformatieObjectFactory.create(
            informatieobjecttype=INFORMATIEOBJECTTYPE,
        )
        zio = ObjectInformatieObjectFactory.create(
            is_besluit=True,
            informatieobject__informatieobjecttype=INFORMATIEOBJECTTYPE
        )

        eo_detail_url = reverse('enkelvoudiginformatieobject-detail', kwargs={
            'version': '1',
            'uuid': eo.uuid,
        })
        zio_detail_url = reverse('objectinformatieobject-detail', kwargs={
            'version': '1',
            'uuid': zio.uuid,
        })

        response = self.client.patch(zio_detail_url, {
            'object': 'https://something.different',
            'informatieobject': eo_detail_url,
            'objectType': ObjectTypes.zaak,
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)

        for field in ['object', 'informatieobject', 'objectType']:
            with self.subTest(field=field):
                error = get_validation_errors(response, field)
                self.assertEqual(error['code'], IsImmutableValidator.code)

    def test_read_zaak(self):
        zio = ObjectInformatieObjectFactory.create(
            is_zaak=True,
            informatieobject__informatieobjecttype=INFORMATIEOBJECTTYPE
        )
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
            'objectType': ObjectTypes.zaak,
            'aardRelatieWeergave': RelatieAarden.labels[RelatieAarden.hoort_bij],
            'titel': '',
            'beschrijving': '',
            'registratiedatum': dt_to_api(zio.registratiedatum),
        }

        self.assertEqual(response.json(), expected)

    def test_filter(self):
        zio = ObjectInformatieObjectFactory.create(
            is_zaak=True,
            informatieobject__informatieobjecttype=INFORMATIEOBJECTTYPE
        )
        eo_detail_url = reverse('enkelvoudiginformatieobject-detail', kwargs={
            'version': '1',
            'uuid': zio.informatieobject.uuid,
        })
        zio_list_url = reverse('objectinformatieobject-list', kwargs={'version': '1'})

        response = self.client.get(zio_list_url, {
            'informatieobject': f'http://testserver{eo_detail_url}',
        })

        self.assertEqual(response.status_code, 200)

    def test_update_zaak(self):
        eo = EnkelvoudigInformatieObjectFactory.create(
            informatieobjecttype=INFORMATIEOBJECTTYPE
        )
        zio = ObjectInformatieObjectFactory.create(
            is_zaak=True,
            informatieobject__informatieobjecttype=INFORMATIEOBJECTTYPE
        )

        eo_detail_url = reverse('enkelvoudiginformatieobject-detail', kwargs={
            'version': '1',
            'uuid': eo.uuid,
        })
        zio_detail_url = reverse('objectinformatieobject-detail', kwargs={
            'version': '1',
            'uuid': zio.uuid,
        })

        response = self.client.patch(zio_detail_url, {
            'object': 'https://something.different',
            'informatieobject': eo_detail_url,
            'objectType': ObjectTypes.besluit,
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)

        for field in ['object', 'informatieobject', 'objectType']:
            with self.subTest(field=field):
                error = get_validation_errors(response, field)
                self.assertEqual(error['code'], IsImmutableValidator.code)

    def test_sync_create_fails(self):
        self.mocked_sync_create.side_effect = SyncError("Sync failed")

        enkelvoudig_informatie = EnkelvoudigInformatieObjectFactory.create(
            informatieobjecttype=INFORMATIEOBJECTTYPE
        )
        enkelvoudig_informatie_url = reverse('enkelvoudiginformatieobject-detail', kwargs={
            'version': '1',
            'uuid': enkelvoudig_informatie.uuid,
        })

        content = {
            'informatieobject': 'http://testserver' + enkelvoudig_informatie_url,
            'object': BESLUIT,
            'objectType': ObjectTypes.besluit,
        }

        # Send to the API
        response = self.client.post(self.list_url, content)

        # Test response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)

        # transaction must be rolled back
        self.assertFalse(ObjectInformatieObject.objects.exists())

    @freeze_time('2018-09-19T12:25:19+0200')
    def test_delete(self):
        document = EnkelvoudigInformatieObjectFactory.create(
            informatieobjecttype=INFORMATIEOBJECTTYPE
        )
        oio = ObjectInformatieObjectFactory.create(
            informatieobject=document,
            object=ZAAK,
            object_type=ObjectTypes.zaak,
            aard_relatie=RelatieAarden.hoort_bij
        )
        oio_url = reverse('objectinformatieobject-detail', kwargs={
            'version': '1',
            'uuid': oio.uuid,
        })

        self.assertEqual(self.mocked_sync_delete.call_count, 0)

        response = self.client.delete(oio_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, response.data)

        self.assertEqual(self.mocked_sync_delete.call_count, 1)

        # Relation is gone, document still exists.
        self.assertFalse(ObjectInformatieObject.objects.exists())
        self.assertTrue(EnkelvoudigInformatieObject.objects.exists())

    def test_besluitinformatieobject_partial_update_irrelevant_fields_validation(self):
        eo = EnkelvoudigInformatieObjectFactory.create(
            informatieobjecttype=INFORMATIEOBJECTTYPE,
        )
        bio = ObjectInformatieObjectFactory.create(
            is_besluit=True,
            informatieobject__informatieobjecttype=INFORMATIEOBJECTTYPE
        )

        eo_detail_url = reverse('enkelvoudiginformatieobject-detail', kwargs={
            'version': '1',
            'uuid': eo.uuid,
        })
        bio_detail_url = reverse('objectinformatieobject-detail', kwargs={
            'version': '1',
            'uuid': bio.uuid,
        })

        # Attempt to do a partial update with fields that should be ignored for
        # `ObjectInformatieObjecten` with object_type `besluit`
        response = self.client.patch(bio_detail_url, {
            'titel': 'some title',
            'beschrijving': 'some description'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify that the fields are indeed ignored and do not appear
        # in the response
        self.assertNotIn('titel', response.data)
        self.assertNotIn('beschrijving', response.data)
        self.assertNotIn('registratiedatum', response.data)
