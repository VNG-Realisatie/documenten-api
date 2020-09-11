import uuid
from base64 import b64encode
from datetime import date
from unittest.mock import patch

from django.test import override_settings
from django.utils import timezone

from freezegun import freeze_time
from privates.test import temp_private_root
from rest_framework import status
from rest_framework.test import APITestCase
from vng_api_common.tests import (
    JWTAuthMixin,
    get_operation_url,
    get_validation_errors,
    reverse,
)

from drc.datamodel.models import (
    EnkelvoudigInformatieObject,
    EnkelvoudigInformatieObjectCanonical,
)
from drc.datamodel.tests.factories import (
    EnkelvoudigInformatieObjectFactory,
    ObjectInformatieObjectFactory,
)

INFORMATIEOBJECTTYPE = (
    "https://example.com/ztc/api/v1/catalogus/1/informatieobjecttype/1"
)


@freeze_time("2018-06-27")
@temp_private_root()
class EnkelvoudigInformatieObjectAPITests(JWTAuthMixin, APITestCase):

    list_url = reverse(EnkelvoudigInformatieObject)
    heeft_alle_autorisaties = True

    @override_settings(LINK_FETCHER="vng_api_common.mocks.link_fetcher_200")
    @patch("vng_api_common.validators.fetcher")
    @patch("vng_api_common.validators.obj_has_shape", return_value=True)
    def test_create(self, *mocks):
        content = {
            "identificatie": uuid.uuid4().hex,
            "bronorganisatie": "159351741",
            "creatiedatum": "2018-06-27",
            "titel": "detailed summary",
            "auteur": "test_auteur",
            "formaat": "txt",
            "taal": "eng",
            "bestandsnaam": "dummy.txt",
            "inhoud": b64encode(b"some file content").decode("utf-8"),
            "bestandsomvang": 17,
            "link": "http://een.link",
            "beschrijving": "test_beschrijving",
            "informatieobjecttype": INFORMATIEOBJECTTYPE,
            "vertrouwelijkheidaanduiding": "openbaar",
        }

        # Send to the API
        response = self.client.post(self.list_url, content)

        # Test response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

        # Test database
        self.assertEqual(EnkelvoudigInformatieObject.objects.count(), 1)
        stored_object = EnkelvoudigInformatieObject.objects.get()

        self.assertEqual(stored_object.identificatie, content["identificatie"])
        self.assertEqual(stored_object.bronorganisatie, "159351741")
        self.assertEqual(stored_object.creatiedatum, date(2018, 6, 27))
        self.assertEqual(stored_object.titel, "detailed summary")
        self.assertEqual(stored_object.auteur, "test_auteur")
        self.assertEqual(stored_object.formaat, "txt")
        self.assertEqual(stored_object.taal, "eng")
        self.assertEqual(stored_object.versie, 1)
        self.assertAlmostEqual(stored_object.begin_registratie, timezone.now())
        self.assertEqual(stored_object.bestandsnaam, "dummy.txt")
        self.assertEqual(stored_object.inhoud.read(), b"some file content")
        self.assertEqual(stored_object.bestandsomvang, 17)
        self.assertEqual(stored_object.link, "http://een.link")
        self.assertEqual(stored_object.beschrijving, "test_beschrijving")
        self.assertEqual(stored_object.informatieobjecttype, INFORMATIEOBJECTTYPE)
        self.assertEqual(stored_object.vertrouwelijkheidaanduiding, "openbaar")

        expected_url = reverse(
            "enkelvoudiginformatieobject-detail",
            kwargs={"version": "1", "uuid": stored_object.uuid},
        )
        expected_file_url = get_operation_url(
            "enkelvoudiginformatieobject_download", uuid=stored_object.uuid
        )

        expected_response = content.copy()
        expected_response.update(
            {
                "url": f"http://testserver{expected_url}",
                "inhoud": f"http://testserver{expected_file_url}?versie=1",
                "versie": 1,
                "beginRegistratie": stored_object.begin_registratie.isoformat().replace(
                    "+00:00", "Z"
                ),
                "vertrouwelijkheidaanduiding": "openbaar",
                "bestandsomvang": stored_object.inhoud.size,
                "integriteit": {"algoritme": "", "waarde": "", "datum": None},
                "ontvangstdatum": None,
                "verzenddatum": None,
                "ondertekening": {"soort": "", "datum": None},
                "indicatieGebruiksrecht": None,
                "status": "",
                "locked": False,
                "bestandsdelen": [],
                "lock": "",
            }
        )
        response_data = response.json()
        self.assertEqual(sorted(response_data.keys()), sorted(expected_response.keys()))

        for key in response_data.keys():
            with self.subTest(field=key):
                self.assertEqual(response_data[key], expected_response[key])

    def test_read(self):
        test_object = EnkelvoudigInformatieObjectFactory.create(
            informatieobjecttype=INFORMATIEOBJECTTYPE
        )

        # Retrieve from the API
        detail_url = reverse(
            "enkelvoudiginformatieobject-detail",
            kwargs={"version": "1", "uuid": test_object.uuid},
        )

        response = self.client.get(detail_url)

        # Test response
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        file_url = get_operation_url(
            "enkelvoudiginformatieobject_download", uuid=test_object.uuid
        )
        expected = {
            "url": f"http://testserver{detail_url}",
            "identificatie": test_object.identificatie,
            "bronorganisatie": test_object.bronorganisatie,
            "creatiedatum": "2018-06-27",
            "titel": "some titel",
            "auteur": "some auteur",
            "status": "",
            "formaat": "some formaat",
            "taal": "nld",
            "beginRegistratie": test_object.begin_registratie.isoformat().replace(
                "+00:00", "Z"
            ),
            "versie": 1,
            "bestandsnaam": "",
            "inhoud": f"http://testserver{file_url}?versie=1",
            "bestandsomvang": test_object.inhoud.size,
            "link": "",
            "beschrijving": "",
            "ontvangstdatum": None,
            "verzenddatum": None,
            "ondertekening": {"soort": "", "datum": None},
            "indicatieGebruiksrecht": None,
            "vertrouwelijkheidaanduiding": "openbaar",
            "integriteit": {"algoritme": "", "waarde": "", "datum": None},
            "informatieobjecttype": INFORMATIEOBJECTTYPE,
            "locked": False,
            "bestandsdelen": [],
        }
        response_data = response.json()
        self.assertEqual(sorted(response_data.keys()), sorted(expected.keys()))

        for key in response_data.keys():
            with self.subTest(field=key):
                self.assertEqual(response_data[key], expected[key])

    def test_eio_download_with_accept_application_octet_stream_header(self):
        eio = EnkelvoudigInformatieObjectFactory.create(
            beschrijving="beschrijving1", inhoud__data=b"inhoud1"
        )

        eio_url = get_operation_url(
            "enkelvoudiginformatieobject_download", uuid=eio.uuid
        )

        response = self.client.get(eio_url, HTTP_ACCEPT="application/octet-stream")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_bestandsomvang(self):
        """
        Assert that the API shows the filesize.
        """
        test_object = EnkelvoudigInformatieObjectFactory.create(
            inhoud__data=b"some content"
        )

        # Retrieve from the API
        detail_url = reverse(
            "enkelvoudiginformatieobject-detail",
            kwargs={"version": "1", "uuid": test_object.uuid},
        )

        response = self.client.get(detail_url)

        # Test response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["bestandsomvang"], 12)  # 12 bytes

    @override_settings(LINK_FETCHER="vng_api_common.mocks.link_fetcher_200")
    @patch("vng_api_common.validators.fetcher")
    @patch("vng_api_common.validators.obj_has_shape", return_value=True)
    def test_integrity_empty(self, *mocks):
        """
        Assert that integrity is optional.
        """
        content = {
            "identificatie": uuid.uuid4().hex,
            "bronorganisatie": "159351741",
            "creatiedatum": "2018-12-13",
            "titel": "Voorbeelddocument",
            "auteur": "test_auteur",
            "formaat": "text/plain",
            "taal": "eng",
            "bestandsnaam": "dummy.txt",
            "vertrouwelijkheidaanduiding": "openbaar",
            "inhoud": b64encode(b"some file content").decode("utf-8"),
            "bestandsomvang": 17,
            "informatieobjecttype": "https://example.com/ztc/api/v1/catalogus/1/informatieobjecttype/1",
            "integriteit": None,
        }

        # Send to the API
        response = self.client.post(self.list_url, content)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        stored_object = EnkelvoudigInformatieObject.objects.get()
        self.assertEqual(
            stored_object.integriteit, {"algoritme": "", "waarde": "", "datum": None}
        )

    @override_settings(LINK_FETCHER="vng_api_common.mocks.link_fetcher_200")
    @patch("vng_api_common.validators.fetcher")
    @patch("vng_api_common.validators.obj_has_shape", return_value=True)
    def test_integrity_provided(self, *mocks):
        """
        Assert that integrity is saved.
        """
        content = {
            "identificatie": uuid.uuid4().hex,
            "bronorganisatie": "159351741",
            "creatiedatum": "2018-12-13",
            "titel": "Voorbeelddocument",
            "auteur": "test_auteur",
            "formaat": "text/plain",
            "taal": "eng",
            "bestandsnaam": "dummy.txt",
            "vertrouwelijkheidaanduiding": "openbaar",
            "inhoud": b64encode(b"some file content").decode("utf-8"),
            "bestandsomvang": 17,
            "informatieobjecttype": "https://example.com/ztc/api/v1/catalogus/1/informatieobjecttype/1",
            "integriteit": {
                "algoritme": "md5",
                "waarde": "27c3a009a3cbba674d0b3e836f2d4685",
                "datum": "2018-12-13",
            },
        }

        # Send to the API
        response = self.client.post(self.list_url, content)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        stored_object = EnkelvoudigInformatieObject.objects.get()
        self.assertEqual(
            stored_object.integriteit,
            {
                "algoritme": "md5",
                "waarde": "27c3a009a3cbba674d0b3e836f2d4685",
                "datum": date(2018, 12, 13),
            },
        )

    def test_filter_by_identification(self):
        EnkelvoudigInformatieObjectFactory.create(identificatie="foo")
        EnkelvoudigInformatieObjectFactory.create(identificatie="bar")

        response = self.client.get(self.list_url, {"identificatie": "foo"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()["results"]

        self.assertEqual(len(response_data), 1)
        self.assertEqual(response_data[0]["identificatie"], "foo")

    def test_destroy_no_relations_allowed(self):
        """
        Assert that destroying is possible when there are no relations.
        """
        eio = EnkelvoudigInformatieObjectFactory.create()
        url = reverse(eio)

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_destroy_with_relations_not_allowed(self):
        """
        Assert that destroying is not possible when there are relations.
        """
        eio = EnkelvoudigInformatieObjectFactory.create()
        ObjectInformatieObjectFactory.create(informatieobject=eio.canonical)
        url = reverse(eio)

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error = get_validation_errors(response, "nonFieldErrors")
        self.assertEqual(error["code"], "pending-relations")

    def test_validate_unknown_query_params(self):
        EnkelvoudigInformatieObjectFactory.create_batch(2)
        url = get_operation_url("enkelvoudiginformatieobject_list")

        response = self.client.get(url, {"someparam": "somevalue"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error = get_validation_errors(response, "nonFieldErrors")
        self.assertEqual(error["code"], "unknown-parameters")

    @override_settings(LINK_FETCHER="vng_api_common.mocks.link_fetcher_200")
    @patch("vng_api_common.validators.fetcher")
    @patch("vng_api_common.validators.obj_has_shape", return_value=True)
    def test_invalid_inhoud(self, *mocks):
        content = {
            "identificatie": uuid.uuid4().hex,
            "bronorganisatie": "159351741",
            "creatiedatum": "2018-06-27",
            "titel": "detailed summary",
            "auteur": "test_auteur",
            "formaat": "txt",
            "taal": "eng",
            "bestandsnaam": "dummy.txt",
            "inhoud": [1, 2, 3],
            "link": "http://een.link",
            "beschrijving": "test_beschrijving",
            "informatieobjecttype": INFORMATIEOBJECTTYPE,
            "vertrouwelijkheidaanduiding": "openbaar",
        }

        # Send to the API
        response = self.client.post(self.list_url, content)

        # Test response
        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST, response.data
        )

        error = get_validation_errors(response, "inhoud")
        self.assertEqual(error["code"], "invalid")


@override_settings(LINK_FETCHER="vng_api_common.mocks.link_fetcher_200")
class EnkelvoudigInformatieObjectVersionHistoryAPITests(JWTAuthMixin, APITestCase):
    list_url = reverse(EnkelvoudigInformatieObject)
    heeft_alle_autorisaties = True

    @patch("vng_api_common.validators.fetcher")
    @patch("vng_api_common.validators.obj_has_shape", return_value=True)
    def test_eio_update(self, *mocks):
        eio = EnkelvoudigInformatieObjectFactory.create(
            beschrijving="beschrijving1", informatieobjecttype=INFORMATIEOBJECTTYPE
        )

        eio_url = reverse(
            "enkelvoudiginformatieobject-detail", kwargs={"uuid": eio.uuid}
        )

        eio_response = self.client.get(eio_url)
        eio_data = eio_response.data

        lock = self.client.post(f"{eio_url}/lock").data["lock"]
        eio_data.update(
            {
                "beschrijving": "beschrijving2",
                "inhoud": b64encode(b"aaaaa"),
                "bestandsomvang": 5,
                "lock": lock,
            }
        )

        for i in ["integriteit", "ondertekening"]:
            eio_data.pop(i)

        response = self.client.put(eio_url, eio_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        response_data = response.json()

        self.assertEqual(response_data["beschrijving"], "beschrijving2")

        eios = EnkelvoudigInformatieObject.objects.filter(uuid=eio.uuid).order_by(
            "-versie"
        )
        self.assertEqual(len(eios), 2)

        latest_version = eios.first()
        self.assertEqual(latest_version.versie, 2)
        self.assertEqual(latest_version.beschrijving, "beschrijving2")

        first_version = eios[1]
        self.assertEqual(first_version.versie, 1)
        self.assertEqual(first_version.beschrijving, "beschrijving1")

    def test_eio_partial_update(self):
        eio = EnkelvoudigInformatieObjectFactory.create(beschrijving="beschrijving1")

        eio_url = reverse(
            "enkelvoudiginformatieobject-detail", kwargs={"uuid": eio.uuid}
        )
        lock = self.client.post(f"{eio_url}/lock").data["lock"]
        response = self.client.patch(
            eio_url, {"beschrijving": "beschrijving2", "lock": lock}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()

        self.assertEqual(response_data["beschrijving"], "beschrijving2")

        eios = EnkelvoudigInformatieObject.objects.filter(uuid=eio.uuid).order_by(
            "-versie"
        )
        self.assertEqual(len(eios), 2)

        latest_version = eios.first()
        self.assertEqual(latest_version.versie, 2)
        self.assertEqual(latest_version.beschrijving, "beschrijving2")

        first_version = eios[1]
        self.assertEqual(first_version.versie, 1)
        self.assertEqual(first_version.beschrijving, "beschrijving1")

    def test_eio_delete(self):
        eio = EnkelvoudigInformatieObjectFactory.create(beschrijving="beschrijving1")

        eio_url = reverse(
            "enkelvoudiginformatieobject-detail", kwargs={"uuid": eio.uuid}
        )
        lock = self.client.post(f"{eio_url}/lock").data["lock"]
        self.client.patch(eio_url, {"beschrijving": "beschrijving2", "lock": lock})

        response = self.client.delete(eio_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(EnkelvoudigInformatieObjectCanonical.objects.exists())
        self.assertFalse(EnkelvoudigInformatieObject.objects.exists())

    def test_eio_detail_retrieves_latest_version(self):
        eio = EnkelvoudigInformatieObjectFactory.create(beschrijving="beschrijving1")

        eio_url = reverse(
            "enkelvoudiginformatieobject-detail", kwargs={"uuid": eio.uuid}
        )
        lock = self.client.post(f"{eio_url}/lock").data["lock"]
        self.client.patch(eio_url, {"beschrijving": "beschrijving2", "lock": lock})

        response = self.client.get(eio_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["beschrijving"], "beschrijving2")

    def test_eio_list_shows_latest_versions(self):
        eio1 = EnkelvoudigInformatieObjectFactory.create(beschrijving="object1")

        eio1_url = reverse(
            "enkelvoudiginformatieobject-detail", kwargs={"uuid": eio1.uuid}
        )
        lock = self.client.post(f"{eio1_url}/lock").data["lock"]
        self.client.patch(eio1_url, {"beschrijving": "object1 versie2", "lock": lock})

        eio2 = EnkelvoudigInformatieObjectFactory.create(beschrijving="object2")

        eio2_url = reverse(
            "enkelvoudiginformatieobject-detail", kwargs={"uuid": eio2.uuid}
        )
        lock = self.client.post(f"{eio2_url}/lock").data["lock"]
        self.client.patch(eio2_url, {"beschrijving": "object2 versie2", "lock": lock})

        response = self.client.get(reverse(EnkelvoudigInformatieObject))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.data["results"]
        self.assertEqual(len(response_data), 2)

        self.assertEqual(response_data[0]["beschrijving"], "object1 versie2")
        self.assertEqual(response_data[1]["beschrijving"], "object2 versie2")

    def test_eio_detail_filter_by_version(self):
        eio = EnkelvoudigInformatieObjectFactory.create(beschrijving="beschrijving1")

        eio_url = reverse(
            "enkelvoudiginformatieobject-detail", kwargs={"uuid": eio.uuid}
        )
        lock = self.client.post(f"{eio_url}/lock").data["lock"]
        self.client.patch(eio_url, {"beschrijving": "beschrijving2", "lock": lock})

        response = self.client.get(eio_url, {"versie": 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["beschrijving"], "beschrijving1")

    def test_eio_detail_filter_by_wrong_version_gives_404(self):
        eio = EnkelvoudigInformatieObjectFactory.create(beschrijving="beschrijving1")

        eio_url = reverse(
            "enkelvoudiginformatieobject-detail", kwargs={"uuid": eio.uuid}
        )
        lock = self.client.post(f"{eio_url}/lock").data["lock"]
        self.client.patch(eio_url, {"beschrijving": "beschrijving2", "lock": lock})

        response = self.client.get(eio_url, {"versie": 100})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_eio_detail_filter_by_registratie_op(self):
        with freeze_time("2019-01-01 12:00:00"):
            eio = EnkelvoudigInformatieObjectFactory.create(
                beschrijving="beschrijving1"
            )

        eio_url = reverse(
            "enkelvoudiginformatieobject-detail", kwargs={"uuid": eio.uuid}
        )
        lock = self.client.post(f"{eio_url}/lock").data["lock"]
        with freeze_time("2019-01-01 13:00:00"):
            self.client.patch(eio_url, {"beschrijving": "beschrijving2", "lock": lock})

        response = self.client.get(eio_url, {"registratieOp": "2019-01-01T12:00:00"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["beschrijving"], "beschrijving1")

    @freeze_time("2019-01-01 12:00:00")
    def test_eio_detail_filter_by_wrong_registratie_op_gives_404(self):
        eio = EnkelvoudigInformatieObjectFactory.create(beschrijving="beschrijving1")

        eio_url = reverse(
            "enkelvoudiginformatieobject-detail", kwargs={"uuid": eio.uuid}
        )
        lock = self.client.post(f"{eio_url}/lock").data["lock"]
        self.client.patch(eio_url, {"beschrijving": "beschrijving2", "lock": lock})

        response = self.client.get(eio_url, {"registratieOp": "2019-01-01T11:59:00"})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_eio_download_content_filter_by_version(self):
        eio = EnkelvoudigInformatieObjectFactory.create(
            beschrijving="beschrijving1", inhoud__data=b"inhoud1"
        )

        eio_url = reverse(
            "enkelvoudiginformatieobject-detail", kwargs={"uuid": eio.uuid}
        )
        lock = self.client.post(f"{eio_url}/lock").data["lock"]
        self.client.patch(
            eio_url,
            {
                "inhoud": b64encode(b"inhoud2"),
                "beschrijving": "beschrijving2",
                "lock": lock,
            },
        )

        response = self.client.get(eio_url, {"versie": "1"})

        response = self.client.get(response.data["inhoud"])
        self.assertEqual(response._container[0], b"inhoud1")

    def test_eio_download_content_filter_by_registratie(self):
        with freeze_time("2019-01-01 12:00:00"):
            eio = EnkelvoudigInformatieObjectFactory.create(
                beschrijving="beschrijving1", inhoud__data=b"inhoud1"
            )

        eio_url = reverse(
            "enkelvoudiginformatieobject-detail", kwargs={"uuid": eio.uuid}
        )
        lock = self.client.post(f"{eio_url}/lock").data["lock"]
        with freeze_time("2019-01-01 13:00:00"):
            self.client.patch(
                eio_url,
                {
                    "inhoud": b64encode(b"inhoud2"),
                    "beschrijving": "beschrijving2",
                    "lock": lock,
                },
            )

        response = self.client.get(eio_url, {"registratieOp": "2019-01-01T12:00:00"})

        response = self.client.get(response.data["inhoud"])
        self.assertEqual(response._container[0], b"inhoud1")


@override_settings(LINK_FETCHER="vng_api_common.mocks.link_fetcher_200")
class EnkelvoudigInformatieObjectPaginationAPITests(JWTAuthMixin, APITestCase):
    list_url = reverse(EnkelvoudigInformatieObject)
    heeft_alle_autorisaties = True

    def test_pagination_default(self):
        """
        Deleting a Besluit causes all related objects to be deleted as well.
        """
        EnkelvoudigInformatieObjectFactory.create_batch(2)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()
        self.assertEqual(response_data["count"], 2)
        self.assertIsNone(response_data["previous"])
        self.assertIsNone(response_data["next"])

    def test_pagination_page_param(self):
        EnkelvoudigInformatieObjectFactory.create_batch(2)

        response = self.client.get(self.list_url, {"page": 1})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()
        self.assertEqual(response_data["count"], 2)
        self.assertIsNone(response_data["previous"])
        self.assertIsNone(response_data["next"])
