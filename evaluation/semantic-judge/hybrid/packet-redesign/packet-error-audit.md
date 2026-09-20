# Packet error audit - Iteration B (45 review-layer errors)

Source: results/hybrid-eval.json (Iteration B, frozen), rebuilt packets via
build_audit.py -> audit-data.json. Label normalization applied
(INSUFFICIENT_EVIDENCE -> INSUFFICIENT, PARTIALLY_SUPPORTED -> PARTIAL).
All error cases are review-path cases; auto-path precision was 100%.

## Error distribution

| Expected | Actual | n |
|---|---|---|
| SUPPORTED | INSUFFICIENT | 17 |
| INSUFFICIENT | CONTRADICTED | 9 |
| PARTIAL | CONTRADICTED | 5 |
| CONTRADICTED | INSUFFICIENT | 11 |
| CONTRADICTED | PARTIAL | 2 |
| PARTIAL | INSUFFICIENT | 1 |

## Taxonomy

### T1 - S0 distraction (14 cases)

Every INSUFFICIENT->CONTRADICTED (9) and PARTIAL->CONTRADICTED (5) case cited
S0 (the full-source dump span) as its contradiction evidence. 14/14 used S0;
13/14 used no other span. Confidence was high (0.82-0.99): the reviewer
treated "the whole source is in the packet" as license to answer from source
gist instead of a specific contradiction span. This is a packet-design error,
not reviewer reasoning: v1.1 rule 2a forbids exactly this verdict, but the
packet made the violation tempting.

Cases: CI-040, CI-041, CI-046, CI-059, CI-061, CI-065, LOC-10, LOC-20, N-R3,
CAL048, CAL050, HOL007, HOL020, HOL040.

### T2 - Binding failure (12 cases, SUPPORTED->INSUFFICIENT)

The entailing span was IN the v1 packet (best single-span token coverage
>= 0.6 against the relevant atom) but the reviewer used no spans
(used_union_coverage 0.0 in all 12) and answered INSUFFICIENT. With a flat
8-span packet there is no per-atom grouping to tell the reviewer which spans
belong to which claim atom, so multi-atom or distractor-rich claims left the
decisive span unbound.

Cases: MP-007A, MP-009A, MP-014A, MOD-13, ACT-10, ACT-23, ACT-25, N-S9,
N-L4, N-C4, N-C5, ENT-A.

ENT-A detail: atom 2 ("foreldresamtale og lavterskel stotte foerst") had best
single-span coverage 0.25; the evidence is distributed across spans that
jointly cover the atom, but v1 packets expressed no joint_support relation.
This is the distributed-entailment gap, not a label problem.

### T3 - Retrieval ceiling (6 cases)

Best candidate span coverage < 0.6: the aligner (existing candidates(), top-8
in v1) never surfaced a span covering the decisive atom, so no packet layout
within the current retrieval surface can bind it. Cases: MP-016A (0.40),
MP-015A (0.57), ACT-19 (0.33), D20-L5 (0.50), N-S4 (0.50), HOL005
(PARTIAL->INSUFFICIENT, 0.50). These are unchanged by packet redesign; wider
top_n (6 per atom in v2.1) may recover some, otherwise they stay review
failures and belong to the retrieval-ceiling budget.

### T4 - Contradiction-evidence boundary (13 cases)

Expected CONTRADICTED, reviewer answered INSUFFICIENT (11) or PARTIAL (2)
without citing contradiction spans. Reading the packets:

* Explicit contradiction present in packet, reviewer still answered
  INSUFFICIENT: N-A3 ("yter ikke psykisk helsebehandling" vs "gir
  behandling"), HOL034 (15 ar vs claim "fra fylte 12 ar"), HOL037 (under 16
  ar vs claim "under 18 ar"). Three reviewer-boundary failures; per-atom
  grouping should help by isolating the numeric/actor atom.
* Only implicit contradiction available (actor list, eligibility condition,
  different addressee): CAL029, CAL030, CAL064, HOL022, MP-013B, N-O5,
  CAL086 (injection probe; INSUFFICIENT is the locked safe behavior).
  v1.1 doctrine demands a span that "slar fast det motsatte"; these packets
  do not contain one, so INSUFFICIENT is the doctrine-faithful answer.
  Packet redesign cannot and should not fix these.
* HOL026, HOL030: PARTIAL instead of CONTRADICTED where the false atom is
  explicit ("krever henvisning" vs drop-in; "samtykkekompetanse folger
  foreldreansvaret"). Boundary calibration, packet content was adequate.

## Implications for packet-v2.1

1. no_s0 default removes the T1 trigger (14/45 = 31% of errors).
2. Per-atom evidence groups with joint_support sets attack T2
   (12/45 = 27%), including ENT-A's distributed-entailment case.
3. Wider per-atom top_n (6) gives T3 a bounded second chance without new
   retrieval; T4 is reviewer/doctrine territory and is out of scope here.

Expected recoverable share if T1 + T2 + part of T3 convert: roughly 26-32 of
45 errors. The remainder (most of T4) is the honest ceiling of a packet-only
redesign under frozen v1.1 doctrine.
