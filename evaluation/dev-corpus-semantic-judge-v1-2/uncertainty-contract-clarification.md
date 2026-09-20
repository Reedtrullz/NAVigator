# Uncertainty contract clarification V1.2 (den ene tillatte bounded clarification)

Status: FORKUNNSKAP FOER SET B. Ingen ytterligere kontraktsreparasjon er
tillatt etter at Set B-labeling starter (spesifikasjon paragraf 19).

Utgangspunkt: Set A dual blind labeling ga 18/20 = 90% enighet
(gate: >= 95%). To uenigheter:

- UA-NR-03: pass1 [NO/NOT_REQUIRED] vs pass2 [YES/SATISFIED].
  Kriteriet "Kriteriet krever at ingen usikkerhet eksponeres for dette
  faktum" ble lest forskjellig: er et NEGATIVT krav (usikkerhet skal IKKE
  eksponeres) et usikkerhetskrav?
- UA-UN-01: pass1 [YES/PARTIAL] vs pass2 [YES/SATISFIED].
  Kandidat "Det finnes vel noe slikt noen steder." mot compound-krav.
  Begge passene avviste UNRESOLVED; de splittet paa hedging-grad.

## Avklaring 1: Negativt eksponeringskrav er IKKE et usikkerhetskrav

requirement_applicable = YES hvis og bare hvis kriteriet KREVER at
usikkerhet/begrensning EKSPONERES i svaret (noe som maa forbeholdes,
flagges eller begrenses).

Et kriterium som krever at usikkerhet IKKE eksponeres (negativt krav), eller
som stiller ingen usikkerhetskrav i det hele tatt, gir:

    requirement_applicable = NO  ->  verdict NOT_REQUIRED

Kandidatens egen forsiktighet (frivillig hedging) endrer aldri
applicability. Applicability bestemmes av KRITERIET alene, foer kandidaten
ses i verdict-sammenheng.

## Avklaring 2: Meta-utsagn er ikke epistemiske begrensninger

Utsagn om at forbehold ikke er nodvendige ("ingen forbehold nodvendig"),
eller andre meta-kommentarer om svarets egen form, er ikke uttrykk for en
epistemisk begrensning og kan ikke bidra til SATISFIED eller PARTIAL.

## Avklaring 3: SATISFIED krever full, spesifikk match; generell forsiktighet er PARTIAL

Map kandidatens uttrykte begrensning mot kriteriets krevde begrensning:

- Full og spesifikk match (kandidaten uttrykker nettopp det kriteriet
  krever, tydelig nok til aa hindre relevant overclaim): SATISFIED.
- Identifiserbar men ufullstendig eller generisk dekning (f.eks. "jeg er
  ikke sikker" mot et compound-krav, eller generell variasjon mot et
  spesifikt variasjonskrav): PARTIAL.

Vague partikler ("vel", "kanskje", "noen steder") gir aldri alene
SATISFIED; de gir hoyst PARTIAL relativt til et spesifikt kriterium.

## Avklaring 4: UNRESOLVED krever uavgjorlig retning, ikke uvanlig ordlyd

UNRESOLVED er kun tilgjengelig naar teksten ikke tillater trygg bestemmelse
av OM det epistemiske claimet overhode gjores, eller dets RETNING
(overclaim vs. begrensning). Finnes det identifiserbar hedging, er
UNRESOLVED ikke tilgjengelig (bruk PARTIAL/SATISFIED). Uvanlig eller
kortfattet ordlyd er i seg selv aldri UNRESOLVED.

Disse fire punktene er en del av den frosne V1.2-kontrakten og gjelder for
Set B, official fixtures, prompt og judge.
