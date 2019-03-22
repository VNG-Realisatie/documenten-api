import json
import base64

from django.conf import settings
from django.test import override_settings

from mock import patch
from rest_framework import status
from rest_framework.test import APITestCase
from vng_api_common.constants import VertrouwelijkheidsAanduiding
from vng_api_common.tests import JWTScopesMixin, get_operation_url

from drc.api.scopes import SCOPE_DOCUMENTEN_ALLES_VERWIJDEREN
from drc.datamodel.tests.factories import EnkelvoudigInformatieObjectFactory, ObjectInformatieObjectFactory, GebruiksrechtenFactory


@override_settings(LINK_FETCHER='vng_api_common.mocks.link_fetcher_200')
class SendNotifTestCase(JWTScopesMixin, APITestCase):

    def setUp(self):
        super().setUp()

        patcher_sync_create = patch('drc.sync.signals.sync_create')
        self.mocked_sync_create = patcher_sync_create.start()
        self.addCleanup(patcher_sync_create.stop)

        patcher_sync_delete = patch('drc.sync.signals.sync_delete')
        self.mocked_sync_delete = patcher_sync_delete.start()
        self.addCleanup(patcher_sync_delete.stop)

    @override_settings(LINK_FETCHER='vng_api_common.mocks.link_fetcher_200')
    @patch('zds_client.Client.request')
    def test_send_notif_create_enkelvoudiginformatieobject(self, mock_client):
        """
        Registreer een ENKELVOUDIGINFORMATIEOBJECT
        """
        url = get_operation_url('enkelvoudiginformatieobject_create')
        data = {
            'identificatie': 'AMS20180701001',
            'bronorganisatie': '159351741',
            'creatiedatum': '2018-07-01',
            'titel': 'text_extra.txt',
            'auteur': 'ANONIEM',
            'formaat': 'text/plain',
            'taal': 'dut',
            'inhoud': base64.b64encode(b'Extra tekst in bijlage').decode('utf-8'),
            'informatieobjecttype': 'https://example.com/ztc/api/v1/catalogus/1/informatieobjecttype/1',
            'vertrouwelijkheidaanduiding': VertrouwelijkheidsAanduiding.openbaar
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

        data = response.json()
        notif_args, notif_kwargs = mock_client.call_args_list[0]
        msg = json.loads(notif_kwargs['data'])

        self.assertEqual(notif_args[0], settings.NOTIFICATIES_URL)
        self.assertEqual(msg['kanaal'], settings.NOTIFICATIES_KANAAL)
        self.assertEqual(msg['resource'], 'enkelvoudiginformatieobject')
        self.assertEqual(msg['actie'], 'create')
        self.assertEqual(msg['resourceUrl'], data['url'])
        self.assertEqual(msg['kenmerken'][0]['bronorganisatie'], data['bronorganisatie'])
        self.assertEqual(msg['kenmerken'][1]['informatieobjecttype'], data['informatieobjecttype'])
        self.assertEqual(msg['kenmerken'][2]['vertrouwelijkheidaanduiding'], data['vertrouwelijkheidaanduiding'])

    @patch('zds_client.Client.request')
    def test_send_notif_delete_objectinformatieobject(self, mock_client):
        """
        Deleting a EnkelvoudigInformatieObject causes all related objects to be deleted as well.

        """
        io = EnkelvoudigInformatieObjectFactory.create()
        oio = ObjectInformatieObjectFactory.create(informatieobject=io, is_zaak=True)
        oio_delete_url = get_operation_url('objectinformatieobject_delete', uuid=oio.uuid)

        response = self.client.delete(oio_delete_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, response.data)

        notif_args, notif_kwargs = mock_client.call_args_list[0]
        msg = json.loads(notif_kwargs['data'])

        self.assertEqual(notif_args[0], settings.NOTIFICATIES_URL)
        self.assertEqual(msg['kanaal'], settings.NOTIFICATIES_KANAAL)
        self.assertEqual(msg['resource'], 'objectinformatieobject')
        self.assertEqual(msg['actie'], 'destroy')
        self.assertEqual(msg['resourceUrl'], 'http://testserver{}'.format(oio_delete_url))
        self.assertEqual(msg['kenmerken'][0]['bronorganisatie'], io.bronorganisatie)
        self.assertEqual(msg['kenmerken'][1]['informatieobjecttype'], io.informatieobjecttype)
        self.assertEqual(msg['kenmerken'][2]['vertrouwelijkheidaanduiding'], io.vertrouwelijkheidaanduiding)
