#!/usr/bin/env python3
"""Build replay fixtures from frozen research artifacts.

Each fixture page is a synthetic captured HTML page containing the verbatim
quotes already registered in the frozen predictions/audit/access artifacts.
These fixtures are DATA for replay, not runtime logic. The runtime never
sees municipality names or expected verdicts.

Usage: python3 build_fixtures.py  (run from repository root or this dir)
Writes: fixture-manifest.json
"""

import hashlib
import json
import os

RETRIEVED = "2026-09-09"


def page(title, body):
    return (
        "<!DOCTYPE html><html lang=\"nb\"><head><meta charset=\"utf-8\">"
        "<title>%s</title></head><body><main>%s</main></body></html>" % (title, body)
    )


def p(text):
    return "<p>%s</p>" % text


# ---------------------------------------------------------------------------
# Generalization V1 scenario fixtures (22 cells: 11 municipalities x C/D)
# ---------------------------------------------------------------------------

GEN_PAGES = {
    # --- Raelingen: SPA shell + fallback source; no access markers retrievable ---
    "https://www.ralingen.kommune.no/artikkel/lavterskel-psykisk-helsehjelp": page(
        "Lavterskel psykisk helsehjelp",
        '<div id="app"></div><script>render()</script>'
        + p("Et tilbud til deg som sliter med psykiske helseutfordringer som "
            "nedstemthet, sorg, bekymringer, stress eller s\u00f8vnproblemer."),
    ),
    "https://oldralingen.bedreinnsats.no/": page(
        "Raelingen kommune",
        p("Avdeling psykisk helse og avhengighet i kommunen tilbyr hjelp og "
          "bistand til voksne innbyggere med psykiske helseplager og/eller "
          "avhengighetsproblematikk samsamt deres p\u00e5r\u00f8rende."),
    ),
    "https://api.skjema.no/ralingen/templates/pdf/123461/nb": page(
        "Selvhenvisningsskjema helse/omsorg",
        p("Tjenester som saksbehandles ved tjenestekontoret for helse og omsorg: "
          "psykisk helsetjeneste, ambulerende psykisk helsetjeneste, rustjeneste."),
    ),

    # --- Drammen: direct digital + explicit age ---
    "https://www.drammen.kommune.no/tjenester/helse-velferd/helsefremmende-tjenester/rask-psykisk-helsehjelp/": page(
        "Rask psykisk helsehjelp Drammen",
        p("Rask psykisk helsehjelp er et gratis behandlingstilbud for personer "
          "over 16 \u00e5r som opplever vanlige angst- og depresjonsplager eller "
          "utfordringer rundt stress, rus og s\u00f8vn. Behandlingen er kortvarig "
          "og du kan selv ta kontakt.")
        + p("P\u00e5melding skjer digitalt via v\u00e5rt p\u00e5meldingsskjema."),
    ),
    "https://www.drammen.kommune.no/tjenester/helse-velferd/helsefremmende-tjenester/drammen/helsestasjon-for-ungdom-drammen/": page(
        "Helsestasjon for ungdom Drammen",
        p("Helsestasjon for ungdom er et gratis tilbud til ungdom fra 13 \u00e5r "
          "og fram til du fyller 25 \u00e5r. Helsesykepleier er alltid tilstede "
          "og det er ingen timebestilling."),
    ),

    # --- Fredrikstad: direct phone (kartleggingssamtale) ---
    "https://www.fredrikstad.kommune.no/tjenester/helse/psykisk-helse-og-rus/rask-psykisk-helsehjelp/": page(
        "Rask psykisk helsehjelp Fredrikstad",
        p("Rask psykisk helsehjelp er et korttids behandlingstilbud for "
          "innbyggere i Fredrikstad kommune over 16 \u00e5r med milde til "
          "moderate former for angst, depresjon, s\u00f8vnvansker og/eller "
          "begynnende rusproblematikk. Rask psykisk helsehjelp er gratis, og "
          "du trenger ingen henvisning fra lege.")
        + p("Vi starter med en kartleggingssamtale over telefon, og blir enige "
            "om veien videre sammen med deg. Ta kontakt for timebestilling."),
    ),
    "https://www.fredrikstad.kommune.no/tjenester/barne-og-familietjenester/helsestasjoner/helsestasjon-for-ungdom/": page(
        "Helsestasjon for ungdom Fredrikstad",
        p("Helsestasjon for ungdom"),
    ),

    # --- Askoy: C direct contact (barn/unge) + D age-gap ---
    "https://askoy.kommune.no/tjenester/helse-og-mestring/tjenestetilbud-fysisk-og-psykisk-helse/psykisk-helse/hvordan-ta-kontakt-med-origo": page(
        "Hvordan ta kontakt med Origo - Askoy kommune",
        p("Ofte er det nyttig \u00e5 ta kontakt med oss i samarbeid med noen du "
          "allerede er i kontakt med, for eksempel helsesykepleier eller "
          "fastlege. Men du er ogs\u00e5 velkommen til \u00e5 ta kontakt med oss "
          "p\u00e5 egen h\u00e5nd.")
        + p("Du kan ringe oss p\u00e5 telefon 56 15 86 99. Telefontid "
            "mandag-fredag: klokken 09.00-14.00.")
        + p("For voksne over 24 \u00e5r \u00f8nsker vi fortrinnsvis henvisning fra "
            "fastlege eller spesialisthelsetjeneste for oppf\u00f8lging i Origo."),
    ),
    "https://askoy.kommune.no/tjenester/barn-unge-og-familie/helsestasjoner-og-skolehelsetjenesten/helsestasjon-for-ungdom-hfu": page(
        "Helsestasjon for ungdom HFU - Askoy",
        p("Helsestasjon for ungdom HFU"),
    ),

    # --- Bamble: explicit 0-100, self contact, phone + drop-in ---
    "https://www.bamble.kommune.no/helse-og-mestring/psykisk-helse-og-rusomsorg/bamblehjelpa/": page(
        "Bamblehjelpa - Bamble kommune",
        p("Bamblehjelpa er en lavterskel helsetjeneste der du selv kan ta "
          "kontakt dersom du \u00f8nsker endring i din livssituasjon. Vi er en "
          "tjeneste fra 0-100 \u00e5r, der vi jobber i et nettverksperspektiv.")
        + p("Du kan kontakte oss p\u00e5 telefon 48 16 50 77 i telefontiden, "
            "eller komme p\u00e5 drop-in for voksne."),
    ),
    "https://www.bamble.kommune.no/helse-og-mestring/psykisk-helse-og-rusomsorg/bamblehjelpa/kontaktinformasjon/": page(
        "Kontaktinformasjon Bamblehjelpa",
        p("Bamblehjelpa Mobil 48 16 50 77 (+4748165077) Adresse: Reidunsvei 37, "
          "3961 Stathelle Telefontid: Hverdager kl. 10-14"),
    ),
    "https://www.bamble.kommune.no/barn-unge-og-familie/helsetjenester-for-barn-unge-og-familier/helsestasjon-for-ungdom/": page(
        "Helsestasjon for ungdom - Bamble",
        p("Helsestasjon for ungdom"),
    ),

    # --- Birkenes: explicit 18+, application form ---
    "https://www.birkenes.kommune.no/innhold/helse-og-velferd/psykisk-helse-for-voksne/": page(
        "Psykisk helse for voksne - Birkenes",
        p("Du m\u00e5 v\u00e6re over 18 \u00e5r og bo i Birkenes kommune.")
        + p("Henvisning fra fastlege eller andre instanser. Fyll ut v\u00e5rt "
            "digitale selvhenvisningsskjema som du finner her. Ta kontakt ved "
            "\u00e5 ringe oss p\u00e5 tlf.: 95 00 36 52 (hverdager 09-15)"),
    ),
    "https://www.birkenes.kommune.no/innhold/barnehage-og-skole/ressurssenter/helsestasjon/": page(
        "Helsestasjon - Birkenes",
        p("Helsestasjon"),
    ),

    # --- Bjerkreim: contact invitation, no explicit age bound ---
    "https://www.bjerkreim.kommune.no/tjenester/helse-og-omsorg/avdeling-mestring/stotte-nar-livet-er-krevende/": page(
        "Avdeling Mestring - st\u00f8tte n\u00e5r livet er krevende",
        p("Avdeling Mestring tilbyr tjenester til innbyggere i Bjerkreim "
          "kommune som opplever psykiske helseutfordringer og/eller "
          "rusrelaterte utfordringer.")
        + p("Du kan ta kontakt dersom du for eksempel opplever: nedstemthet, "
            "angst, sorg. Listen er ikke utt\u00f8mmende, ta gjerne kontakt "
            "ogs\u00e5 dersom du er usikker p\u00e5 om tilbudet passer for deg.")
        + p("Kontaktinformasjon: Telefon: 404 44 911. \u00c5pningstid: Hverdager "
            "kl. 08.00-15.00. Anita Driftland, Avdelingsleder mestringsavdeling."),
    ),

    # --- Alstahaug: explicit 18+ primary, direct contact or fastlege ---
    "https://www.alstahaug.kommune.no/tjenester/helse-og-velferd/psykisk-helse--og-rustjeneste/psykisk-helsetjeneste": page(
        "Psykisk helsetjeneste for voksne - Alstahaug",
        p("Mennesker som bor og midlertidig oppholder seg i kommunen, "
          "prim\u00e6rt over fylte 18 \u00e5r. Du kan ta kontakt direkte eller via "
          "fastlege.")
        + p("Kontakt: Avdelingsleder 468 49 969 / 750 75 215."),
    ),
    "https://www.alstahaug.kommune.no/tjenester/helse-og-velferd/tjenester-til-barn-og-unge/helsestasjon/helsestasjon-for-ungdom": page(
        "Helsestasjon for ungdom - Alstahaug",
        p("Helsestasjon for ungdom er et gratis tilbud til ungdom mellom 12 "
          "og 20 \u00e5r som bor i Alstahaug kommune, eller g\u00e5r p\u00e5 "
          "Sandnessj\u00f8en videreg\u00e5ende skole."),
    ),

    # --- Etnedal: all ages, direct phone/SMS ---
    "https://www.etnedal.kommune.no/tjenester/familie-helse-og-omsorg/psykisk-helsearbeid/": page(
        "Psykisk helsetjeneste Etnedal",
        p("Alle kan ta kontakt \u00e5 f\u00e5 hjelp hos oss. Du trenger ikke "
          "henvisning fra lege eller andre instanser. Tjenesten er gratis, "
          "tilbudet gis til alle - barn, ungdom, voksne og til alle "
          "p\u00e5r\u00f8rende. Du kan ta kontakt ved \u00e5 ringe eller sende SMS."),
    ),
    "https://www.etnedal.kommune.no/tjenester/familie-helse-og-omsorg/kommunepsykolog/": page(
        "Kommunepsykolog - Etnedal",
        p("Kommunepsykolog"),
    ),

    # --- Aure: all ages, direct contact or referral ---
    "https://www.aure.kommune.no/tjenester/helse-og-omsorg/psykisk-helse-og-rus/psykisk-helsehjelp/": page(
        "Psykisk helsehjelp - Aure",
        p("Du kan ta kontakt selv eller du kan henvises av lege eller andre "
          "instanser. Du vil raskt f\u00e5 tilbud om hjelp i form av en "
          "vurderingssamtale/ f\u00f8rstegangssamtale.")
        + p("Psykisk helse og rus er en del av det kommunale tjenestetilbudet "
            "til barn, unge og voksne. Fagleder: 90 52 27 36."),
    ),
    "https://www.aure.kommune.no/tjenester/helse-og-omsorg/psykisk-helse-og-rus/kommunepsykolog/": page(
        "Kommunepsykolog - Aure",
        p("Lavterskel behandlings-og oppf\u00f8lgingstilbud. Ta kontakt med "
          "Psykisk helse om du har behov for psykisk helsehjelp"),
    ),
    "https://www.aure.kommune.no/tjenester/helse-og-omsorg/familie-barn-og-ungdom/helsestasjon-for-ungdom/": page(
        "Helsestasjon for ungdom - Aure",
        p("Helsestasjon for ungdom (HFU) er et gratis tilbud for deg mellom "
          "13-25 \u00e5r. \u00c5pent onsdager i oddetalls-uker fra 14:30-15.15. "
          "Du m\u00f8ter b\u00e5de helsesykepleier og lege p\u00e5 HFU."),
    ),

    # --- Balsfjord: explicit 0-25, named-staff contact (E2) ---
    "https://www.balsfjord.kommune.no/psykisk-helsetjeneste": page(
        "Psykisk helsetjeneste og rusfaglig helsearbeid - Balsfjord",
        p("Tilbud til barn, unge og voksne. Kontakt: Avdelingsleder rus og "
          "psykisk helse 404 48 737."),
    ),
    "https://www.balsfjord.kommune.no/barne-ungdoms-og-familieteamet": page(
        "Barne-, ungdoms- og familieteamet (0-25) - Balsfjord",
        p("Barne-, ungdoms- og familieteamet tilbyr rask psykisk helsehjelp "
          "til barn og ungdom 0-25 \u00e5r. Foresatte og ungdom kan selv ta "
          "kontakt via telefon 404 48 737 / 453 55 161, eller via "
          "henvisningsskjema sendt i posten."),
    ),
    "https://www.balsfjord.kommune.no/helsestasjon-for-ungdom": page(
        "Helsestasjon for ungdom - Balsfjord",
        p("Helsestasjon for ungdom er et gratis tilbud for ungdom 13-20 \u00e5r. "
          "Drop-in onsdag partallsuker 16-18, uten timebestilling."),
    ),
}

GEN_SEARCH_INDEX = {
    "Raelingen psykisk helse voksne": [
        {"url": "https://www.ralingen.kommune.no/artikkel/lavterskel-psykisk-helsehjelp", "title": "Lavterskel psykisk helsehjelp"},
        {"url": "https://oldralingen.bedreinnsats.no/", "title": "Raelingen kommune"},
    ],
    "Raelingen psykisk helse kontakt": [
        {"url": "https://api.skjema.no/ralingen/templates/pdf/123461/nb", "title": "Selvhenvisningsskjema"},
    ],
    "Drammen psykisk helse voksne": [
        {"url": "https://www.drammen.kommune.no/tjenester/helse-velferd/helsefremmende-tjenester/rask-psykisk-helsehjelp/", "title": "Rask psykisk helsehjelp"},
    ],
    "Drammen psykisk helse rus": [
        {"url": "https://www.drammen.kommune.no/tjenester/helse-velferd/helsefremmende-tjenester/drammen/helsestasjon-for-ungdom-drammen/", "title": "Helsestasjon for ungdom"},
    ],
    "Fredrikstad psykisk helse voksne": [
        {"url": "https://www.fredrikstad.kommune.no/tjenester/helse/psykisk-helse-og-rus/rask-psykisk-helsehjelp/", "title": "Rask psykisk helsehjelp"},
    ],
    "Fredrikstad psykisk helse kontakt": [
        {"url": "https://www.fredrikstad.kommune.no/tjenester/barne-og-familietjenester/helsestasjoner/helsestasjon-for-ungdom/", "title": "Helsestasjon for ungdom"},
    ],
    "Askoy psykisk helse voksne": [
        {"url": "https://askoy.kommune.no/tjenester/helse-og-mestring/tjenestetilbud-fysisk-og-psykisk-helse/psykisk-helse/hvordan-ta-kontakt-med-origo", "title": "Origo - hvordan ta kontakt"},
    ],
    "Askoy psykisk helse rus": [
        {"url": "https://askoy.kommune.no/tjenester/barn-unge-og-familie/helsestasjoner-og-skolehelsetjenesten/helsestasjon-for-ungdom-hfu", "title": "HFU"},
    ],
    "Bamble psykisk helse voksne": [
        {"url": "https://www.bamble.kommune.no/helse-og-mestring/psykisk-helse-og-rusomsorg/bamblehjelpa/", "title": "Bamblehjelpa"},
    ],
    "Bamble psykisk helse kontakt": [
        {"url": "https://www.bamble.kommune.no/helse-og-mestring/psykisk-helse-og-rusomsorg/bamblehjelpa/kontaktinformasjon/", "title": "Kontaktinformasjon"},
    ],
    "Bamble helsestasjon ungdom": [
        {"url": "https://www.bamble.kommune.no/barn-unge-og-familie/helsetjenester-for-barn-unge-og-familier/helsestasjon-for-ungdom/", "title": "HFU Bamble"},
    ],
    "Birkenes psykisk helse voksne": [
        {"url": "https://www.birkenes.kommune.no/innhold/helse-og-velferd/psykisk-helse-for-voksne/", "title": "Psykisk helse for voksne"},
    ],
    "Birkenes psykisk helse rus": [
        {"url": "https://www.birkenes.kommune.no/innhold/barnehage-og-skole/ressurssenter/helsestasjon/", "title": "Helsestasjon"},
    ],
    "Bjerkreim psykisk helse voksne": [
        {"url": "https://www.bjerkreim.kommune.no/tjenester/helse-og-omsorg/avdeling-mestring/stotte-nar-livet-er-krevende/", "title": "Avdeling Mestring"},
    ],
    "Alstahaug psykisk helse voksne": [
        {"url": "https://www.alstahaug.kommune.no/tjenester/helse-og-velferd/psykisk-helse--og-rustjeneste/psykisk-helsetjeneste", "title": "Psykisk helsetjeneste"},
    ],
    "Alstahaug helsestasjon ungdom": [
        {"url": "https://www.alstahaug.kommune.no/tjenester/helse-og-velferd/tjenester-til-barn-og-unge/helsestasjon/helsestasjon-for-ungdom", "title": "HFU Alstahaug"},
    ],
    "Etnedal psykisk helse voksne": [
        {"url": "https://www.etnedal.kommune.no/tjenester/familie-helse-og-omsorg/psykisk-helsearbeid/", "title": "Psykisk helsetjeneste Etnedal"},
    ],
    "Etnedal psykisk helse kontakt": [
        {"url": "https://www.etnedal.kommune.no/tjenester/familie-helse-og-omsorg/kommunepsykolog/", "title": "Kommunepsykolog"},
    ],
    "Aure psykisk helse voksne": [
        {"url": "https://www.aure.kommune.no/tjenester/helse-og-omsorg/psykisk-helse-og-rus/psykisk-helsehjelp/", "title": "Psykisk helsehjelp"},
        {"url": "https://www.aure.kommune.no/tjenester/helse-og-omsorg/psykisk-helse-og-rus/kommunepsykolog/", "title": "Kommunepsykolog"},
    ],
    "Aure helsestasjon ungdom": [
        {"url": "https://www.aure.kommune.no/tjenester/helse-og-omsorg/familie-barn-og-ungdom/helsestasjon-for-ungdom/", "title": "HFU Aure"},
    ],
    "Balsfjord psykisk helse voksne": [
        {"url": "https://www.balsfjord.kommune.no/psykisk-helsetjeneste", "title": "Psykisk helsetjeneste"},
        {"url": "https://www.balsfjord.kommune.no/barne-ungdoms-og-familieteamet", "title": "BUF"},
    ],
    "Balsfjord helsestasjon ungdom": [
        {"url": "https://www.balsfjord.kommune.no/helsestasjon-for-ungdom", "title": "HFU Balsfjord"},
    ],
}

GEN_KNOWN_URLS = [
    "https://www.ralingen.kommune.no/artikkel/lavterskel-psykisk-helsehjelp",
    "https://oldralingen.bedreinnsats.no/",
    "https://api.skjema.no/ralingen/templates/pdf/123461/nb",
    "https://www.drammen.kommune.no/tjenester/helse-velferd/helsefremmende-tjenester/rask-psykisk-helsehjelp/",
    "https://www.drammen.kommune.no/tjenester/helse-velferd/helsefremmende-tjenester/drammen/helsestasjon-for-ungdom-drammen/",
    "https://www.fredrikstad.kommune.no/tjenester/helse/psykisk-helse-og-rus/rask-psykisk-helsehjelp/",
    "https://www.fredrikstad.kommune.no/tjenester/barne-og-familietjenester/helsestasjoner/helsestasjon-for-ungdom/",
    "https://askoy.kommune.no/tjenester/helse-og-mestring/tjenestetilbud-fysisk-og-psykisk-helse/psykisk-helse/hvordan-ta-kontakt-med-origo",
    "https://askoy.kommune.no/tjenester/barn-unge-og-familie/helsestasjoner-og-skolehelsetjenesten/helsestasjon-for-ungdom-hfu",
    "https://www.bamble.kommune.no/helse-og-mestring/psykisk-helse-og-rusomsorg/bamblehjelpa/",
    "https://www.bamble.kommune.no/helse-og-mestring/psykisk-helse-og-rusomsorg/bamblehjelpa/kontaktinformasjon/",
    "https://www.bamble.kommune.no/barn-unge-og-familie/helsetjenester-for-barn-unge-og-familier/helsestasjon-for-ungdom/",
    "https://www.birkenes.kommune.no/innhold/helse-og-velferd/psykisk-helse-for-voksne/",
    "https://www.birkenes.kommune.no/innhold/barnehage-og-skole/ressurssenter/helsestasjon/",
    "https://www.bjerkreim.kommune.no/tjenester/helse-og-omsorg/avdeling-mestring/stotte-nar-livet-er-krevende/",
    "https://www.alstahaug.kommune.no/tjenester/helse-og-velferd/psykisk-helse--og-rustjeneste/psykisk-helsetjeneste",
    "https://www.alstahaug.kommune.no/tjenester/helse-og-velferd/tjenester-til-barn-og-unge/helsestasjon/helsestasjon-for-ungdom",
    "https://www.etnedal.kommune.no/tjenester/familie-helse-og-omsorg/psykisk-helsearbeid/",
    "https://www.etnedal.kommune.no/tjenester/familie-helse-og-omsorg/kommunepsykolog/",
    "https://www.aure.kommune.no/tjenester/helse-og-omsorg/psykisk-helse-og-rus/psykisk-helsehjelp/",
    "https://www.aure.kommune.no/tjenester/helse-og-omsorg/psykisk-helse-og-rus/kommunepsykolog/",
    "https://www.aure.kommune.no/tjenester/helse-og-omsorg/familie-barn-og-ungdom/helsestasjon-for-ungdom/",
    "https://www.balsfjord.kommune.no/psykisk-helsetjeneste",
    "https://www.balsfjord.kommune.no/barne-ungdoms-og-familieteamet",
    "https://www.balsfjord.kommune.no/helsestasjon-for-ungdom",
]

# ---------------------------------------------------------------------------
# Access V1 target fixtures (9 targets)
# ---------------------------------------------------------------------------

ACCESS_PAGES = {
    "https://www.alta.kommune.no/tjenester/helse-og-omsorg/psykisk-helse/psykisk-helse-og-rus": page(
        "Psykisk helse og rus - Alta",
        p("Psykisk helse og rus gir ulike hjelpetilbud til deg over 18 \u00e5r. "
          "Virksomheten best\u00e5r av fire tjenester: Lavterskeltjenesten, "
          "Samtaletjenesten, ROP oppf\u00f8lgingstjenesten og Boligtjenesten. "
          "For veiledning - ta kontakt med Tjenestekontoret v\u00e5rt. "
          "Kontaktinformasjon f\u00e5r du ved \u00e5 trykke her."),
    ),
    "https://www.alta.kommune.no/tjenester/helse-og-omsorg/tjenestekontor": page(
        "Tjenestekontor - Alta",
        p("E-post: tjenestekontoret@alta.kommune.no Avdelingsleder "
          "Tjenestekontor Jorunn Sleveland Nordholm Telefon: 90 24 32 61"),
    ),
    "https://www.alta.kommune.no/tjenester/helse-og-omsorg/psykisk-helse/psykisk-helse-og-rus/lavterskelteam": page(
        "Lavterskelteam - Alta",
        p("Du trenger ingen henvisning, og en digital kartlegging danner "
          "grunnlaget for en avklaringssamtale og videre oppf\u00f8lging.")
        + p("Mob: 475 19 058 (bemannet man, ons, fre kl. 09.00-11.00 og "
            "13.00-14.00) E-post: lavterskelpsykiskhelse@alta.kommune.no"),
    ),
    "https://www.steinkjer.kommune.no/tjenester/helse-omsorg-og-sosiale-tjenester/helsetjenester/legetjenester/kommunepsykologen/": page(
        "Kommunepsykologen - Steinkjer",
        p("Det er for tiden ikke kapasitet til \u00e5 tilby avklaringssamtaler "
          "og/eller behandling av pasienter. Kommunepsykologen innehar "
          "klinisk vurderingskompetanse, og bidrar prim\u00e6rt med veiledning "
          "av annet helsepersonell i kommunen.")
        + p("\u00d8nsker du kontakt med kommunepsykologen, send e-post til: "
            "Trude Hoff"),
    ),
    "https://www.ulstein.kommune.no/tenester/helse-og-omsorg/tenester-til-heimebuande/psykisk-helse-og-rus/teneste-for-psykisk-helse-og-rus/": page(
        "Teneste for psykisk helse og rus - Ulstein",
        p("Korleis s\u00f8ke om dette tenestetilbodet? Bruk skjema for helse- og "
          "omsorgstenester. Du kan ogs\u00e5 ringe Margaret Bjerkvik.")
        + p("Eit anna alternativ er at fastlegen din eller ein annan instans "
            "sender skriftleg tilvising. N\u00e5r kan du vente svar? S\u00f8knader vert "
            "handsama."),
    ),
    "https://www.ulstein.kommune.no/tenester/helse-og-omsorg/tenester-til-heimebuande/psykisk-helse-og-rus/kommunepsykolog/": page(
        "Kommunepsykolog - Ulstein",
        p("Hovudoppg\u00e5va til kommunepsykologtenesta er f\u00f8rebygging og "
          "helsefremmande arbeid. Vi hjelper kommunen i sp\u00f8rsm\u00e5l om "
          "psykisk helse i alle tenester. Kommunepsykologen tilbyr rettleiing "
          "og fagst\u00f8tte til tilsette og faggrupper i kommunen."),
    ),
    "https://www.orland.kommune.no/vare-tjenester/helse-omsorg-og-sosiale-tjenester/psykisk-helse-og-rus/psykisk-helse/psykisk-helse-ungdom/": page(
        "Psykisk helse ungdom - Orland",
        p("Hvis disse tjenestene allerede er fors\u00f8kt, med liten til ingen "
          "forbedring kan Ambulant ungdomsteam kontaktes. Ta kontakt med "
          "ambulant ungdomsteam.")
        + p("Dorte Beate Solvik, Leder (helse og omsorg), Mobil 90 89 85 04. "
            "Nina Anita Loeng Mjelde, Fagutvikler."),
    ),
    "https://www.orland.kommune.no/vare-tjenester/helse-omsorg-og-sosiale-tjenester/lege-og-helsetjenester/helsestasjonen/helsestasjon-for-ungdom/": page(
        "Helsestasjon for ungdom - Orland",
        p("\u00c5pningstider HFU 26. august: kl.14:30 - 17:30, 09. september: "
          "kl. 14:30 - 17:30, 16. desember: kl. 14:30 - 17:30.")
        + p("HFU finner du i helsestasjonens lokaler, Orland Medisinske "
            "senter, inngang A, 2. etasje. Kontakt oss. Telefon til "
            "helsestasjon: 72 51 97 80"),
    ),
    "https://www.askvoll.kommune.no/tenestene-vare/helse-og-omsorg/psykisk-helse-og-rusteneste/": page(
        "Psykisk helse- og rusteneste - Askvoll",
        p("Psykisk helse- og rusteneste for vaksne er eit gratis "
          "l\u00e5gterskeltilbod for unge og vaksne over 18 \u00e5r. Du treng "
          "ikkje tilvising for \u00e5 f\u00e5 hjelp."),
    ),
    "https://www.askvoll.kommune.no/tenestene-vare/helse-og-omsorg/psykisk-helse-og-rusteneste/psykisk-helse-og-rusteneste-for-vaksne/": page(
        "Psykisk helse- og rusteneste for vaksne - Askvoll",
        p("Linda Kvalheim, Psykisk helsearbeider, Telefon 41 62 13 03. "
          "Connie Aven, Psykiatrisk sjukepleiar, Telefon 93 06 64 23. "
          "Sidsel F\u00e6nn Kongsvik, Ruskonsulent, Telefon 57 73 45 10, "
          "Mobil 48 00 41 48."),
    ),
    "https://hasvik.kommune.no/tjenester/helse-og-omsorg/helsestasjon": page(
        "Helsestasjon - Hasvik",
        p("Skolehelsetjenesten. Helsesykepleier har kontortid p\u00e5 alle "
          "skolene i kommunen. Skolehelsetjenesten tilbyr samtaler med "
          "elever, individuelt eller i grupper, og kan henvise eleven videre "
          "ved behov.")
        + p("Hasvik Legestasjon Telefon: 78 45 25 00. Jordmor: time bestilles "
            "via legekontoret."),
    ),
    "https://hasvik.kommune.no/tjenester/helse-og-omsorg/helsetjenester/rus-og-psykiatri/psykisk-helse": page(
        "Psykisk helse - Hasvik",
        p("Helsesykepleier: Ragnhild Torkildsen. Telefon: 78 45 25 56."),
    ),
}

ACCESS_SEARCH_INDEX = {
    "Alta psykisk helse voksne": [
        {"url": "https://www.alta.kommune.no/tjenester/helse-og-omsorg/psykisk-helse/psykisk-helse-og-rus", "title": "Psykisk helse og rus"},
    ],
    "Steinkjer psykisk helse kontakt": [
        {"url": "https://www.steinkjer.kommune.no/tjenester/helse-omsorg-og-sosiale-tjenester/helsetjenester/legetjenester/kommunepsykologen/", "title": "Kommunepsykologen"},
    ],
    "Ulstein psykisk helse voksne": [
        {"url": "https://www.ulstein.kommune.no/tenester/helse-og-omsorg/tenester-til-heimebuande/psykisk-helse-og-rus/teneste-for-psykisk-helse-og-rus/", "title": "Teneste for psykisk helse og rus"},
        {"url": "https://www.ulstein.kommune.no/tenester/helse-og-omsorg/tenester-til-heimebuande/psykisk-helse-og-rus/kommunepsykolog/", "title": "Kommunepsykolog"},
    ],
    "Orland psykisk helse ungdom": [
        {"url": "https://www.orland.kommune.no/vare-tjenester/helse-omsorg-og-sosiale-tjenester/psykisk-helse-og-rus/psykisk-helse/psykisk-helse-ungdom/", "title": "Ambulant ungdomsteam"},
    ],
    "Orland helsestasjon ungdom": [
        {"url": "https://www.orland.kommune.no/vare-tjenester/helse-omsorg-og-sosiale-tjenester/lege-og-helsetjenester/helsestasjonen/helsestasjon-for-ungdom/", "title": "HFU Orland"},
    ],
    "Askvoll psykisk helse voksne": [
        {"url": "https://www.askvoll.kommune.no/tenestene-vare/helse-og-omsorg/psykisk-helse-og-rusteneste/", "title": "Psykisk helse- og rusteneste"},
    ],
    "Hasvik helsestasjon": [
        {"url": "https://hasvik.kommune.no/tjenester/helse-og-omsorg/helsestasjon", "title": "Helsestasjon"},
        {"url": "https://hasvik.kommune.no/tjenester/helse-og-omsorg/helsetjenester/rus-og-psykiatri/psykisk-helse", "title": "Psykisk helse"},
    ],
}

ACCESS_KNOWN_URLS = list(ACCESS_PAGES.keys())


def build_manifest():
    pages = {}
    manifest_entries = []
    for role, source in [("generalization_replay", GEN_PAGES),
                         ("access_regression", ACCESS_PAGES)]:
        for url, html in source.items():
            content = html.encode("utf-8")
            h = hashlib.sha256(content).hexdigest()
            pages[url] = {"content": html, "status": 200, "captured_at": RETRIEVED}
            manifest_entries.append({
                "url": url,
                "sha256": h,
                "captured_at": RETRIEVED,
                "replay_role": role,
                "byte_size": len(content),
            })

    all_pages = {**GEN_PAGES, **ACCESS_PAGES}
    search_index = {**GEN_SEARCH_INDEX, **ACCESS_SEARCH_INDEX}
    known_urls = list(dict.fromkeys(GEN_KNOWN_URLS + ACCESS_KNOWN_URLS))

    manifest = {
        "manifest_version": "1.0",
        "created_at": RETRIEVED,
        "description": "Synthetic replay fixtures built from frozen research "
                       "artifacts (generalization V1 + access verification V1). "
                       "Each page contains verbatim quotes from the frozen "
                       "artifacts. These are DATA for replay, not runtime logic.",
        "retrieved_date": RETRIEVED,
        "pages": pages,
        "search_index": search_index,
        "known_urls": known_urls,
        "fixture_entries": manifest_entries,
    }
    return manifest


if __name__ == "__main__":
    m = build_manifest()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixture-manifest.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(m, f, indent=2, ensure_ascii=False)
    print("Wrote %s with %d pages, %d search entries, %d known URLs" %
          (out, len(m["pages"]), len(m["search_index"]), len(m["known_urls"])))
