# Disagreement-logg: Judge A vs Judge B (kalibrering v0.2, run 1)

7 av 84 claims ga ulik verdict. Ingen avvikendene er safety-kritiske.

| ID | Forventet | Judge A | conf | Judge B | conf | Vurdering |
|---|---|---|---|---|---|---|
| CAL009 | SUPPORTED | INSUFFICIENT | 0,74 | SUPPORTED | 0,95 | B har rett: "ordningen" arver dokumentets tema. A er for streng paa implisitt kontekst. |
| CAL066 | INSUFFICIENT | INSUFFICIENT | 0,95 | PARTIAL | 0,90 | A har rett. B overleser en svak kilde. |
| CAL068 | INSUFFICIENT | INSUFFICIENT | 0,92 | CONTRADICTED | 0,66 | A har rett; B konkluderer kontradiksjon med lav confidence. |
| CAL074 | INSUFFICIENT | INSUFFICIENT | 0,86 | SUPPORTED | 0,70 | A har rett; B accepterer tema-overlap som stotte (klassisk FP-moenster). |
| CAL075 | INSUFFICIENT | INSUFFICIENT | 0,88 | CONTRADICTED | 0,70 | A har rett; B overkonkluderer. |
| CAL077 | INSUFFICIENT | CONTRADICTED | 0,88 | INSUFFICIENT | 0,95 | B har rett; A leser dato-scope som kontradiksjon. |
| CAL078 | SUPPORTED | INSUFFICIENT | 0,84 | SUPPORTED | 0,86 | B har rett; modal "kan fa" er tilstrekkelig dekket av kildens vilkarsbeskrivelse. |

Moenster: B (deepseek) feiler mot "tema-overlap er ikke stotte" i INSUFFICIENT-
tilfellene (CAL074 er naermest en binaer FP-risk i prod); A (gpt-5.5) er mer
konservativ med implisitt dokumentkontekst og modalitet. Fusion "begge ma si
SUPPORTED" eliminerer B sin FP-risk og beholder A sin 0/62.

Totalvurdering: A er mer stabil og sikrere; B tilfoerer verdi som andre-stemme
i fusion, men skal ikke kjore alene (moter ikke pre-registrerte terskler som
primandommer).
