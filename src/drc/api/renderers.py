from rest_framework.renderers import BaseRenderer


class BinaryFileRenderer(BaseRenderer):
    media_type = "application/octet-stream"
    format = "octet-stream"  # TODO: test this behavior
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
