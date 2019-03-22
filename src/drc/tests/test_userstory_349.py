"""
Ref: https://github.com/VNG-Realisatie/gemma-zaken/issues/349
"""
from django.test import override_settings
from mock import patch

from rest_framework import status
from rest_framework.test import APITestCase
from vng_api_common.tests import JWTScopesMixin, get_operation_url

from drc.api.scopes import SCOPE_DOCUMENTEN_ALLES_VERWIJDEREN
from drc.datamodel.models import EnkelvoudigInformatieObject, Gebruiksrechten, ObjectInformatieObject
from drc.datamodel.tests.factories import EnkelvoudigInformatieObjectFactory, GebruiksrechtenFactory, \
    ObjectInformatieObjectFactory


@override_settings(LINK_FETCHER='vng_api_common.mocks.link_fetcher_200')
class US349TestCase(JWTScopesMixin, APITestCase):

    scopes = [SCOPE_DOCUMENTEN_ALLES_VERWIJDEREN]
    zaaktypes = ['*']

    def setUp(self):
        super().setUp()

        patcher_sync_create = patch('drc.sync.signals.sync_create')
        self.mocked_sync_create = patcher_sync_create.start()
        self.addCleanup(patcher_sync_create.stop)

        patcher_sync_delete = patch('drc.sync.signals.sync_delete')
        self.mocked_sync_delete = patcher_sync_delete.start()
        self.addCleanup(patcher_sync_delete.stop)

    def test_delete_document_cascades_properly(self):
        """
        Deleting a EnkelvoudigInformatieObject causes all related objects to be deleted as well.
        """
        informatieobject = EnkelvoudigInformatieObjectFactory.create()

        GebruiksrechtenFactory.create(informatieobject=informatieobject)
        ObjectInformatieObjectFactory.create(informatieobject=informatieobject, is_zaak=True)

        informatieobject_delete_url = get_operation_url('enkelvoudiginformatieobject_delete', uuid=informatieobject.uuid)

        response = self.client.delete(informatieobject_delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, response.data)

        self.assertEqual(EnkelvoudigInformatieObject.objects.all().count(), 0)

        self.assertFalse(Gebruiksrechten.objects.all().exists())
        self.assertFalse(ObjectInformatieObject.objects.all().exists())
