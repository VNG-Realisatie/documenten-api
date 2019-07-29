import uuid

from base64 import b64encode
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings

from privates.test import temp_private_root
from rest_framework import status
from rest_framework.test import APITestCase
from vng_api_common.constants import VertrouwelijkheidsAanduiding
from vng_api_common.tests import (
    JWTAuthMixin, get_operation_url, get_validation_errors, reverse
)

from drc.api.tests.utils import split_file
from drc.datamodel.models import EnkelvoudigInformatieObject
from drc.datamodel.tests.factories import EnkelvoudigInformatieObjectFactory
from drc.api.scopes import SCOPE_DOCUMENTEN_LOCK, SCOPE_DOCUMENTEN_AANMAKEN, SCOPE_DOCUMENTEN_ALLES_LEZEN, \
    SCOPE_DOCUMENTEN_ALLES_VERWIJDEREN, SCOPE_DOCUMENTEN_BIJWERKEN, SCOPE_DOCUMENTEN_GEFORCEERD_UNLOCK

INFORMATIEOBJECTTYPE = 'https://example.com/ztc/api/v1/catalogus/1/informatieobjecttype/1'


@temp_private_root()
@override_settings(LINK_FETCHER='vng_api_common.mocks.link_fetcher_200')
class SmallFileUpload(JWTAuthMixin, APITestCase):
    heeft_alle_autorisaties = True

    def test_create_eio(self):
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
            'bestandsomvang': 17,
            'link': 'http://een.link',
            'beschrijving': 'test_beschrijving',
            'informatieobjecttype': INFORMATIEOBJECTTYPE,
            'vertrouwelijkheidaanduiding': 'openbaar',
        }
        list_url = reverse(EnkelvoudigInformatieObject)

        response = self.client.post(list_url, content)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

        data = response.json()
        eio = EnkelvoudigInformatieObject.objects.get()
        file_url = get_operation_url('enkelvoudiginformatieobject_download', uuid=eio.uuid)

        self.assertEqual(eio.vertrouwelijkheidaanduiding, VertrouwelijkheidsAanduiding.openbaar)
        self.assertEqual(eio.titel, 'detailed summary')
        self.assertEqual(eio.canonical.bestandsdelen.count(), 0)
        self.assertEqual(eio.inhoud.file.read(), b'some file content')
        self.assertEqual(data['inhoud'], f'http://testserver{file_url}?versie=1')
        self.assertEqual(data['locked'], False)

    def test_create_without_file(self):
        content = {
            'identificatie': uuid.uuid4().hex,
            'bronorganisatie': '159351741',
            'creatiedatum': '2018-06-27',
            'titel': 'detailed summary',
            'auteur': 'test_auteur',
            'formaat': 'txt',
            'taal': 'eng',
            'bestandsnaam': 'dummy.txt',
            'inhoud': None,
            'bestandsomvang': None,
            'link': 'http://een.link',
            'beschrijving': 'test_beschrijving',
            'informatieobjecttype': INFORMATIEOBJECTTYPE,
            'vertrouwelijkheidaanduiding': 'openbaar',
        }
        list_url = reverse(EnkelvoudigInformatieObject)

        response = self.client.post(list_url, content)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.json()
        eio = EnkelvoudigInformatieObject.objects.get()

        self.assertEqual(data['inhoud'], None)
        self.assertEqual(eio.bestandsomvang, None)

    def test_create_empty_file(self):
        content = {
            'identificatie': uuid.uuid4().hex,
            'bronorganisatie': '159351741',
            'creatiedatum': '2018-06-27',
            'titel': 'detailed summary',
            'auteur': 'test_auteur',
            'formaat': 'txt',
            'taal': 'eng',
            'bestandsnaam': 'dummy.txt',
            'inhoud': None,
            'bestandsomvang': 0,
            'link': 'http://een.link',
            'beschrijving': 'test_beschrijving',
            'informatieobjecttype': INFORMATIEOBJECTTYPE,
            'vertrouwelijkheidaanduiding': 'openbaar',
        }
        list_url = reverse(EnkelvoudigInformatieObject)

        response = self.client.post(list_url, content)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.json()
        eio = EnkelvoudigInformatieObject.objects.get()
        file_url = get_operation_url('enkelvoudiginformatieobject_download', uuid=eio.uuid)

        self.assertEqual(eio.bestandsomvang, 0)
        self.assertEqual(data['inhoud'], f'http://testserver{file_url}?versie=1')

        file_response = self.client.get(file_url)

        self.assertEqual(file_response.status_code, status.HTTP_200_OK)
        self.assertEqual(file_response.content, b'')

    def test_update_eio_metadata(self):
        eio = EnkelvoudigInformatieObjectFactory.create(
            informatieobjecttype=INFORMATIEOBJECTTYPE,
        )
        detail_url = reverse(eio)
        lock_url = get_operation_url('enkelvoudiginformatieobject_lock', uuid=eio.uuid)

        # lock
        response_lock = self.client.post(lock_url)
        lock = response_lock.json()['lock']

        # update metadata
        response = self.client.patch(detail_url, {'titel': 'another summary', 'lock': lock})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        eio_new = eio.canonical.latest_version
        file_url = get_operation_url('enkelvoudiginformatieobject_download', uuid=eio_new.uuid)

        self.assertEqual(eio_new.versie, 2)
        self.assertEqual(eio_new.titel, 'another summary')
        self.assertEqual(eio.canonical.bestandsdelen.count(), 0)
        self.assertEqual(data['inhoud'], f'http://testserver{file_url}?versie=2')

    def test_update_eio_file(self):
        eio = EnkelvoudigInformatieObjectFactory.create(
            informatieobjecttype=INFORMATIEOBJECTTYPE,
        )
        detail_url = reverse(eio)
        lock_url = get_operation_url('enkelvoudiginformatieobject_lock', uuid=eio.uuid)

        # lock
        response_lock = self.client.post(lock_url)
        lock = response_lock.json()['lock']

        # update metadata
        response = self.client.patch(
            detail_url,
            {
                'inhoud': b64encode(b'some other file content').decode('utf-8'),
                'bestandsomvang': 23,
                'lock': lock
            }
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        eio_new = eio.canonical.latest_version
        file_url = get_operation_url('enkelvoudiginformatieobject_download', uuid=eio_new.uuid)

        self.assertEqual(eio.canonical.bestandsdelen.count(), 0)
        self.assertEqual(data['inhoud'], f'http://testserver{file_url}?versie=2')
        self.assertEqual(eio_new.inhoud.file.read(), b'some other file content')

    def test_update_eio_file_set_empty(self):
        eio = EnkelvoudigInformatieObjectFactory.create(
            informatieobjecttype=INFORMATIEOBJECTTYPE,
        )
        detail_url = reverse(eio)
        lock_url = get_operation_url('enkelvoudiginformatieobject_lock', uuid=eio.uuid)

        # lock
        response_lock = self.client.post(lock_url)
        lock = response_lock.json()['lock']

        # update metadata
        response = self.client.patch(
            detail_url,
            {
                'inhoud': None,
                'bestandsomvang': None,
                'lock': lock
            }
        )


        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        eio_new = eio.canonical.latest_version

        self.assertEqual(eio.canonical.bestandsdelen.count(), 0)
        self.assertEqual(data['inhoud'], None)
        self.assertEqual(eio_new.bestandsomvang, None)

    def test_update_eio_only_size(self):
        eio = EnkelvoudigInformatieObjectFactory.create(
            informatieobjecttype=INFORMATIEOBJECTTYPE,
        )
        detail_url = reverse(eio)
        lock_url = get_operation_url('enkelvoudiginformatieobject_lock', uuid=eio.uuid)

        # lock
        response_lock = self.client.post(lock_url)
        lock = response_lock.json()['lock']

        # update metadata
        response = self.client.patch(detail_url, {'bestandsomvang': 20, 'lock': lock})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)

        error = get_validation_errors(response, 'nonFieldErrors')
        self.assertEqual(error['code'], 'file-size')


@temp_private_root()
@override_settings(LINK_FETCHER='vng_api_common.mocks.link_fetcher_200',
                   CHUNK_SIZE=10)
class LargeFileAPITests(JWTAuthMixin, APITestCase):

    informatieobjecttype = INFORMATIEOBJECTTYPE
    scopes = [
        SCOPE_DOCUMENTEN_LOCK, SCOPE_DOCUMENTEN_AANMAKEN, SCOPE_DOCUMENTEN_ALLES_LEZEN,
        SCOPE_DOCUMENTEN_ALLES_VERWIJDEREN, SCOPE_DOCUMENTEN_BIJWERKEN
    ]

    def _create_metadata(self):
        self.file_content = SimpleUploadedFile("file.txt", b"filecontentstring")
        content = {

            'identificatie': uuid.uuid4().hex,
            'bronorganisatie': '159351741',
            'creatiedatum': '2018-06-27',
            'titel': 'detailed summary',
            'auteur': 'test_auteur',
            'formaat': 'txt',
            'taal': 'eng',
            'bestandsnaam': 'dummy.txt',
            'bestandsomvang': self.file_content.size,
            'link': 'http://een.link',
            'beschrijving': 'test_beschrijving',
            'informatieobjecttype': INFORMATIEOBJECTTYPE,
            'vertrouwelijkheidaanduiding': VertrouwelijkheidsAanduiding.openbaar,
        }
        list_url = reverse(EnkelvoudigInformatieObject)

        response = self.client.post(list_url, content)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

        self.eio = EnkelvoudigInformatieObject.objects.get()
        self.canonical = self.eio.canonical
        data = response.json()

        self.assertEqual(self.eio.vertrouwelijkheidaanduiding, VertrouwelijkheidsAanduiding.openbaar)
        self.assertEqual(self.eio.titel, 'detailed summary')
        self.assertEqual(self.eio.inhoud, '')
        self.assertEqual(self.canonical.bestandsdelen.count(), 2)
        self.assertEqual(data['locked'], True)
        self.assertEqual(data['lock'], self.canonical.lock)

        self.bestandsdelen = self.canonical.bestandsdelen.order_by('index').all()

        for part in self.bestandsdelen:
            self.assertEqual(part.voltooid, False)
            self.assertEqual(part.inhoud, '')
        self.assertEqual(self.bestandsdelen[0].grootte, settings.CHUNK_SIZE)
        self.assertEqual(self.bestandsdelen[1].grootte, self.file_content.size - settings.CHUNK_SIZE)

    def _upload_part_files(self):
        part_files = split_file(self.file_content, settings.CHUNK_SIZE)
        for part in self.bestandsdelen:
            part_url = get_operation_url('bestandsdeel_update', uuid=part.uuid)

            response = self.client.put(
                part_url,
                {'inhoud': part_files.pop(0),
                 'lock': self.canonical.lock},
                format='multipart'
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

            part.refresh_from_db()

            self.assertNotEqual(part.inhoud, '')
            self.assertEqual(part.voltooid, True)

    def _unlock(self):
        unlock_url = get_operation_url('enkelvoudiginformatieobject_unlock', uuid=self.eio.uuid)

        response = self.client.post(unlock_url, {'lock': self.canonical.lock})

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, response.data)

        self.canonical.refresh_from_db()
        self.eio.refresh_from_db()

        self.assertEqual(self.canonical.bestandsdelen.count(), 0)
        self.assertNotEqual(self.eio.inhoud.path, '')
        self.assertEqual(self.eio.inhoud.size, self.file_content.size)

    def _download_file(self):
        file_url = get_operation_url('enkelvoudiginformatieobject_download', uuid=self.eio.uuid)

        response = self.client.get(file_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content, b'filecontentstring')

    def test_create_eio_full_process(self):
        self._create_metadata()
        self._upload_part_files()
        self._unlock()
        self._download_file()

    def test_upload_part_wrong_size(self):
        self._create_metadata()

        # change file size for part file
        part = self.bestandsdelen[0]
        part.grootte = part.grootte + 1
        part.save()

        # upload part file
        part_url = get_operation_url('bestandsdeel_update', uuid=part.uuid)
        part_file = split_file(self.file_content, settings.CHUNK_SIZE)[0]

        response = self.client.put(
            part_url,
            {'inhoud': part_file,
             'lock': self.canonical.lock},
            format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error = get_validation_errors(response, 'nonFieldErrors')
        self.assertEqual(error['code'], 'file-size')

    def test_upload_part_twice_correct(self):
        self._create_metadata()
        self._upload_part_files()

        # upload one of parts again
        self.file_content.seek(0)
        part_files = split_file(self.file_content, settings.CHUNK_SIZE)
        part = self.bestandsdelen[0]
        part_url = get_operation_url('bestandsdeel_update', uuid=part.uuid)

        response = self.client.put(
            part_url,
            {'inhoud': part_files[0], 'lock': self.canonical.lock},
            format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        part.refresh_from_db()

        self.assertNotEqual(part.inhoud, '')
        self.assertEqual(part.voltooid, True)

    def test_unlock_without_uploading(self):
        self._create_metadata()

        # unlock
        unlock_url = get_operation_url('enkelvoudiginformatieobject_unlock', uuid=self.eio.uuid)

        response = self.client.post(unlock_url, {'lock': self.canonical.lock})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error = get_validation_errors(response, 'nonFieldErrors')
        self.assertEqual(error['code'], 'file-size')

    def test_unlock_not_finish_upload(self):
        self._create_metadata()

        # unload 1 part of file
        part_file = split_file(self.file_content, settings.CHUNK_SIZE)[0]
        part = self.bestandsdelen[0]
        part_url = get_operation_url('bestandsdeel_update', uuid=part.uuid)

        response = self.client.put(
            part_url,
            {'inhoud': part_file, 'lock': self.canonical.lock},
            format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        # unlock
        unlock_url = get_operation_url('enkelvoudiginformatieobject_unlock', uuid=self.eio.uuid)

        response = self.client.post(unlock_url, {'lock': self.canonical.lock})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)

        error = get_validation_errors(response, 'nonFieldErrors')
        self.assertEqual(error['code'], 'incomplete-upload')

    def test_unlock_not_finish_upload_force(self):
        self.autorisatie.scopes = self.autorisatie.scopes + [SCOPE_DOCUMENTEN_GEFORCEERD_UNLOCK]
        self.autorisatie.save()
        self._create_metadata()

        # unload 1 part of file
        part_file = split_file(self.file_content, settings.CHUNK_SIZE)[0]
        part = self.bestandsdelen[0]
        part_url = get_operation_url('bestandsdeel_update', uuid=part.uuid)

        response = self.client.put(
            part_url,
            {'inhoud': part_file, 'lock': self.canonical.lock},
            format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        # force unlock
        unlock_url = get_operation_url('enkelvoudiginformatieobject_unlock', uuid=self.eio.uuid)

        response = self.client.post(unlock_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.eio.refresh_from_db()
        self.canonical.refresh_from_db()

        self.assertEqual(self.eio.bestandsomvang, None)
        self.assertEqual(self.canonical.bestandsdelen.count(), 0)

    def test_update_metadata_without_upload(self):
        self._create_metadata()

        # update file metadata
        eio_url = get_operation_url('enkelvoudiginformatieobject_read', uuid=self.eio.uuid)

        response = self.client.patch(eio_url, {
            'beschrijving': 'beschrijving2',
            'lock': self.canonical.lock
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        data = response.json()
        self.eio.refresh_from_db()

        self.assertIsNone(data['inhoud'])  # the link to download is None
        self.assertEqual(len(data['bestandsdelen']), 2)
        self.assertEqual(self.eio.beschrijving, 'beschrijving2')

    def test_update_metadata_after_unfinished_upload(self):
        self._create_metadata()

        # unload 1 part of file
        part_file = split_file(self.file_content, settings.CHUNK_SIZE)[0]
        part = self.bestandsdelen[0]
        part_url = get_operation_url('bestandsdeel_update', uuid=part.uuid)

        response = self.client.put(
            part_url,
            {'inhoud': part_file, 'lock': self.canonical.lock},
            format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        part.refresh_from_db()
        self.assertEqual(part.voltooid, True)

        # update metedata
        eio_url = get_operation_url('enkelvoudiginformatieobject_read', uuid=self.eio.uuid)

        response = self.client.patch(eio_url, {
            'beschrijving': 'beschrijving2',
            'lock': self.canonical.lock
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.canonical.refresh_from_db()
        part_new = self.canonical.bestandsdelen.order_by('index').first()

        self.assertEqual(self.canonical.bestandsdelen.count(), 2)
        self.assertEqual(self.canonical.empty_bestandsdelen, True)
        self.assertEqual(part_new.voltooid, False)

    def test_update_metadata_set_size(self):
        self._create_metadata()

        # update file metadata
        eio_url = get_operation_url('enkelvoudiginformatieobject_read', uuid=self.eio.uuid)

        response = self.client.patch(eio_url, {
            'bestandsomvang': 45,
            'lock': self.canonical.lock
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        data = response.json()
        self.canonical.refresh_from_db()
        self.eio.refresh_from_db()

        self.assertEqual(self.eio.bestandsomvang, 45)
        self.assertEqual(self.canonical.bestandsdelen.count(), 5)
        self.assertEqual(data['inhoud'], None)

    def test_update_metadata_set_size_zero(self):
        self._create_metadata()

        # update file metadata
        eio_url = get_operation_url('enkelvoudiginformatieobject_read', uuid=self.eio.uuid)

        response = self.client.patch(eio_url, {
            'bestandsomvang': 0,
            'lock': self.canonical.lock
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        data = response.json()
        self.canonical.refresh_from_db()
        self.eio.refresh_from_db()
        file_url = get_operation_url('enkelvoudiginformatieobject_download', uuid=self.eio.uuid)

        self.assertEqual(self.eio.bestandsomvang, 0)
        self.assertEqual(self.canonical.bestandsdelen.count(), 0)
        self.assertEqual(data['inhoud'], f'http://testserver{file_url}?versie=1')

    def test_update_metadata_set_size_null(self):
        self._create_metadata()

        # update file metadata
        eio_url = get_operation_url('enkelvoudiginformatieobject_read', uuid=self.eio.uuid)

        response = self.client.patch(eio_url, {
            'bestandsomvang': None,
            'lock': self.canonical.lock
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        data = response.json()
        self.canonical.refresh_from_db()
        self.eio.refresh_from_db()

        self.assertEqual(self.eio.bestandsomvang, None)
        self.assertEqual(self.canonical.bestandsdelen.count(), 0)
        self.assertEqual(data['inhoud'], None)
