import json
import logging
import re
import uuid
from dataclasses import dataclass
from urllib.request import Request, urlopen

from django.contrib.contenttypes.models import ContentType
from django.urls import resolve
from django.urls.exceptions import Resolver404
from django.utils.translation import ugettext_lazy as _

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from rest_framework import serializers

logger = logging.getLogger(__name__)


def is_uri(s):
    try:
        from urllib.parse import urlparse

        result = urlparse(s)
        return all([result.scheme, result.netloc])
    except:
        return False


@dataclass
class ExpansionField:
    def __init__(
        self,
        id,
        parent,
        sub_field_parent,
        sub_field,
        level,
        struc_type,
        value,
        is_empty,
        code=None,
        parent_code=None,
    ):
        self.id: str = id
        self.parent: str = parent
        self.sub_field_parent: str = sub_field_parent
        self.sub_field: str = sub_field
        self.level: int = level
        self.type: str = struc_type
        self.value: dict = value
        self.is_empty: bool = is_empty
        self.code = code
        self.parent_code = parent_code


EXPAND_QUERY_PARAM = OpenApiParameter(
    name="expand",
    location=OpenApiParameter.QUERY,
    description="Haal details van gelinkte resources direct op. Als je meerdere resources tegelijk wilt ophalen kun je deze scheiden met een komma. Voor het ophalen van resources die een laag dieper genest zijn wordt de punt-notatie gebruikt.",
    type=OpenApiTypes.STR,
    examples=[
        OpenApiExample(name="expand zaaktype", value="zaaktype"),
        OpenApiExample(name="expand status", value="status"),
        OpenApiExample(name="expand status.statustype", value="status.statustype"),
        OpenApiExample(
            name="expand hoofdzaak.status.statustype",
            value="hoofdzaak.status.statustype",
        ),
        OpenApiExample(
            name="expand hoofdzaak.deelzaken.status.statustype",
            value="hoofdzaak.deelzaken.status.statustype",
        ),
    ],
)


class ExpansionMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.expanded_fields = []
        self.called_external_uris = {}
        self.expanded_fields_all = []

    @extend_schema(parameters=[EXPAND_QUERY_PARAM])
    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        response = self.inclusions(response)
        return response

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response = self.inclusions(response)
        return response

    @staticmethod
    def _convert_to_internal_url(url: str) -> str:
        """Convert external uri (https://testserver/api/v1...) to internal uri (/api/v1...)"""
        keyword = "api"
        save_sentence = False
        internal_url = "/"
        if isinstance(url, dict):
            if not url.get("url", None):
                for key, value in url.items():
                    if is_uri(value):
                        url = value
                        break
            else:
                url = url.get("url", None)
        if not url:
            return ""
        for word in url.split("/"):
            if word == keyword:
                save_sentence = True
            if save_sentence:
                internal_url += word + "/"

        return internal_url[:-1]

    def _get_external_data(self, url):
        if isinstance(url, dict):
            if not url.get("url", None):
                for key, value in url.items():
                    if is_uri(value):
                        url = value
                        break
            else:
                url = url.get("url", None)
        if not self.called_external_uris.get(url, None):
            try:
                access_token = self.request.jwt_auth.encoded
                # access_token = "eyJhbGciOiJIUzI1NiIsImNsaWVudF9pZGVudGlmaWVyIjoiYWxsdGhlc2NvcGVzYXJlYmVsb25ndG91czIyMjIyMzEzMjUzMi1SdTgyYkpMUlNRaWciLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJhbGx0aGVzY29wZXNhcmViZWxvbmd0b3VzMjIyMjIzMTMyNTMyLVJ1ODJiSkxSU1FpZyIsImlhdCI6MTY5MjA4MTY1NiwiY2xpZW50X2lkIjoiYWxsdGhlc2NvcGVzYXJlYmVsb25ndG91czIyMjIyMzEzMjUzMi1SdTgyYkpMUlNRaWciLCJ1c2VyX2lkIjoiIiwidXNlcl9yZXByZXNlbnRhdGlvbiI6IiJ9.YBE7OTjwhB7xbBXVM1ZMuPixzY2BbhYz8XAcYxrn_GI"
                headers = {"Authorization": f"Bearer {access_token}"}

                with urlopen(Request(url, headers=headers)) as response:
                    data = json.loads(response.read().decode("utf8"))
                    self.called_external_uris[url] = data
                    return data

            except:
                self.called_external_uris[url] = {}
                return {}
        else:
            return self.called_external_uris[url]

    def _get_internal_data(self, url):
        resolver_match = resolve(self._convert_to_internal_url(url))

        uuid = resolver_match.kwargs["uuid"]

        kwargs = {"uuid": uuid}

        content_type = ContentType.objects.get(
            model=resolver_match.func.initkwargs["basename"]
        )

        obj = content_type.get_object_for_this_type(**kwargs)

        serializer = resolver_match.func.cls.serializer_class

        serializer_exp_field = serializer(obj, context={"request": self.request})

        return serializer_exp_field.data

    def get_data(
        self,
        url: str,
    ) -> dict:
        """Get data from external url or from local database"""

        try:
            return self._get_internal_data(url)
        except Resolver404:
            return self._get_external_data(url)
        except Exception as e:
            logger.error(
                f"The following error occured while trying to get data from {url}: {e}"
            )
            return {}

    def build_expand_schema(
        self,
        result: dict,
        fields_to_expand: list,
    ):
        """Build the expand schema for the response. First, the fields to expand are split on the "." character. Then, the first part of the split is used to get the urls from the result. The urls are then used to get the corresponding data from the external api or from the local database. The data is then gathered/collected inside a list consisted of namedtuples. When all data is collected, it calls the _build_json method which builds the json response."""
        expansion = {"_expand": {}}
        self.expanded_fields_all = []

        for exp_field in fields_to_expand:
            loop_id = str(uuid.uuid4())
            self.expanded_fields = []
            for depth, sub_field in enumerate(exp_field.split(".")):
                if depth == 0:
                    try:
                        urls = result[self.convert_camel_to_snake(sub_field)]
                    except KeyError:
                        try:
                            urls = result[sub_field]
                        except KeyError:
                            raise self.validation_invalid_expand_field(sub_field)

                    if isinstance(urls, list):
                        for x in urls:
                            self._add_to_expanded_fields(
                                loop_id,
                                exp_field,
                                sub_field,
                                depth,
                                data=self.get_data(x),
                                struc_type="list",
                                is_empty=False,
                                original_data=result,
                            )
                        if not urls:
                            expansion["_expand"][sub_field] = []
                    else:
                        if urls:
                            self._add_to_expanded_fields(
                                loop_id,
                                exp_field,
                                sub_field,
                                depth,
                                data=self.get_data(urls),
                                struc_type="dict",
                                is_empty=False,
                                original_data=result,
                            )
                        else:
                            expansion["_expand"][sub_field] = {}

                else:

                    for field in self.expanded_fields:
                        if (
                            field.sub_field == exp_field.split(".")[depth - 1]
                            and field.level == depth - 1
                        ):
                            if self.next_iter_if_value_is_empty(field.value):
                                continue
                            try:
                                urls = field.value[
                                    self.convert_camel_to_snake(sub_field)
                                ]
                            except KeyError:
                                try:
                                    urls = field.value[sub_field]
                                except KeyError:
                                    raise self.validation_invalid_expand_field(
                                        sub_field
                                    )
                            if isinstance(urls, list):
                                if urls:
                                    for x in urls:
                                        self._add_to_expanded_fields(
                                            loop_id,
                                            exp_field,
                                            sub_field,
                                            depth,
                                            data=self.get_data(x),
                                            struc_type="list",
                                            is_empty=False,
                                            original_data=result,
                                            field=field,
                                        )
                                else:
                                    self._add_to_expanded_fields(
                                        loop_id,
                                        exp_field,
                                        sub_field,
                                        depth,
                                        data={},
                                        struc_type="list",
                                        is_empty=True,
                                        original_data=result,
                                        field=field,
                                    )
                            else:
                                if urls:
                                    self._add_to_expanded_fields(
                                        loop_id,
                                        exp_field,
                                        sub_field,
                                        depth,
                                        data=self.get_data(urls),
                                        struc_type="dict",
                                        is_empty=False,
                                        original_data=result,
                                        field=field,
                                    )

                                else:
                                    self._add_to_expanded_fields(
                                        loop_id,
                                        exp_field,
                                        sub_field,
                                        depth,
                                        data={},
                                        struc_type="dict",
                                        is_empty=True,
                                        original_data=result,
                                        field=field,
                                    )
                        else:
                            if self.next_iter_if_value_is_empty(field.value):
                                field.is_empty = True

            if not self.expanded_fields:
                continue
            expansion = self._build_json(expansion)

        for key in ["loop_id", "depth", "code", "parent_code"]:
            self.remove_key(expansion, key)

        result["_expand"].update(expansion["_expand"])

    def _build_json(self, expansion: dict) -> dict:
        max_value = max(self.expanded_fields, key=lambda x: x.level).level
        for i in range(max_value + 1):
            specific_levels = [x for x in self.expanded_fields if x.level == i]

            for index, fields_of_level in enumerate(specific_levels):
                if index == 0 and i == 0:
                    if fields_of_level.type == "list" and not expansion["_expand"].get(
                        fields_of_level.sub_field, None
                    ):
                        expansion["_expand"][fields_of_level.sub_field] = []
                    elif fields_of_level.type == "dict" and not expansion[
                        "_expand"
                    ].get(fields_of_level.sub_field, None):
                        expansion["_expand"][fields_of_level.sub_field] = {}

                if i == 0:
                    if fields_of_level.type == "list":
                        skip = False
                        for field_dict in expansion["_expand"][
                            fields_of_level.sub_field
                        ]:
                            if fields_of_level.value["url"] == field_dict["url"]:
                                skip = True
                        if not skip:
                            expansion["_expand"][fields_of_level.sub_field].append(
                                fields_of_level.value
                            )

                    elif fields_of_level.type == "dict" and not expansion[
                        "_expand"
                    ].get(fields_of_level.sub_field, None):

                        expansion["_expand"][
                            fields_of_level.sub_field
                        ] = fields_of_level.value

                else:
                    match = self.get_parent_dict(
                        expansion["_expand"],
                        target_key1="url",
                        target_key3="code",
                        target_value1=fields_of_level.parent,
                        target_value3=fields_of_level.parent_code,
                        level=i,
                        field_level=fields_of_level.level,
                    )

                    if not match:
                        continue

                    for parent_dict in match:
                        if isinstance(parent_dict, str):
                            if parent_dict != fields_of_level.sub_field_parent:
                                continue
                            parent_dict = match[parent_dict]
                        if parent_dict.get("url", None) != fields_of_level.parent:
                            continue

                        if not parent_dict.get("_expand", {}) and isinstance(
                            parent_dict[fields_of_level.sub_field], list
                        ):

                            parent_dict["_expand"] = {fields_of_level.sub_field: []}
                        elif not parent_dict.get("_expand", {}).get(
                            fields_of_level.sub_field, None
                        ) and isinstance(parent_dict[fields_of_level.sub_field], list):

                            parent_dict["_expand"].update(
                                {fields_of_level.sub_field: []}
                            )

                        elif not parent_dict.get("_expand", {}) and isinstance(
                            parent_dict[fields_of_level.sub_field], str
                        ):
                            parent_dict["_expand"] = {fields_of_level.sub_field: {}}

                        elif not parent_dict.get("_expand", {}).get(
                            fields_of_level.sub_field, None
                        ) and isinstance(parent_dict[fields_of_level.sub_field], str):
                            parent_dict["_expand"].update(
                                {fields_of_level.sub_field: {}}
                            )

                        if isinstance(parent_dict[fields_of_level.sub_field], list):
                            add = True
                            for expand in parent_dict["_expand"][
                                fields_of_level.sub_field
                            ]:
                                if expand["url"] == fields_of_level.value["url"]:
                                    add = False

                            if add:
                                if fields_of_level.is_empty:
                                    parent_dict["_expand"][
                                        fields_of_level.sub_field
                                    ] = []
                                else:
                                    parent_dict["_expand"][
                                        fields_of_level.sub_field
                                    ].append(fields_of_level.value)

                        elif isinstance(parent_dict[fields_of_level.sub_field], str):
                            if fields_of_level.is_empty:
                                parent_dict["_expand"].update(
                                    {fields_of_level.sub_field: {}}
                                )
                            else:
                                parent_dict["_expand"].update(
                                    {fields_of_level.sub_field: fields_of_level.value}
                                )
                        elif parent_dict[fields_of_level.sub_field] is None:
                            try:
                                parent_dict["_expand"].update(
                                    {fields_of_level.sub_field: fields_of_level.value}
                                )
                            except KeyError:
                                parent_dict["_expand"] = {fields_of_level.sub_field: {}}

        return expansion

    def get_parent_dict(
        self,
        data,
        target_key1,
        target_key3,
        target_value1,
        target_value3,
        level,
        field_level,
        parent=None,
    ):
        """Get the parent dictionary of the target value."""

        if isinstance(data, dict):
            if target_value3:
                to_compare = bool(
                    data.get(target_key1) == target_value1
                    and data.get(target_key3) == target_value3
                    and data.get("depth") == level - 1
                )
            elif not target_value3:
                to_compare = bool(
                    data.get(target_key1) == target_value1
                    and data.get("depth") == level - 1
                )

            if to_compare:
                return parent

            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    parent_dict = self.get_parent_dict(
                        value,
                        target_key1,
                        target_key3,
                        target_value1,
                        target_value3,
                        level,
                        field_level,
                        parent=data,
                    )
                    if parent_dict is not None:
                        return parent_dict

        elif isinstance(data, list):
            for item in data:
                if isinstance(item, (dict, list)):
                    parent_dict = self.get_parent_dict(
                        item,
                        target_key1,
                        target_key3,
                        target_value1,
                        target_value3,
                        level,
                        field_level,
                        parent=data,
                    )
                    if parent_dict is not None:
                        return parent_dict
        return None

    def remove_key(self, data, target_key):
        if isinstance(data, dict):
            for key in list(data.keys()):
                if key == target_key:
                    del data[key]
                elif isinstance(data[key], (dict, list)):
                    self.remove_key(data[key], target_key)
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, (dict, list)):
                    self.remove_key(item, target_key)

    def inclusions(self, response):
        expand_filter = self.request.query_params.get("expand", "")
        if self.action == "_zoek":
            expand_filter = self.get_search_input().get("expand", "")
        if expand_filter:
            fields_to_expand = expand_filter.split(",")
            if self.action == "list" or self.action == "_zoek":
                for response_data in (
                    response.data
                    if isinstance(response.data, list)
                    else response.data["results"]
                ):
                    response_data["_expand"] = {}
                    self.build_expand_schema(
                        response_data,
                        fields_to_expand,
                    )
            elif self.action == "retrieve":
                response.data["_expand"] = {}
                self.build_expand_schema(response.data, fields_to_expand)

        return response

    @staticmethod
    def convert_camel_to_snake(string):
        # Insert underscore before each capital letter
        import re

        snake_case = re.sub(r"(?<!^)(?=[A-Z])", "_", string).lower()
        return snake_case

    @staticmethod
    def validation_invalid_expand_field(field):
        return serializers.ValidationError(
            {
                "expand": _(
                    f"The submitted field {field} did not match any fields in the expandable json"
                )
            },
            code="invalid-expand-field",
        )

    def next_iter_if_value_is_empty(self, value):
        values = value.copy()
        self.remove_key(values, "loop_id")
        self.remove_key(values, "depth")
        self.remove_key(values, "code")
        self.remove_key(values, "parent_code")
        if not values:
            return True
        return False

    def _add_to_expanded_fields(
        self,
        loop_id,
        exp_field,
        sub_field,
        depth,
        data,
        struc_type,
        is_empty,
        original_data,
        field=None,
    ):
        unique_code = uuid.uuid4().hex

        for old_field in self.expanded_fields_all:
            if (
                old_field.level == depth
                and old_field.sub_field == sub_field
                and loop_id != old_field.id
            ):
                old_field.id = loop_id
                self.expanded_fields.append(old_field)
                return

        copy_data = data.copy()
        field_to_add = ExpansionField(
            loop_id,
            field.value["url"] if depth != 0 else original_data["url"],
            exp_field.split(".")[depth - 1] if depth != 0 else None,
            sub_field,
            depth,
            struc_type,
            copy_data,
            is_empty,
            code=unique_code,
            parent_code=field.code if depth > 0 else unique_code,
        )

        field_to_add.value["loop_id"] = loop_id
        field_to_add.value["depth"] = field_to_add.level
        field_to_add.value["parent_code"] = field.code if depth > 0 else unique_code
        field_to_add.value["code"] = unique_code if depth > 0 else unique_code
        self.expanded_fields.append(field_to_add)
        self.expanded_fields_all.append(field_to_add)


class ExpandFieldValidator:
    MAX_STEPS_DEPTH = 10
    MAX_EXPANDED_FIELDS = 20
    REGEX = r"^[\w']+([.,][\w']+)*$"  # regex checks for field names separated by . or , (e.g "rollen,rollen.statussen")

    def _validate_maximum_depth_reached(self, expanded_fields):
        """Validate maximum iterations to prevent infinite recursion"""
        for expand_combination in expanded_fields.split(","):
            if len(expand_combination.split(".")) > self.MAX_STEPS_DEPTH:
                raise serializers.ValidationError(
                    {
                        "expand": _(
                            f"The submitted fields have surpassed its maximum recursion limit of {self.MAX_STEPS_DEPTH}"
                        )
                    },
                    code="recursion-limit",
                )
            elif len(expanded_fields.split(",")) > self.MAX_EXPANDED_FIELDS:
                raise serializers.ValidationError(
                    {
                        "expand": _(
                            f"The submitted expansion string has surpassed its maximum limit of {self.MAX_EXPANDED_FIELDS}"
                        )
                    },
                    code="max-str-length",
                )

    def _validate_regex(self, expanded_fields):
        if not re.match(self.REGEX, expanded_fields):
            raise serializers.ValidationError(
                {
                    "expand": _(
                        f"The submitted expand fields do not match the required regex of {self.REGEX}"
                    )
                },
                code="expand-format-error",
            )

    def list(self, request, *args, **kwargs):
        expand_filter = request.query_params.get("expand", "")

        if not request.query_params or not expand_filter:
            return super().list(request, *args, **kwargs)

        self._validate_regex(expand_filter)
        self._validate_maximum_depth_reached(expand_filter)
        return super().list(request, *args, **kwargs)
