"""
Defines the scopes used in the DRC component.
"""

from vng_api_common.scopes import Scope


SCOPE_DOCUMENTEN_ALLES_VERWIJDEREN = Scope(
    'scopes.documenten.verwijderen',
    description="""
**Laat toe om**:

* documenten te verwijderen
"""
)
