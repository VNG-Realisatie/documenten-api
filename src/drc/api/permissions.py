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


def allow_scopes(private_file) -> bool:
    """
    Check request to have a correct scope to retrieve media files
    """
    if private_file.request.jwt_auth.has_auth(scopes=SCOPE_DOCUMENTEN_ALLES_LEZEN):
        return True

    return False
