from rest_framework.test import APITestCase

from .factories import EnkelvoudigInformatieObjectFactory, PartUploadFactory


class UploadTestCase(APITestCase):

    def test_complete_upload_true(self):
        eio = EnkelvoudigInformatieObjectFactory(
            bronorganisatie=730924658,
            identificatie='5d940d52-ff5e-4b18-a769-977af9130c04'
        )
        canonical = eio.canonical
        PartUploadFactory.create(informatieobject=canonical)

        self.assertTrue(canonical.complete_upload)

    def test_complete_upload_false(self):
        eio = EnkelvoudigInformatieObjectFactory(
            bronorganisatie=730924658,
            identificatie='5d940d52-ff5e-4b18-a769-977af9130c04'
        )
        canonical = eio.canonical
        PartUploadFactory.create(informatieobject=canonical)
        PartUploadFactory.create(informatieobject=canonical, inhoud=None, chunk_size=0)

        self.assertFalse(canonical.complete_upload)

    def test_complete_part_true(self):
        part = PartUploadFactory.create()

        self.assertTrue(part.complete)

    def test_complete_part_false(self):
        part = PartUploadFactory.create(inhoud=None, chunk_size=0)

        self.assertFalse(part.complete)
