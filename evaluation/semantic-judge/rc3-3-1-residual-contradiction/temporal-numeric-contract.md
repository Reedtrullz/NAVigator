# TEMPORAL_NUMERIC_APPLICABILITY_V1 (frozen runtime semantics, pre-implementation)

Scope: numeric.py + a single guard wrapper in engine.py. No boundary,
reviewer, routing, threshold, evidence-ledger, or relation-architecture
changes.

## D1 Quantity identity (unchanged)

RC3.3 quantity identity, comparator intervals, coverage semantics,
aggregate/component role checks, and law-reference exclusions are carried
over byte-for-byte in behavior. Role/qualifier/binding mismatches (delt vs
full sats, aggregate vs component) remain quantity-identity failures and
stay positive conflicts.

## D2 Temporal status classification

Each side is classified per clause containing the deciding quantity:

- HISTORICAL: clause carries history/supersession signals
  (gjaldt, tidligere/tidlegare, forrige, erstattet, opphort, sist endret,
  gammel/gamal sats, historisk, var/ble + amount, or an explicit year
  reference "i/fra/per YEAR" with YEAR < CURRENT_YEAR=2026).
- CURRENT: currency signals (na/naa, naavaerende, gjeldende, i dag,
  dette aret, fra/per CURRENT_YEAR) or no temporal signal at all
  (KB default is current-state documentation).
- CURRENT_YEAR=2026 is a frozen calibration constant (source: KB
  verification date 30.08.2026), not a tunable threshold.

## D3 Applicability mismatch (fail closed)

Temporal applicability mismatch exists when claim status and the deciding
evidence quantity's status differ (one HISTORICAL, one CURRENT), or when
the claim's amount is DERIVED from a base quantity that conflicts with the
evidence's matching base quantity (stale base; derived value unverified).

Effect: hard numeric amount-contradiction rules (R01/R08/R09/R19/R23/R24/
R25 numeric and amount-table conflicts) do not fire; the relation fails
closed to RELATED_BUT_INSUFFICIENT. Numeric ENTAILS via shared number,
numeric entailment backup, or coverage also fails closed to RBI (a
historical amount never entails a current-framed claim without temporal
binding, and vice versa).

## D4 Exemptions (frozen)

- DATE-provenance claims (law/registry effective dates about a document
  itself) are exempt: their gold resolution is date identity, and both
  burned RC3.3 date cases resolve there.
- Arithmetic identity conflicts ("a + b = c" vs evidence arithmetic) are
  exempt from the stale guard: an arithmetic conflict is a positive
  logical conflict independent of temporal status.
- Quantity-identity failures (role/qualifier/binding mismatch) remain
  positive conflicts (not applicability questions).

## D5 Frozen reading of spec 16 (UNKNOWN status)

Direct value-vs-value conflicts of the SAME identified quantity with NO
temporal signal on either side retain the RC3.3 positive-conflict doctrine
(different numbers of the same current quantity conflict). The burned
140-case regression is a binding gate in this task (raw counts, CONTRADICTS
precision >=99%), and spec 13 preserves positive conflicts. The spec-16
fail-closed obligation is implemented by D3: any RESOLVED status conflict
(historical vs current, superseded vs current) or unverified derived base
blocks auto-contradiction and auto-entailment.

## D6 Supersession representation

Evidence clauses may carry old and new values. The quantity sitting in a
superseded/history clause is HISTORICAL and can never alone support a
CURRENT-framed claim (D3); a current clause value resolves normally. No
nearest-number heuristic is introduced.
