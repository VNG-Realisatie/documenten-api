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
from drc.api.scopes import SCOPE_DOCUMENTEN_LOCK, SCOPE_DOCUMENTEN_AANMAKEN, SCOPE_DOCUMENTEN_ALLES_LEZEN, \
    SCOPE_DOCUMENTEN_ALLES_VERWIJDEREN, SCOPE_DOCUMENTEN_BIJWERKEN

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


@temp_private_root()
@override_settings(LINK_FETCHER='vng_api_common.mocks.link_fetcher_200',
                   CHUNK_SIZE=10)
class LargeFileCreateAPITests(JWTAuthMixin, APITestCase):

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

    def test_upload_file_full_process(self):
        self._create_metadata()
        self._upload_part_files()
        self._unlock()
        self._download_file()

    def test_upload_file_wrong_size(self):
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

    def test_upload_part_twice_incorrect_size(self):
        self._create_metadata()
        self._upload_part_files()

        # upload one of parts again with incorrect size
        part_file = SimpleUploadedFile("file.txt", b"file")
        part = self.bestandsdelen[0]
        part_url = get_operation_url('bestandsdeel_update', uuid=part.uuid)

        response = self.client.put(
            part_url,
            {'inhoud': part_file, 'lock': self.canonical.lock},
            format='multipart'
        )

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

    # def test_update_metadata_without_upload(self):
    #     self._create_metadata()
    #     self._lock_document()
    #
    #     # update file metadata
    #     eio_url = get_operation_url('enkelvoudiginformatieobject_read', uuid=self.eio.uuid)
    #
    #     response = self.client.patch(eio_url, {
    #         'beschrijving': 'beschrijving2',
    #         'lock': self.canonical.lock
    #     })
    #
    #     self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
    #
    #     data = response.json()
    #
    #     self.assertEqual(self.canonical.enkelvoudiginformatieobject_set.count(), 2)
    #     self.assertEqual(data['versie'], 2)
    #     self.assertIsNone(data['inhoud'])  # the link to download is None
    #     self.assertEqual(len(data['bestandsdelen']), 2)  # all the parts are remained
    #
    # def test_update_metadata_after_upload(self):
    #     self._create_metadata()
    #     self._lock_document()
    #     self._upload_part_files()
    #     self._mark_complete()
    #
    #     # update file metadata
    #     eio_url = get_operation_url('enkelvoudiginformatieobject_read', uuid=self.eio.uuid)
    #
    #     response = self.client.patch(eio_url, {
    #         'beschrijving': 'beschrijving2',
    #         'lock': self.canonical.lock
    #     })
    #
    #     self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
    #
    #     data = response.json()
    #     new_eio = self.canonical.enkelvoudiginformatieobject_set.order_by('-versie').first()
    #     old_file_url = get_operation_url('enkelvoudiginformatieobject_download', uuid=self.eio.uuid)
    #     new_file_url = get_operation_url('enkelvoudiginformatieobject_download', uuid=new_eio.uuid)
    #
    #     self.assertEqual(self.canonical.enkelvoudiginformatieobject_set.count(), 2)
    #     self.assertEqual(data['versie'], 2)
    #     # link is the same as it was
    #     self.assertEqual(data['inhoud'], f'http://testserver{old_file_url}')
    #     self.assertEqual(data['inhoud'], f'http://testserver{new_file_url}')
    #
    #     # download
    #     self._download_file()
