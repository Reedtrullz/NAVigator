# RC-08 Root Cause: Track-Scoped Retrieval

## Defects (pre-change evidence)

- **A. Unscoped scoring**: `phase2/knowledge.py::retrieve()` scores all 61
  index docs for every track query; track/domain plays no role in selection.
- **B. Hardcoded domain**: `_doc_record()` emits `"domain": "general"` for
  every doc regardless of content.
- **C. Domain overwrite**: `phase2/pipeline.py` s4 assigns
  `rec["domain"] = track["domain"]` after the fact, so downstream code reads a
  claim the retrieval engine never used.
- **D. Unfiltered planner INFO blocks**: `phase3/planner.py` emits an INFO
  block per retrieved record; records retrieved by cross-domain lexical hits
  leak irrelevant content into answers.
- **F. No domain metadata**: `data/knowledge-index-v1.json` entries carried only
  id/path/sha256/class/freshness; no domains field existed.
- **G. Domain-blind gap reserve**: the gap-slot mechanism reserves slots without
  regard to track domain.

## Index metadata repair (mechanism F)

One-shot script `rc08-add-doc-domains.py` added a `domains` array to each of
the 61 doc entries in the knowledge index, derived from the frozen decompose
vocabulary (mental_health, housing, financial_support, child_safety,
education, employment, legal_rights; `general` fallback). Doc files and their
sha256 pins are untouched.

Index SHA before: b83a0808ee8b2d91b0e254ad9bbe6457770bcb8f494ea7083219464deb7b6aa1
Index SHA after:  c8de229b663e14f67b83e582a6a3b57dcef9bb6546de9edede60d2afa38bb31b

## Source repair (mechanisms A/C/D/G)

- `retrieve()` filters candidate docs by track domain before scoring.
- `_doc_record()` emits the doc's own `domains` list instead of a hardcoded
  value; the per-record `domain` field remains the primary tag for compat.
- s4 no longer overwrites `domain` on records.
- Planner INFO blocks are scoped to records whose domains intersect the track
  domain (or primary-domain compat).
- Gap-slot reserve is scoped by track domain.

## Generalization guard

No case IDs, corpus strings, or expected verdicts are referenced in runtime
logic; scoping is driven solely by the frozen decompose domain vocabulary.
