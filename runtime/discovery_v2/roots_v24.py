"""V2.4 canonical municipality-root rule (root-resolution repair).

New lineage module: the historical runtime/discovery_v2/roots.py is frozen
and untouched. The V2.3 docstring, the frozen provider-config-v2-3.json and
the burned/gold corpus all specify the national program platform as
<slug>.bedreinnsats.no; the historical module constructed
<slug>.bedinnsats.no instead. V2.4 corrects that single construction and
keeps every other pattern identical.

Pattern rule, not a municipality lookup: no municipality names, no case IDs,
no service-page or gold-URL knowledge enters this module.
"""

from runtime.discovery_v2.roots import canonical_roots as _v23_roots


def canonical_roots_v24(municipality):
    roots = _v23_roots(municipality)
    # Historical V2.3 appended https://<slug>.bedinnsats.no/ (missing 're').
    # Replace exactly that construction with the canonical platform suffix.
    return [r.replace("://www.", "://").replace(
        ".bedinnsats.no/", ".bedreinnsats.no/") if "kommune.no" not in r
        and r.endswith(".bedinnsats.no/")
        else r for r in roots]
