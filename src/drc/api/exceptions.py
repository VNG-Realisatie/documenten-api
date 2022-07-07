from django.utils.translation import ugettext_lazy as _

from rest_framework.exceptions import APIException


class OneAddressOnlyVerzendingException(APIException):
    status_code = 400
    default_detail = _(f"verzending must contain precisely one correspondentieadress")
    default_code = "invalid-amount"
