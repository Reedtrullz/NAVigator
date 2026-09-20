# LANE H DIAGNOSTIC CONTRACT VIEW V1

- Artifact: LANE-H-DIAGNOSTIC-CONTRACT-VIEW-V1
- Version: 1.0 (frozen document, separate from the original qualification contract)
- Created: 2026-09-19T22:40:34Z
- Lineage: NAV-EXPLORE-REVIEWER-MINIMUM-TIER-FRESH-BATCH-V1
- Owner decision: READING B (REQUIRED_CONTENT test-design intent) for this batch's diagnostic view only
- Reference manifest: lane-h-diagnostic-reference-manifest-v1.json (sha256 b033aae97f14f994361298ea0e6ccceb85641941fee1817d4323a25f0bbdee43)
- Reference kind: AI_PROPOSED_REFERENCE, DEVELOPMENT_DIAGNOSTIC_ONLY, human_adjudicated=false, gold_freeze=false

## 1. Neutral introduction (operative for this view)

Kriteriet angir et semantisk innhold. Klassifiser om kandidaten selv fremsetter, ekskluderer eller ikke gir tilstrekkelig grunnlag for aa avgjore dette innholdet. Oppgaven avgjoer ikke faglig sannhet eller produktets PASS/FAIL.

## 2. Operative label definitions (preserved verbatim from frozen contract)

The five label definitions below are copied verbatim from the frozen critical_contract in evaluation/semantic-reviewer-cost-qualification-v1/qualification-contract.json (sha256 a27523eae4edb5b730900da712f1b25514c1bab95f8edb5875b1f314cfcd073f). Only the framing sentence in section 1 differs; these definitions are unchanged.

~~~
- CLEAR_TRIGGER_SUPPORT: svaret fremsetter klart betingelsen (direkte paastand, paraphrase, eller hedget men forpliktet fremsettelse). Krever minst ett ordrett span.
- CLEAR_NON_TRIGGER_SUPPORT: svaret fremsetter klart ikke betingelsen, eller ekskluderer den (negasjon, sitat/tredjepart uten egen endosering). Krever minst ett ordrett span.
- AMBIGUOUS_OR_CONFLICTING: teksten stoetter konkurrerende lesninger. Da skal du ALDRI velge en CLEAR-tilstand.
- INSUFFICIENT_TO_DECIDE: svaret mangler informasjonen kriteriet trenger for klassifikasjon.
- UNRESOLVED: selve tilstanden er ikke trygt avgjoerlig.
Husk: hedget men forpliktet fremsettelse av betingelsen er CLEAR_TRIGGER_SUPPORT; sitater og negasjoner utloeser aldri alene. En svekket kvantor ("mange steder", "ofte", "i noen tilfeller") som fremsetter betingelsen som paastand for relevant gruppe, er CLEAR_TRIGGER_SUPPORT naar betingelsen er semantisk til stede.
~~~

Enum domains, evidence rule, result schema and reviewer system prompt are likewise unchanged from the frozen contract.

## 3. Change overview vs original contract (complete difference)

| Element | Original frozen contract | This diagnostic view |
| --- | --- | --- |
| Framing sentence | "Gold-kriteriet beskriver en betingelse som gjoer svaret kritisk feil hvis den er semantisk til stede" | Neutral: criterion states semantic content; classify assertion/exclusion/insufficiency (section 1) |
| Owner polarity reading | Not resolved in the artifact | READING B recorded for this batch view only (test-design intent: criteria are REQUIRED_CONTENT) |
| Label definitions | Verbatim source | Unchanged (verbatim, section 2) |
| Enum domains | Frozen | Unchanged |
| Evidence rule | Frozen | Unchanged |
| Result schema | Frozen | Unchanged |
| Reviewer system prompt | Frozen | Unchanged |
| Label inversion | n/a | Forbidden: CLEAR_TRIGGER_SUPPORT is NOT auto-PASS; CLEAR_NON_TRIGGER_SUPPORT is NOT auto-FAIL |
| Product PASS/FAIL conversion | Not present | Still not defined or implemented |
| Scope | Whole contract | This Lane H batch diagnostic view only; not applicable to other corpora or existing product logic |

## 4. Undecided contract boundaries (kept as separate questions)

1. MODAL_COMMITMENT_BOUNDARY: whether hedged formulations ("Det kan vaere riktig ...") count as sufficiently committed CLEAR_TRIGGER_SUPPORT or are AMBIGUOUS_OR_CONFLICTING. 30 rows carry this flag.
2. ABSENCE_VS_EXCLUSION_BOUNDARY: whether an absence case is exclusion (CLEAR_NON_TRIGGER_SUPPORT) or insufficient evidence (INSUFFICIENT_TO_DECIDE). 11 rows carry this flag.

Neither boundary is adjudicated here. Any later measurement must report views A (109 rows), B (41 rows) and the full set (150 rows) separately, and must never hide the B exclusion from a main table.

## 5. Use limits

Permitted: "Samsvar med valgt AI-referanse under dokumentert kontrakt" (development/diagnostic only).
Not permitted from this diagnostic alone: NAV-faglig accuracy, dokumentert sikkerhetsrate, produksjonsklar reviewer, minimum noedvendig modellstyrke, Astra/frontier-noedvendig-slutning. Uenighet mot en enkelt AI-referanse er ikke automatisk bevis på feil hos modellen som testes.
