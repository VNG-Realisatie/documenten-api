import uuid

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

INFORMATIEOBJECTTYPE = 'https://example.com/ztc/api/v1/catalogus/1/informatieobjecttype/1'


@temp_private_root()
@override_settings(LINK_FETCHER='vng_api_common.mocks.link_fetcher_200',
                   CHUNK_SIZE=10)
class FileUploadAPITests(JWTAuthMixin, APITestCase):

    heeft_alle_autorisaties = True

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

        self.assertEqual(self.eio.vertrouwelijkheidaanduiding, VertrouwelijkheidsAanduiding.openbaar)
        self.assertEqual(self.eio.titel, 'detailed summary')
        self.assertEqual(self.eio.inhoud, '')
        self.assertEqual(self.canonical.parts.count(), 2)

        self.parts = self.canonical.parts.order_by('part_number').all()

        for part in self.parts:
            self.assertEqual(part.complete, False)
            self.assertEqual(part.inhoud, '')
        self.assertEqual(self.parts[0].chunk_size, settings.CHUNK_SIZE)
        self.assertEqual(self.parts[1].chunk_size, self.file_content.size - settings.CHUNK_SIZE)

    def _lock_document(self):
        lock_url = get_operation_url('enkelvoudiginformatieobject_lock', uuid=self.eio.uuid)

        response = self.client.post(lock_url)
        self.canonical.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertNotEqual(self.canonical.lock, '')

    def _upload_part_files(self):
        part_files = split_file(self.file_content, settings.CHUNK_SIZE)
        for part in self.parts:
            part_url = get_operation_url('partupload_update', uuid=part.uuid)

            response = self.client.put(
                part_url,
                {'inhoud': part_files.pop(0)},
                format='multipart'
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

            part.refresh_from_db()

            self.assertNotEqual(part.inhoud, '')
            self.assertEqual(part.complete, True)

    def _mark_complete(self):
        complete_url = get_operation_url('enkelvoudiginformatieobject_complete', uuid=self.eio.uuid)

        response = self.client.put(complete_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        data = response.json()
        self.canonical.refresh_from_db()
        self.eio.refresh_from_db()
        file_url = get_operation_url('enkelvoudiginformatieobject_download', uuid=self.eio.uuid)

        self.assertEqual(self.canonical.parts.count(), 0)
        self.assertNotEqual(self.eio.inhoud.path, '')
        self.assertEqual(self.eio.inhoud.size, self.file_content.size)
        self.assertEqual(data['inhoud'], f'http://testserver{file_url}')

    def _download_file(self):
        file_url = get_operation_url('enkelvoudiginformatieobject_download', uuid=self.eio.uuid)

        response = self.client.get(file_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content, b'filecontentstring')

    def test_upload_file_full_process(self):
        self._create_metadata()
        self._lock_document()
        self._upload_part_files()
        self._mark_complete()
        self._download_file()

    def test_upload_file_wrong_size(self):
        self._create_metadata()
        self._lock_document()

        # change file size for part file
        part = self.parts[0]
        part.chunk_size = part.chunk_size + 1
        part.save()

        # upload part file
        part_url = get_operation_url('partupload_update', uuid=part.uuid)
        part_file = split_file(self.file_content, settings.CHUNK_SIZE)[0]

        response = self.client.put(
            part_url,
            {'inhoud': part_file},
            format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error = get_validation_errors(response, 'nonFieldErrors')
        self.assertEqual(error['code'], 'file-size')

    def test_upload_not_locked(self):
        self._create_metadata()
        self._upload_part_files()

        # mark as complete
        complete_url = get_operation_url('enkelvoudiginformatieobject_complete', uuid=self.eio.uuid)

        response = self.client.put(complete_url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error = get_validation_errors(response, 'nonFieldErrors')
        self.assertEqual(error['code'], 'unlocked')

    def test_upload_part_twice_correct(self):
        self._create_metadata()
        self._lock_document()
        self._upload_part_files()

        # upload one of parts again
        self.file_content.seek(0)
        part_files = split_file(self.file_content, settings.CHUNK_SIZE)
        part = self.parts[0]
        part_url = get_operation_url('partupload_update', uuid=part.uuid)

        response = self.client.put(
            part_url,
            {'inhoud': part_files[0]},
            format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        part.refresh_from_db()

        self.assertNotEqual(part.inhoud, '')
        self.assertEqual(part.complete, True)

    def test_upload_part_twice_incorrect_size(self):
        self._create_metadata()
        self._lock_document()
        self._upload_part_files()

        # upload one of parts again with incorrect size
        part_file = SimpleUploadedFile("file.txt", b"file")
        part = self.parts[0]
        part_url = get_operation_url('partupload_update', uuid=part.uuid)

        response = self.client.put(
            part_url,
            {'inhoud': part_file},
            format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error = get_validation_errors(response, 'nonFieldErrors')
        self.assertEqual(error['code'], 'file-size')

    def test_mark_complete_not_uploaded(self):
        self._create_metadata()
        self._lock_document()

        # mark complete without uploading part files
        complete_url = get_operation_url('enkelvoudiginformatieobject_complete', uuid=self.eio.uuid)

        response = self.client.put(complete_url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error = get_validation_errors(response, 'nonFieldErrors')
        self.assertEqual(error['code'], 'incomplete-upload')

    def test_update_metadata_without_upload(self):
        self._create_metadata()
        self._lock_document()

        # update file metadata
        eio_url = get_operation_url('enkelvoudiginformatieobject_read', uuid=self.eio.uuid)

        response = self.client.patch(eio_url, {
            'beschrijving': 'beschrijving2',
            'lock': self.canonical.lock
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        data = response.json()

        self.assertEqual(self.canonical.enkelvoudiginformatieobject_set.count(), 2)
        self.assertEqual(data['versie'], 2)
        self.assertIsNone(data['inhoud'])  # the link to download is None
        self.assertEqual(len(data['parts']), 2)  # all the parts are remained

    def test_update_metadata_after_upload(self):
        self._create_metadata()
        self._lock_document()
        self._upload_part_files()
        self._mark_complete()

        # update file metadata
        eio_url = get_operation_url('enkelvoudiginformatieobject_read', uuid=self.eio.uuid)

        response = self.client.patch(eio_url, {
            'beschrijving': 'beschrijving2',
            'lock': self.canonical.lock
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        data = response.json()
        new_eio = self.canonical.enkelvoudiginformatieobject_set.order_by('-versie').first()
        old_file_url = get_operation_url('enkelvoudiginformatieobject_download', uuid=self.eio.uuid)
        new_file_url = get_operation_url('enkelvoudiginformatieobject_download', uuid=new_eio.uuid)

        self.assertEqual(self.canonical.enkelvoudiginformatieobject_set.count(), 2)
        self.assertEqual(data['versie'], 2)
        # link is the same as it was
        self.assertEqual(data['inhoud'], f'http://testserver{old_file_url}')
        self.assertEqual(data['inhoud'], f'http://testserver{new_file_url}')

        # download
        self._download_file()
