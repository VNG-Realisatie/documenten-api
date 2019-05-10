"""
Defines the scopes used in the DRC component.
"""

from vng_api_common.scopes import Scope

SCOPE_DOCUMENTEN_ALLES_VERWIJDEREN = Scope(
    'documenten.verwijderen',
    description="""
**Laat toe om**:

* documenten te verwijderen
"""
)

SCOPE_DOCUMENTEN_ALLES_LEZEN = Scope(
    'documenten.lezen',
    description="""
**Laat toe om**:

* documenten te lezen
* documentdetails op te vragen
"""
)

SCOPE_DOCUMENTEN_BIJWERKEN = Scope(
    'documenten.bijwerken',
    description="""
**Laat toe om**:

* attributen van een document te wijzingen
"""
)

SCOPE_DOCUMENTEN_AANMAKEN = Scope(
    'documenten.aanmaken',
    description="""
**Laat toe om**:

* documenten aan te maken
