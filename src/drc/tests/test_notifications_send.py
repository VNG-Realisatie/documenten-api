import base64
import json
from unittest.mock import patch

from django.conf import settings
from django.test import override_settings

from freezegun import freeze_time
from rest_framework import status
from rest_framework.test import APITestCase
from vng_api_common.constants import VertrouwelijkheidsAanduiding
from vng_api_common.tests import JWTScopesMixin, get_operation_url

from drc.api.scopes import SCOPE_DOCUMENTEN_ALLES_VERWIJDEREN
from drc.datamodel.tests.factories import (
    EnkelvoudigInformatieObjectFactory, GebruiksrechtenFactory,
    ObjectInformatieObjectFactory
)


@freeze_time("2012-01-14")
@override_settings(
    LINK_FETCHER='vng_api_common.mocks.link_fetcher_200',
    NOTIFICATIONS_DISABLED=False
)
class SendNotifTestCase(JWTScopesMixin, APITestCase):

    def setUp(self):
        super().setUp()

        patcher_sync_create = patch('drc.sync.signals.sync_create')
        self.mocked_sync_create = patcher_sync_create.start()
        self.addCleanup(patcher_sync_create.stop)

        patcher_sync_delete = patch('drc.sync.signals.sync_delete')
        self.mocked_sync_delete = patcher_sync_delete.start()
        self.addCleanup(patcher_sync_delete.stop)

    @patch('zds_client.Client.from_url')
    def test_send_notif_create_enkelvoudiginformatieobject(self, mock_client):
        """
        Registreer een ENKELVOUDIGINFORMATIEOBJECT
        """
        client = mock_client.return_value
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
        client.create.assert_called_once_with(
            'notificaties',
            {
                'kanaal': 'documenten',
                'hoofdObject': data['url'],
                'resource': 'enkelvoudiginformatieobject',
                'resourceUrl': data['url'],
                'actie': 'create',
                'aanmaakdatum': '2012-01-14T00:00:00Z',
                'kenmerken': [
                    {'bronorganisatie': '159351741'},
                    {'informatieobjecttype': 'https://example.com/ztc/api/v1/catalogus/1/informatieobjecttype/1'},
                    {'vertrouwelijkheidaanduiding': VertrouwelijkheidsAanduiding.openbaar}
                ]
            }
        )

    @patch('zds_client.Client.from_url')
    def test_send_notif_delete_objectinformatieobject(self, mock_client):
        """
        Deleting a EnkelvoudigInformatieObject causes all related objects to be deleted as well.
        """
        client = mock_client.return_value
        io = EnkelvoudigInformatieObjectFactory.create()
        io_url = get_operation_url('enkelvoudiginformatieobject_read', uuid=io.uuid)
        oio = ObjectInformatieObjectFactory.create(informatieobject=io, is_zaak=True)
        oio_delete_url = get_operation_url('objectinformatieobject_delete', uuid=oio.uuid)

        response = self.client.delete(oio_delete_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, response.data)

        client.create.assert_called_once_with(
            'notificaties',
            {
                'kanaal': 'documenten',
                'hoofdObject': f'http://testserver{io_url}',
                'resource': 'objectinformatieobject',
                'resourceUrl': f'http://testserver{oio_delete_url}',
                'actie': 'destroy',
                'aanmaakdatum': '2012-01-14T00:00:00Z',
                'kenmerken': [
                    {'bronorganisatie': io.bronorganisatie},
                    {'informatieobjecttype': io.informatieobjecttype},
                    {'vertrouwelijkheidaanduiding': io.vertrouwelijkheidaanduiding}
                ]
            }
        )
