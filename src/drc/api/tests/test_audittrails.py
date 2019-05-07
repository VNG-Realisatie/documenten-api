import uuid
from base64 import b64encode
from unittest.mock import patch

from django.test import override_settings
from django.urls import reverse, reverse_lazy

from rest_framework.test import APITestCase
from vng_api_common.audittrails.models import AuditTrail
from vng_api_common.constants import ObjectTypes

from drc.api.serializers import EnkelvoudigInformatieObjectSerializer
from drc.datamodel.models import EnkelvoudigInformatieObject
from drc.datamodel.tests.factories import EnkelvoudigInformatieObjectFactory

ZAAK = f'http://example.com/zrc/api/v1/zaken/{uuid.uuid4().hex}'

@override_settings(LINK_FETCHER='vng_api_common.mocks.link_fetcher_200')
class AuditTrailTests(APITestCase):

    informatieobject_list_url = reverse_lazy('enkelvoudiginformatieobject-list', kwargs={'version': '1'})
    objectinformatieobject_list_url = reverse_lazy('objectinformatieobject-list', kwargs={'version': '1'})

    def setUp(self):
        super().setUp()

        patcher_sync_create = patch('drc.sync.signals.sync_create')
        self.mocked_sync_create = patcher_sync_create.start()
        self.addCleanup(patcher_sync_create.stop)

        patcher_sync_delete = patch('drc.sync.signals.sync_delete')
        self.mocked_sync_delete = patcher_sync_delete.start()
        self.addCleanup(patcher_sync_delete.stop)

    def test_enkelvoudiginformatieobject_create_audittrail(self):
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

        informatieobject_response = self.client.post(self.informatieobject_list_url, content).data

        informatieobject_url = informatieobject_response['url']
        # TODO make api call instead of querying audittrail model?
        audittrails = AuditTrail.objects.filter(hoofdObject=informatieobject_url)
        self.assertEqual(audittrails.count(), 1)

        # Verify that the audittrail for the Zaak creation contains the correct
        # information
        informatieobject_create_audittrail = audittrails.first()
        self.assertEqual(informatieobject_create_audittrail.bron, 'DRC')
        self.assertEqual(informatieobject_create_audittrail.actie, 'create')
        self.assertEqual(informatieobject_create_audittrail.resultaat, 201)
        self.assertEqual(informatieobject_create_audittrail.oud, None)
        self.assertEqual(informatieobject_create_audittrail.nieuw, informatieobject_response)

    def test_objectinformatieobject_create_audittrail(self):
        informatieobject = EnkelvoudigInformatieObjectFactory.create()
        informatieobject_uri = reverse('enkelvoudiginformatieobject-detail', kwargs={
            'version': '1',
            'uuid': informatieobject.uuid,
        })

        content = {
            'informatieobject': 'http://testserver' + informatieobject_uri,
            'object': ZAAK,
            'objectType': ObjectTypes.zaak,
        }

        # Send to the API
        objectinformatieobject_response = self.client.post(self.objectinformatieobject_list_url, content).data

        informatieobject_url = objectinformatieobject_response['informatieobject']
        audittrails = AuditTrail.objects.filter(hoofdObject=informatieobject_url)
        self.assertEqual(audittrails.count(), 1)

        # Verify that the audittrail for the ObjectInformatieObject creation
        # contains the correct information
        objectinformatieobject_create_audittrail = audittrails.first()
        self.assertEqual(objectinformatieobject_create_audittrail.bron, 'DRC')
        self.assertEqual(objectinformatieobject_create_audittrail.actie, 'create')
        self.assertEqual(objectinformatieobject_create_audittrail.resultaat, 201)
        self.assertEqual(objectinformatieobject_create_audittrail.oud, None)
        self.assertEqual(objectinformatieobject_create_audittrail.nieuw, objectinformatieobject_response)

    # TODO tests for gebruiksrechten, put, patch, delete
