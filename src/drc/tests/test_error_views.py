from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase


class ErrorViewTestCase(APITestCase):
    def test_413_error_view(self):
        response = self.client.get(reverse("example-error-413"))

        response_data = response.json()

        self.assertEqual(response.status_code, status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)
        self.assertEqual(response_data["code"], "entity_too_large")
        self.assertEqual(
            response_data["detail"],
            "The request body exceeded the configured maximum body size.",
        )
        self.assertEqual(response_data["title"], "Request entity too large")

        self.assertEqual(response.headers["Content-Type"], "application/problem+json")

    def test_500_error_view(self):
        response = self.client.get(reverse("example-error-500"))

        response_data = response.json()

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response_data["code"], "error")
        self.assertEqual(response_data["detail"], "Er is een serverfout opgetreden.")
        self.assertEqual(response_data["title"], "Er is een serverfout opgetreden.")

        self.assertEqual(response.headers["Content-Type"], "application/problem+json")
