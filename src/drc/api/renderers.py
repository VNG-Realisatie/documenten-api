import json
from json.decoder import JSONDecodeError

from djangorestframework_camel_case.render import CamelCaseJSONRenderer
from rest_framework.renderers import BaseRenderer


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
        except JSONDecodeError as e:
            return rendered

        list_of_responses = self.replace_key_nested_dicts(
            list_of_responses, "Expand", "_expand"
        )
        data_bytes = json.dumps(list_of_responses).encode("utf-8")
        return data_bytes

    def replace_key_nested_dicts(self, nested_dicts, old_key, new_key):
        if isinstance(nested_dicts, list):
            new_list = []
            for dictionary in nested_dicts:
                new_list.append(self.replace_key(dictionary, old_key, new_key))
            return new_list
        else:
            return self.replace_key(nested_dicts, old_key, new_key)

    def replace_key(self, dictionary, old_key, new_key):
        if isinstance(dictionary, dict):
            new_dict = {}
            for key, value in dictionary.items():
                if key == old_key:
                    key = new_key
                new_dict[key] = self.replace_key(value, old_key, new_key)
            return new_dict
        elif isinstance(dictionary, list):
            new_list = []
            for item in dictionary:
                new_list.append(self.replace_key(item, old_key, new_key))
            return new_list
        else:
            return dictionary
