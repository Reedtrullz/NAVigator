# Label Audit (post-freeze)

Official score: e47890d0f5bd57f1f326e679adc8c9707998d663b46445e202adc969ebaa14b2 (unchanged).

## POTENTIAL_BLIND_LABEL_ERROR candidates

High-confidence auto decisions where engine verdict and reviewer path
agreed internally but disagreed with the sealed label were flagged and
then manually re-read against source evidence:

### RC2B-0058 - REJECTED as label error (engine bug)

* Claim: barns inntekt/formue med i botilsettervurderingen.
* Source: 55-bostotte-i-dybden.md:45 - ... Barns inntekt og formue er ikke med.
* Engine supported via quote alignment and missed the trailing negation.
* Sealed label CONTRADICTED is correct.

### RC2B-0136 - REJECTED as label error (engine bug)

* Claim: ved fristbrudd kan behandlingsstedet selv velge aa ignorere Helfo.
* Source: 24-kildedokumentasjon-bup-og-habu.md:59 - ved fristbrudd skal behandlingsstedet kontakte Helfo...
* Engine supported; missed skal->kan deontic flip plus contrary duty.
* Sealed label CONTRADICTED is correct.

### RC2B-0030 - REGISTERED: POTENTIAL_BLIND_LABEL_ERROR

* Claim: ved delt fast bosted fordeles underholdskostnaden etter inntekt i stedet for samvaersfradrag.
* Source: 49-samvaersfradrag-og-reisekostnader.md:18-25 explicitly states:
  Ved DELT FAST BOSTED er samvaersfradrag som hovedregel IKKE aktuelt;
  da fordeles underholdskostnaden etter inntekt i stedet.
* Prediction AUTO_SUPPORTED (conf 0.9); sealed expected CONTRADICTED /
  AUTO_CONTRADICTED. Source evidence appears to directly support the
  claim text. Official sealed label remains authoritative and unchanged.

## AUDITED_SENSITIVITY

Treating RC2B-0030 as SUPPORTED/AUTO_SUPPORTED (per source evidence) and
keeping everything else unchanged:

* semantic 53/160 (33.12%), proof-safe 40/160 (25.00%),
  product 68/160 (42.50%), auto precision 15/17 (88.24%).
* Verdict under alternate labels: still RC2_NOT_CERTIFIED.
  audited-sensitivity.json

## Construction audit

construction-audit.sealed was NOT decrypted (not needed post-freeze; the
single V3->V4 top-level relabel is described only in aggregate in
blind-manifest.json).
