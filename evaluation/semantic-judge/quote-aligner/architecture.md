# Arkitektur: Quote-Aligner Polarity Engine

## Overordnet pipeline

    claim --> normalisering/canon --> atom-splitting
                                            |
    source --> normalisering/canon ---------+
                                            v
                              decide_atom (per atom)
                              1. kandidat-alignment (quote_aligner)
                              2. harde contra-regler (span-baserte)
                              3. myke signaler (soft_blocks)
                              4. polaritets-sammenligning (affirm/negate,
                                 modality, predicate-opposition)
                              5. numerisk alignment (equal / near-miss / akse)
                              6. support-gate + claim-strength-vetoer
                                            |
                                            v
                     aggregate (atom-verdicts -> sluttverdict)

## Nodale designvalg

1. Span-alignment i stedet for ekstraksjon. Motoren aligner claim-atomer
   mot hele source-teksten. Det finnes ingen LLM-span-finder i denne
   prototypen; hverken engine eller harness inneholder modellkall.
2. Harde contra-regler foran polaritet. Eksplisitte tekstsignaler
   (negasjonsspenn, aldersintervall-opposisjon, unntak mot universal,
   eksklusiv eller-liste, funksjonsdeling) gir CONTRADICTED direkte.
3. Claim-strength-vetoer i SUPPORTED-grenen. SUPPORTED krever at alle
   claim-styrke-signaler (universalkvantorer, superlativer, eksklusivitet,
   aktor-familie, funksjonsfamilie, modality, obligasjon) er dekket av source.
   Udekket styrke gir INSUFFICIENT_EVIDENCE, ikke CONTRA.
4. Aggregering. SUP+CONTRA co-equal = PARTIAL (v0.3 regel 3c);
   compound-claims krever konsensus. Injection rapporteres
   (injection_detected) men overstyrer ikke verdict: en regelbasert motor
   kan ikke omprogrammeres av source-tekst, og hard evidence veier tyngre
   enn et forsok pa manipulasjon.
5. Norsk normalisering. aa->a-breve, ar->ar-breve i alder, canon-synonymer
   (f.eks. helsesykepleier -> skolehelsetjeneste), verb-utvidelse
   (gjeld/gjelder).

## Proof-objekt

Hver claim gir et JSON-objekt med:

- verdict: SUPPORTED / PARTIALLY_SUPPORTED / CONTRADICTED / INSUFFICIENT_EVIDENCE
- confidence: 0.0-1.0
- injection_detected: bool
- review_required: bool
- atom_results: liste av atom-objekter med atom_id, rule, signals, verdict
- atoms: komprimert oversikt (id, verdict, rule)

## Kjente tak (dokumentert, ikke fikset - iterasjoner brukt)

- Bare-alder _age_relation krever delt verb for a fa contra; ellers INSUFF.
- Exhaustive-eller er kun koblet i SUPPORTED-grenen (ACT-02-monster).
- Modifier-antonymer (full/halv, permanent/midlertidig) kan fa false-CONTRA
  pa unicode-tekst.
- Cost-akse: gratis->koster invers mangler guard i enkelte monster.
- Review-terskelen gir hoy review-rate (37,9 % av atomer) - tuningflate.

Full liste: final-report.md pkt 51.
