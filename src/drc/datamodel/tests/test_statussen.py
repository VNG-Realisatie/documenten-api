"""
Tests for the business logic w/r to statussen, from RGBZ.
"""
from datetime import date

from django.test import TestCase
from django.core.exceptions import ValidationError

from .factories import EnkelvoudigInformatieObjectFactory
from ..constants import Statussen


class StatusTests(TestCase):

    def test_empty_status_empty_ontvangstdatum(self):
        try:
            EnkelvoudigInformatieObjectFactory.create(ontvangstdatum=None, status='')
        except Exception:
            self.fail("Empty status and ontvangstdatum should be possible")

    def test_empty_status_non_empty_ontvangstdatum(self):
        try:
            EnkelvoudigInformatieObjectFactory.create(
                ontvangstdatum=date(2018, 12, 24),
                status=''
            )
        except Exception:
            self.fail("Empty status and non-empty ontvangstdatum should be possible")

    def test_ontvangstdatum_invalid_status(self):
        for invalid_status in Statussen.invalid_for_received():
            with self.subTest(status=invalid_status):
                with self.assertRaises(ValidationError) as exc_context:
                    EnkelvoudigInformatieObjectFactory.create(
                        ontvangstdatum=date(2018, 12, 24),
                        status=invalid_status
                    )
                self.assertEqual(exc_context.exception.code, 'invalid_for_received')
