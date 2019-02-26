"""
Defines the scopes used in the DRC component.
"""

from zds_schema.scopes import Scope


SCOPE_DOCUMENTEN_ALLES_VERWIJDEREN = Scope(
    'scopes.documenten.verwijderen',
    description="""
**Laat toe om**:

* documenten te verwijderen
"""
)
