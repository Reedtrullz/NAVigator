# HV2-049 Audit (v0.4.1 pre-tuning, spec section 5)

Date: 2026-08-31. Status: LABEL_CORRECTED.

## 1. Claim

HV2-049: "Familievernkontoret i Trondheim ligger i Carl Johans gate 3."

## 2. Source (KB 70)

KB id 70 resolves to `70-lokalt/trondheim/05-familievern-barnevern.md` (last verified 30.08.2026). Under the section heading "Familievernkontoret i Trondheim (STATLIG via Bufetat)" the source explicitly lists:

- "Adresse: Carl Johans gate 3, 7010 Trondheim."

The claims file embedded only the bare line "Adresse: Carl Johans gate 3, 7010 Trondheim." without the section heading. The live primary source (https://www.bufdir.no/familie/familievernkontorer/oversikt/trondheim/, fetched 2026-08-31) confirms under "Post- og besøksadresse": "Carl Johans gate 3, 7010 Trondheim".

## 3. Original expected (answer key)

HV2-049 expected verdict: SUPPORTED ("Adressen bekreftes.").

## 4. Support evidence

- Section heading of source section: "Familievernkontoret i Trondheim (STATLIG via Bufetat)".
- Bullet directly below the heading: "Adresse: Carl Johans gate 3, 7010 Trondheim."
- Same section repeats phone/e-mail for the same office, tying the address block unambiguously to the office.
- Live Bufdir page confirms the same address under "Post- og besøksadresse".

## 5. Contradiction evidence

None. No source line associates a different address with Familievernkontoret i Trondheim.

## 6. Scope

Same subject (Familievernkontoret i Trondheim), same locality (Trondheim), same time (current address info, source verified 30.08.2026, live check 31.08.2026).

## 7. Sufficiency

Sufficient. The address is explicitly affirmed for the named office in the cited source when section context is considered. The v0.4 verdict INSUFFICIENT_EVIDENCE was caused by the extraction layer treating the bare embedded snippet in isolation (subject_match=false because the heading is outside the snippet), not by any real insufficiency.

## 8. Correct label per final doctrine

SUPPORTED. Status: LABEL_CORRECTED (the expected label SUPPORTED is confirmed; v0.4's INSUFFICIENT was a false negative on this case).

## 9. Consequence for tuning

Audit-only conclusion, saved before any tuning per spec. The repair direction is general, not testcase-specific: extraction must resolve subject context (section headings and document structure) for embedded snippets rather than evaluating a bare line in isolation. No HV2-049-specific rule is permitted (spec section 30 id_guard).
