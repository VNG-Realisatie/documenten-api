from vng_api_common.permissions import (
    MainObjAuthScopesRequired, RelatedObjAuthScopesRequired
)

from .scopes import SCOPE_DOCUMENTEN_ALLES_LEZEN


class InformationObjectAuthScopesRequired(MainObjAuthScopesRequired):
    """
    Look at the scopes required for the current action and at informatieobjecttype and vertrouwelijkheidaanduiding
    of current informatieobject and check that they are present in the AC for this client
    """
    permission_fields = ('informatieobjecttype', 'vertrouwelijkheidaanduiding')


class InformationObjectRelatedAuthScopesRequired(RelatedObjAuthScopesRequired):
    """
    Look at the scopes required for the current action and at informatieobjecttype and vertrouwelijkheidaanduiding
    of related informatieobject and check that they are present in the AC for this client
    """
    permission_fields = ('informatieobjecttype', 'vertrouwelijkheidaanduiding')
    obj_path = 'informatieobject'

    # Define the property of the ForeignKey of which the permission fields will
    # be checked
    obj_property = 'latest_version'

    def _get_obj_from_path(self, obj):
        if not isinstance(self.obj_path, str):
            raise TypeError("'obj_path' must be a python dotted path to the main object FK")

        bits = self.obj_path.split('.')
        for bit in bits:
            obj = getattr(obj, bit)

        if self.obj_property:
            obj = getattr(obj, self.obj_property)
        return obj
