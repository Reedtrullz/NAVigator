# NAVigator – kontrollert kontaktpilot

Denne kilden er en ny, begrenset utviklingskandidat for bolig/økonomi. Status er **UTKAST**, distribusjon **BLOCKED**, og den eksperimentelle runtime er frakoblet. Dette er kontakt-/forberedelsesinformasjon, ikke vurdering av rettigheter eller klinisk trygghet.

Fra checkout-roten:

```sh
npm ci --ignore-scripts --no-audit --no-fund --prefix pilot
python3 -S pilot/build/build_pilot.py --generated-at 2026-10-08T12:00:00Z --output-dir outputs/navigator-contact-review-2026-10-08
npm test --prefix pilot
python3 -S pilot/tests/sources_test.py
node pilot/build/test_pilot.js outputs/navigator-contact-review-2026-10-08/NAVigator-pilot.html
python3 -m unittest tests.test_reference_release
```

Åpne den genererte HTML-filen lokalt, eller bruk `python3 -S tools/serve_pilot_review.py outputs/navigator-contact-review-2026-10-08/NAVigator-pilot.html` for en midlertidig server. Den serverer bare HTML-filen på loopback; ingen korpusfiler eksponeres. Stopp med Ctrl-C. Ingen automatisk ekstern dataflyt, lagring, analyse eller telemetri finnes i veiviseren.

Generatoren krever eksplisitt tidspunkt, positiv filallowlist, lokale versjonspinnede utviklingsavhengigheter, gyldig nytt innholdsschema og byteidentisk kopiert policy. Den skriver bare under denne checkoutens `outputs/`. Endre `src/` og bygg på nytt; endre aldri den genererte HTML-filen direkte.

Gamle daterte pilotpakker, registre og målinger er bevart. Generatoren bruker dem ikke som fallback. Ny kildeidentitet finnes i [candidate.json](../releases/next/candidate.json). Tillatelse til å kopiere generisk kode er ikke faglig godkjenning av handlingene.

Plantilstand har én status. Uten situasjonstekst blir bekreftede behov `CONTACT_ONLY`. Maskinens begrensede tekstsjekk kan overse fare. Et oppdaget faresignal sperrer ordinære forslag i den samme åpne siden, også etter tømt tekst, nullstilling og import. Tidligere fremdriftsgrunnlag bevares i arbeidsfilen; ved 20 eldre basisrader per handling avvises ny historikk uten å fjerne tidligere rader. Ingen automatisk diskpersistens innebærer at tilstanden ikke følger en ny nettleserøkt; produktet hevder derfor aldri klinisk trygghet.

Møtenotat og privat arbeidsfil er forskjellige formater. Notatet bruker ett felles innholdsvalg i tekst/kopi/utskrift. Et kontaktforslag som bygger på en utelatt opplysning krever eget, forklart valg. Arbeidsfilen inneholder alle svar og fremdrift, også det som ble utelatt fra notatet; den er ukryptert. Rå situasjonstekst tas ikke med i noen av filene. v1/v2-import gir ingen gjeldende plan eller arvede bekreftelser. Eldre kombinert ukjent-svar får bevart uklar betydning. Det gamle v1-betalingssvaret lagres som migrasjonshistorikk, og det nye spørsmålet må besvares separat.

Se [gjennomføringsloggen](../docs/implementation-2026-10-08.md), [kontrollgrensene](../releases/next/REVIEW.md) og [tilgjengelighetslisten](tests/accessibility-checklist.md). Kvalifisert faglig/personvernkontroll, menneskelige brukerprøver, VoiceOver og faktisk 200/400 % zoom må fortsatt utføres.
