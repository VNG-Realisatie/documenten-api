import uuid
from base64 import b64encode
from datetime import datetime
from unittest.mock import patch

from django.test import override_settings

from freezegun import freeze_time
from rest_framework import status
from rest_framework.test import APITestCase
from vng_api_common.audittrails.models import AuditTrail
from vng_api_common.constants import ObjectTypes
from vng_api_common.tests import JWTAuthMixin, reverse, reverse_lazy
from vng_api_common.utils import get_uuid_from_path

from drc.datamodel.models import (
    EnkelvoudigInformatieObject, EnkelvoudigInformatieObjectCanonical,
    Gebruiksrechten, ObjectInformatieObject
)
from drc.datamodel.tests.factories import EnkelvoudigInformatieObjectFactory

ZAAK = f'http://example.com/zrc/api/v1/zaken/{uuid.uuid4().hex}'


@freeze_time('2019-01-01')
@override_settings(LINK_FETCHER='vng_api_common.mocks.link_fetcher_200')
class AuditTrailTests(JWTAuthMixin, APITestCase):

    informatieobject_list_url = reverse_lazy(EnkelvoudigInformatieObject)
    objectinformatieobject_list_url = reverse_lazy(ObjectInformatieObject)
    gebruiksrechten_list_url = reverse_lazy(Gebruiksrechten)

    heeft_alle_autorisaties = True

    @patch("vng_api_common.validators.fetcher")
    @patch("vng_api_common.validators.obj_has_shape", return_value=True)
    def _create_enkelvoudiginformatieobject(self, *mocks, **HEADERS):
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
            'link': 'http://een.link',
            'beschrijving': 'test_beschrijving',
            'informatieobjecttype': 'https://example.com/ztc/api/v1/catalogus/1/informatieobjecttype/1',
            'vertrouwelijkheidaanduiding': 'openbaar',
        }

        response = self.client.post(self.informatieobject_list_url, content, **HEADERS)

        return response.data

    def test_create_enkelvoudiginformatieobject_audittrail(self):
        informatieobject_data = self._create_enkelvoudiginformatieobject()
        informatieobject_url = informatieobject_data['url']

        audittrails = AuditTrail.objects.filter(hoofd_object=informatieobject_url)
        self.assertEqual(audittrails.count(), 1)

        # Verify that the audittrail for the EnkelvoudigInformatieObject creation contains the correct
        # information
        informatieobject_create_audittrail = audittrails.get()
        self.assertEqual(informatieobject_create_audittrail.bron, 'DRC')
        self.assertEqual(informatieobject_create_audittrail.actie, 'create')
        self.assertEqual(informatieobject_create_audittrail.resultaat, 201)
        self.assertEqual(informatieobject_create_audittrail.oud, None)
        self.assertEqual(informatieobject_create_audittrail.nieuw, informatieobject_data)

    @override_settings(ZDS_CLIENT_CLASS='vng_api_common.mocks.MockClient')
    @patch('vng_api_common.validators.obj_has_shape', return_value=True)
    def test_create_objectinformatieobject_audittrail(self, *mocks):
        informatieobject = EnkelvoudigInformatieObjectFactory.create()

        content = {
            'informatieobject': reverse('enkelvoudiginformatieobject-detail', kwargs={'uuid': informatieobject.uuid}),
            'object': ZAAK,
            'objectType': ObjectTypes.zaak,
        }

        # Send to the API
        objectinformatieobject_response = self.client.post(self.objectinformatieobject_list_url, content).data

        informatieobject_url = objectinformatieobject_response['informatieobject']
        audittrails = AuditTrail.objects.filter(hoofd_object=informatieobject_url)
        self.assertEqual(audittrails.count(), 1)

        # Verify that the audittrail for the ObjectInformatieObject creation
        # contains the correct information
        objectinformatieobject_create_audittrail = audittrails.get()
        self.assertEqual(objectinformatieobject_create_audittrail.bron, 'DRC')
        self.assertEqual(objectinformatieobject_create_audittrail.actie, 'create')
        self.assertEqual(objectinformatieobject_create_audittrail.resultaat, 201)
        self.assertEqual(objectinformatieobject_create_audittrail.oud, None)
        self.assertEqual(objectinformatieobject_create_audittrail.nieuw, objectinformatieobject_response)

    def test_create_and_delete_gebruiksrechten_audittrail(self):
        informatieobject = EnkelvoudigInformatieObjectFactory.create()

        content = {
            'informatieobject': reverse('enkelvoudiginformatieobject-detail', kwargs={'uuid': informatieobject.uuid}),
            'startdatum': datetime.now(),
            'omschrijvingVoorwaarden': 'test'
        }

        gebruiksrechten_response = self.client.post(self.gebruiksrechten_list_url, content).data

        informatieobject_url = gebruiksrechten_response['informatieobject']
        audittrails = AuditTrail.objects.filter(hoofd_object=informatieobject_url)
        self.assertEqual(audittrails.count(), 1)

        # Verify that the audittrail for the Gebruiksrechten creation
        # contains the correct information
        gebruiksrechten_create_audittrail = audittrails.get()
        self.assertEqual(gebruiksrechten_create_audittrail.bron, 'DRC')
        self.assertEqual(gebruiksrechten_create_audittrail.actie, 'create')
        self.assertEqual(gebruiksrechten_create_audittrail.resultaat, 201)
        self.assertEqual(gebruiksrechten_create_audittrail.oud, None)
        self.assertEqual(gebruiksrechten_create_audittrail.nieuw, gebruiksrechten_response)

        delete_response = self.client.delete(gebruiksrechten_response['url'])

        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        audittrails = AuditTrail.objects.filter(hoofd_object=informatieobject_url)
        self.assertEqual(audittrails.count(), 2)

        # Verify that the audittrail for the Gebruiksrechten deletion
        # contains the correct information
        gebruiksrechten_delete_audittrail = audittrails[1]
        self.assertEqual(gebruiksrechten_delete_audittrail.bron, 'DRC')
        self.assertEqual(gebruiksrechten_delete_audittrail.actie, 'destroy')
        self.assertEqual(gebruiksrechten_delete_audittrail.resultaat, 204)
        self.assertEqual(gebruiksrechten_delete_audittrail.oud, gebruiksrechten_response)
        self.assertEqual(gebruiksrechten_delete_audittrail.nieuw, None)

    @patch("vng_api_common.validators.fetcher")
    @patch("vng_api_common.validators.obj_has_shape", return_value=True)
    def test_update_enkelvoudiginformatieobject_audittrail(self, *mocks):
        informatieobject_data = self._create_enkelvoudiginformatieobject()
        informatieobject_url = informatieobject_data['url']

        # lock for update
        eio = EnkelvoudigInformatieObjectCanonical.objects.get()
        eio.lock = '0f60f6d2d2714c809ed762372f5a363a'
        eio.save()

        content = {
            'identificatie': uuid.uuid4().hex,
            'bronorganisatie': '159351741',
            'creatiedatum': '2018-06-27',
            'titel': 'aangepast',
            'auteur': 'aangepaste auteur',
            'formaat': 'txt',
            'taal': 'eng',
            'bestandsnaam': 'dummy.txt',
            'inhoud': b64encode(b'some file content').decode('utf-8'),
            'link': 'http://een.link',
            'beschrijving': 'test_beschrijving',
            'informatieobjecttype': 'https://example.com/ztc/api/v1/catalogus/1/informatieobjecttype/1',
            'vertrouwelijkheidaanduiding': 'openbaar',
            'lock': '0f60f6d2d2714c809ed762372f5a363a'
        }

        informatieobject_response = self.client.put(informatieobject_url, content).data

        audittrails = AuditTrail.objects.filter(hoofd_object=informatieobject_url)
        self.assertEqual(audittrails.count(), 2)

        # Verify that the audittrail for the EnkelvoudigInformatieObject update
        # contains the correct information
        informatieobject_update_audittrail = audittrails[1]
        self.assertEqual(informatieobject_update_audittrail.bron, 'DRC')
        self.assertEqual(informatieobject_update_audittrail.actie, 'update')
        self.assertEqual(informatieobject_update_audittrail.resultaat, 200)

        # locked is False upon InformatieObject creation, but the
        # InformatieObject must be locked before updating is possible, so
        # locked will be True in the version before changes as shown
        # in the audittrail
        informatieobject_data['locked'] = True
        self.assertEqual(informatieobject_update_audittrail.oud, informatieobject_data)
        self.assertEqual(informatieobject_update_audittrail.nieuw, informatieobject_response)

    def test_partial_update_enkelvoudiginformatieobject_audittrail(self):
        informatieobject_data = self._create_enkelvoudiginformatieobject()
        informatieobject_url = informatieobject_data['url']

        # lock for update
        eio = EnkelvoudigInformatieObjectCanonical.objects.get()
        eio.lock = '0f60f6d2d2714c809ed762372f5a363a'
        eio.save()

        informatieobject_response = self.client.patch(
            informatieobject_url,
            {'titel': 'changed',
             'lock': '0f60f6d2d2714c809ed762372f5a363a'}
        ).data

        audittrails = AuditTrail.objects.filter(hoofd_object=informatieobject_url)
        self.assertEqual(audittrails.count(), 2)

        # Verify that the audittrail for the EnkelvoudigInformatieObject
        # partial update contains the correct information
        informatieobject_partial_update_audittrail = audittrails[1]
        self.assertEqual(informatieobject_partial_update_audittrail.bron, 'DRC')
        self.assertEqual(informatieobject_partial_update_audittrail.actie, 'partial_update')
        self.assertEqual(informatieobject_partial_update_audittrail.resultaat, 200)

        # locked is False upon InformatieObject creation, but the
        # InformatieObject must be locked before updating is possible, so
        # locked will be True in the version before changes as shown
        # in the audittrail
        informatieobject_data['locked'] = True
        self.assertEqual(informatieobject_partial_update_audittrail.oud, informatieobject_data)
        self.assertEqual(informatieobject_partial_update_audittrail.nieuw, informatieobject_response)

    def test_audittrail_applicatie_information(self):
        object_response = self._create_enkelvoudiginformatieobject()

        audittrail = AuditTrail.objects.filter(hoofd_object=object_response['url']).get()

        # Verify that the application id stored in the AuditTrail matches
        # the id of the Application used for the request
        self.assertEqual(audittrail.applicatie_id, str(self.applicatie.uuid))

        # Verify that the application representation stored in the AuditTrail
        # matches the label of the Application used for the request
        self.assertEqual(audittrail.applicatie_weergave, self.applicatie.label)

    def test_audittrail_user_information(self):
        object_response = self._create_enkelvoudiginformatieobject()

        audittrail = AuditTrail.objects.filter(hoofd_object=object_response['url']).get()

        # Verify that the user id stored in the AuditTrail matches
        # the user id in the JWT token for the request
        self.assertIn(audittrail.gebruikers_id, self.user_id)

        # Verify that the user representation stored in the AuditTrail matches
        # the user representation in the JWT token for the request
        self.assertEqual(audittrail.gebruikers_weergave, self.user_representation)

    def test_audittrail_toelichting(self):
        toelichting = 'blaaaa'
        object_response = self._create_enkelvoudiginformatieobject(HTTP_X_AUDIT_TOELICHTING=toelichting)

        audittrail = AuditTrail.objects.filter(hoofd_object=object_response['url']).get()

        # Verify that the toelichting stored in the AuditTrail matches
        # the X-Audit-Toelichting header in the HTTP request
        self.assertEqual(audittrail.toelichting, toelichting)

    def test_read_audittrail(self):
        self._create_enkelvoudiginformatieobject()

        eio = EnkelvoudigInformatieObject.objects.get()
        audittrails = AuditTrail.objects.get()
        audittrails_url = reverse(audittrails, kwargs={'enkelvoudiginformatieobject_uuid': eio.uuid})

        response_audittrails = self.client.get(audittrails_url)

        self.assertEqual(response_audittrails.status_code, status.HTTP_200_OK)

    def test_audittrail_resource_weergave(self):
        eio_response = self._create_enkelvoudiginformatieobject()

        eio_uuid = get_uuid_from_path(eio_response['url'])
        eio_unique_representation = EnkelvoudigInformatieObject.objects.get(uuid=eio_uuid).unique_representation()

        audittrail = AuditTrail.objects.filter(hoofd_object=eio_response['url']).get()

        # Verify that the resource weergave stored in the AuditTrail matches
        # the unique representation as defined in the Zaak model
        self.assertIn(audittrail.resource_weergave, eio_unique_representation)
