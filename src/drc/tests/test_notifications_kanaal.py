import json

from django.conf import settings
from django.core.management import call_command

from mock import patch
from rest_framework.test import APITestCase


class CreateNotifKanaalTestCase(APITestCase):

    @patch('zds_client.Client.request')
    def test_kanaal_create_with_name(self, mock_client):
        """
        Test is request to create kanaal is send with specified kanaal name
        """

        call_command('register_kanaal', 'kanaal_test')

        notif_args, notif_kwargs = mock_client.call_args_list[0]
        data = json.loads(notif_kwargs['data'])
        self.assertEqual(notif_args[0], settings.NOTIFICATIES_KANAAL_URL)
        self.assertEqual(notif_kwargs['method'], 'POST')
        self.assertDictEqual(data, {"naam": "kanaal_test"})

    @patch('zds_client.Client.request')
    def test_kanaal_create_without_name(self, mock_client):
        """
        Test is request to create kanaal is send with default kanaal name
        """
        call_command('register_kanaal')

        notif_args, notif_kwargs = mock_client.call_args_list[0]
        data = json.loads(notif_kwargs['data'])
        self.assertEqual(notif_args[0], settings.NOTIFICATIES_KANAAL_URL)
        self.assertEqual(notif_kwargs['method'], 'POST')
        self.assertDictEqual(data, {"naam": settings.NOTIFICATIES_KANAAL})
