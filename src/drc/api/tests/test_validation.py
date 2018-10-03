from django.test import override_settings

from rest_framework import status
from rest_framework.test import APITestCase
from zds_schema.tests import get_validation_errors
from zds_schema.validators import URLValidator

from .utils import reverse


class EnkelvoudigInformatieObjectTests(APITestCase):

    @override_settings(LINK_FETCHER='zds_schema.mocks.link_fetcher_404')
    def test_validate_informatieobjecttype_invalid(self):
        url = reverse('enkelvoudiginformatieobject-list')

        response = self.client.post(url, {
            'informatieobjecttype': 'https://example.com/informatieobjecttype/foo',
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error = get_validation_errors(response, 'informatieobjecttype')
        self.assertEqual(error['code'], URLValidator.code)
