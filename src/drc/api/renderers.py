import json

from djangorestframework_camel_case.render import CamelCaseJSONRenderer
from rest_framework.renderers import BaseRenderer
from json.decoder import JSONDecodeError


class BinaryFileRenderer(BaseRenderer):
    media_type = "application/octet-stream"
    format = None
    charset = None
    render_style = "binary"

    def render(
        self, data, media_type=None, renderer_context=None
    ):  # When trying to download a non-existing file, `data` contains a string instead of binary data.
        # The string needs to be encoded as UTF-8, or it will be coerced into a bytestring using self.charset,
        # which will cause an error (issue #584)
        if isinstance(data, str):
            return data.encode("utf-8")
        return data


class CustomCamelCaseJSONRenderer(CamelCaseJSONRenderer):
    """search and replace Expand with _expand in the response"""

    def render(self, data, *args, **kwargs):
        rendered = super().render(data, *args, **kwargs)
        try:
            list_of_responses = json.loads(rendered)
        except JSONDecodeError:
            return rendered
        if isinstance(list_of_responses, dict):
            if list_of_responses.get("Expand", None):
                list_of_responses["_expand"] = list_of_responses.pop("Expand")
        elif isinstance(list_of_responses, list):
            for response in list_of_responses:
                if response.get("Expand", None):
                    response["_expand"] = response.pop("Expand")
        data_bytes = json.dumps(list_of_responses).encode("utf-8")
        return data_bytes
