import json
import re
import uuid
from collections import namedtuple
from urllib.request import Request, urlopen

from django.contrib.contenttypes.models import ContentType
from django.urls import Resolver404, resolve
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers


class ExpansionMixin:
    ExpansionField = namedtuple(
        "ExpansionField",
        ["id", "parent", "sub_field_parent", "sub_field", "level", "type", "value"],
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.expanded_fields = []
        self.called_external_uris = {}

    def get_serializer(self, *args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output. The expansion mechanism will be applied for the list operation incase the "expand" query paramter has been set.
        """
        serializer = super().get_serializer(*args, **kwargs)
        if not self.request:
            return serializer
        if self.action in ["list"]:
            serializer = self.inclusions(serializer)
        return serializer

    @staticmethod
    def _convert_to_internal_url(url: str) -> str:
        """Convert external uri (https://testserver/api/v1...) to internal uri (/api/v1...)"""
        keyword = "api"
        save_sentence = False
        internal_url = "/"
        if isinstance(url, dict):
            url = url.get("url")
        if not url:
            return ""
        for word in url.split("/"):
            if word == keyword:
                save_sentence = True
            if save_sentence:
                internal_url += word + "/"

        return internal_url[:-1]

    def _get_external_data(self, url):
        if not self.called_external_uris.get(url, None):
            try:
                access_token = self.request.jwt_auth.encoded
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

    def build_expand_schema(
        self,
        result: dict,
        fields_to_expand: list,
    ):
        """Build the expand schema for the response. First, the fields to expand are split on the "." character. Then, the first part of the split is used to get the urls from the result. The urls are then used to get the corresponding data from the external api or from the local database. The data is then gathered/collected inside a list consisted of namedtuples. When all data is collected, it calls the _build_json method which builds the json response."""
        expansion = {"_expand": {}}
        for exp_field in fields_to_expand:
            loop_id = str(uuid.uuid4())
            self.expanded_fields = []
            for depth, sub_field in enumerate(exp_field.split(".")):
                if depth == 0:
                    try:
                        urls = result[sub_field]
                    except KeyError:
                        raise self.validation_invalid_expand_field(sub_field)

                    if isinstance(urls, list):
                        for x in urls:
                            if x:
                                my_tuple = self.ExpansionField(
                                    loop_id,
                                    result["url"],
                                    None,
                                    sub_field,
                                    depth,
                                    "list",
                                    self.get_data(x),
                                )
                                my_tuple.value["loop_id"] = loop_id
                                my_tuple.value["depth"] = depth

                                self.expanded_fields.append(my_tuple)
                    else:
                        if urls:
                            my_tuple = self.ExpansionField(
                                loop_id,
                                result["url"],
                                None,
                                sub_field,
                                depth,
                                "dict",
                                self.get_data(urls),
                            )
                            my_tuple.value["loop_id"] = loop_id
                            my_tuple.value["depth"] = depth
                            self.expanded_fields.append(my_tuple)
                else:
                    for field in self.expanded_fields:
                        if field.sub_field == exp_field.split(".")[depth - 1]:
                            not_empty = field.value.copy()
                            self.remove_key(not_empty, "loop_id")
                            if not not_empty:
                                continue
                            try:
                                urls = field.value[sub_field]
                            except KeyError:
                                raise self.validation_invalid_expand_field(sub_field)
                            if isinstance(urls, list):
                                for x in urls:
                                    if x:
                                        my_tuple = self.ExpansionField(
                                            loop_id,
                                            field.value["url"],
                                            exp_field.split(".")[depth - 1],
                                            sub_field,
                                            depth,
                                            "list",
                                            self.get_data(x),
                                        )
                                        my_tuple.value["loop_id"] = loop_id
                                        my_tuple.value["depth"] = depth

                                        self.expanded_fields.append(my_tuple)
                            else:
                                if urls:
                                    my_tuple = self.ExpansionField(
                                        loop_id,
                                        field.value["url"],
                                        exp_field.split(".")[depth - 1],
                                        sub_field,
                                        depth,
                                        "dict",
                                        self.get_data(urls),
                                    )
                                    my_tuple.value["loop_id"] = loop_id
                                    my_tuple.value["depth"] = depth
                                    self.expanded_fields.append(my_tuple)

            if not self.expanded_fields:
                continue

            expansion = self._build_json(expansion)

        self.remove_key(expansion, "loop_id")
        self.remove_key(expansion, "depth")

        result["_expand"].update(expansion["_expand"])

    def _build_json(self, expansion: dict) -> dict:
        max_value = max(self.expanded_fields, key=lambda x: x.level).level
        for i in range(max_value + 1):
            specific_levels = [x for x in self.expanded_fields if x.level == i]

            for index, fields_of_level in enumerate(specific_levels):
                if index == 0 and i == 0:
                    if fields_of_level.type == "list":
                        expansion["_expand"][fields_of_level.sub_field] = []
                    else:
                        expansion["_expand"][fields_of_level.sub_field] = {}

                if i == 0:
                    if fields_of_level.type == "list":
                        expansion["_expand"][fields_of_level.sub_field].append(
                            fields_of_level.value
                        )
                    else:
                        expansion["_expand"][
                            fields_of_level.sub_field
                        ] = fields_of_level.value

                else:
                    match = self.get_parent_dict(
                        expansion["_expand"],
                        target_key1="url",
                        target_key2="loop_id",
                        target_value1=fields_of_level.parent,
                        target_value2=fields_of_level.id,
                        level=i,
                        field_level=fields_of_level.level,
                    )

                    for parent_dict in match:
                        if isinstance(parent_dict, str):
                            if parent_dict != fields_of_level.sub_field_parent:
                                continue
                            parent_dict = match[parent_dict]
                        if parent_dict.get("url", None) != fields_of_level.parent:
                            continue
                        if not parent_dict.get("_expand", None) and isinstance(
                            parent_dict[fields_of_level.sub_field], list
                        ):
                            parent_dict["_expand"] = {fields_of_level.sub_field: []}

                        elif not parent_dict.get("_expand", None) and isinstance(
                            parent_dict[fields_of_level.sub_field], str
                        ):
                            parent_dict["_expand"] = {fields_of_level.sub_field: {}}

                        if isinstance(parent_dict[fields_of_level.sub_field], list):
                            if (
                                not fields_of_level.value
                                in parent_dict["_expand"][fields_of_level.sub_field]
                            ):
                                parent_dict["_expand"][
                                    fields_of_level.sub_field
                                ].append(fields_of_level.value)
                        elif isinstance(parent_dict[fields_of_level.sub_field], str):
                            parent_dict["_expand"][
                                fields_of_level.sub_field
                            ] = fields_of_level.value

        return expansion

    def get_parent_dict(
        self,
        data,
        target_key1,
        target_key2,
        target_value1,
        target_value2,
        level,
        field_level,
        parent=None,
    ):
        """Get the parent dictionary of the target value."""

        if isinstance(data, dict):
            if (
                data.get(target_key1) == target_value1
                and data.get(target_key2) == target_value2
                and data.get("depth") == level - 1
            ):
                return parent
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    parent_dict = self.get_parent_dict(
                        value,
                        target_key1,
                        target_key2,
                        target_value1,
                        target_value2,
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
                        target_key2,
                        target_value1,
                        target_value2,
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

    def inclusions(self, serializer):
        expand_filter = self.request.query_params.get("expand", "")
        if expand_filter:
            fields_to_expand = expand_filter.split(",")
            for serialized_data in serializer.data:
                serialized_data["_expand"] = {}
                self.build_expand_schema(
                    serialized_data,
                    fields_to_expand,
                )
        return serializer

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
