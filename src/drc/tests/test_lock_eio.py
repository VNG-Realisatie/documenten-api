import tempfile
import uuid

from django.test import override_settings

from freezegun import freeze_time
from rest_framework import status
from rest_framework.test import APITestCase
from vng_api_common.tests import (
    JWTAuthMixin, get_operation_url, get_validation_errors
)

from drc.datamodel.tests.factories import EnkelvoudigInformatieObjectFactory


@freeze_time('2018-06-27')
@override_settings(MEDIA_ROOT=tempfile.mkdtemp(),
                   LINK_FETCHER='vng_api_common.mocks.link_fetcher_200')
class EnkelvoudigInformatieObjectAPITests(JWTAuthMixin, APITestCase):

    heeft_alle_autorisaties = True

    def test_lock_sucess(self):
        eio = EnkelvoudigInformatieObjectFactory.create()
        assert eio.lock == ''
        url = get_operation_url('enkelvoudiginformatieobject_lock', uuid=eio.uuid)

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        data = response.json()
        eio.refresh_from_db()

        self.assertEqual(data['lock'], eio.lock)
        self.assertNotEqual(data['lock'], '')

    def test_lock_fail_locked_doc(self):
        eio = EnkelvoudigInformatieObjectFactory.create(lock=uuid.uuid4().hex)
        url = get_operation_url('enkelvoudiginformatieobject_lock', uuid=eio.uuid)

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)

        error = get_validation_errors(response, 'nonFieldErrors')
        self.assertEqual(error['code'], 'existing-lock')

    def test_unnlock_sucess(self):
        lock = uuid.uuid4().hex
        eio = EnkelvoudigInformatieObjectFactory.create(lock=lock)
        url = get_operation_url('enkelvoudiginformatieobject_unlock', uuid=eio.uuid)

        response = self.client.post(url, {'lock': lock})

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        eio.refresh_from_db()

        self.assertEqual(eio.lock, '')

    def test_unlock_fail_incorrect_id(self):
        eio = EnkelvoudigInformatieObjectFactory.create(lock=uuid.uuid4().hex)
        url = get_operation_url('enkelvoudiginformatieobject_unlock', uuid=eio.uuid)

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)

        error = get_validation_errors(response, 'nonFieldErrors')
        self.assertEqual(error['code'], 'incorrect-lock-id')

    def test_update_sucess(self):
        lock = uuid.uuid4().hex
        eio = EnkelvoudigInformatieObjectFactory.create(lock=lock)
        url = get_operation_url('enkelvoudiginformatieobject_update', uuid=eio.uuid)

        response = self.client.patch(
            url,
            {'titel': 'changed',
             'lock': lock}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        eio.refresh_from_db()

        self.assertEqual(eio.titel, 'changed')

    def test_update_fail_unlocked_doc(self):
        eio = EnkelvoudigInformatieObjectFactory.create()
        assert eio.lock == ''

        url = get_operation_url('enkelvoudiginformatieobject_update', uuid=eio.uuid)

        response = self.client.patch(url, {'titel': 'changed'})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)

        error = get_validation_errors(response, 'nonFieldErrors')
        self.assertEqual(error['code'], 'unlocked')

    def test_update_fail_wrong_id(self):
        eio = EnkelvoudigInformatieObjectFactory.create(lock=uuid.uuid4().hex)

        url = get_operation_url('enkelvoudiginformatieobject_update', uuid=eio.uuid)

        response = self.client.patch(
            url,
            {'titel': 'changed',
             'lock': 12345}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)

        error = get_validation_errors(response, 'nonFieldErrors')
        self.assertEqual(error['code'], 'incorrect-lock-id')
