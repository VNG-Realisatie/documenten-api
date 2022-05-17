from django.utils.translation import ugettext_lazy as _

from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView
from vng_api_common.views import exception_handler


class Http413(APIException):
    status_code = status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
    default_detail = _("Request entity too large")
    default_code = "entity_too_large"


class ProblemJSONRenderer(JSONRenderer):
    media_type = "application/problem+json"


class ErrorView(APIView):
    exception_class = None
    title = None
    swagger_schema = None

    renderer_classes = (ProblemJSONRenderer,)

    def get(self, request, *args, **kwargs):
        exc = self.exception_class(detail=self.title)
        response = exception_handler(exc, {"request": request})
        return response


class HTTP413View(ErrorView):
    exception_class = Http413
    title = _("The request body exceeded the configured maximum body size.")


class HTTP500View(ErrorView):
    exception_class = APIException
