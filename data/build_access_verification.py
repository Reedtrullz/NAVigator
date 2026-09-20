"""Builds data/local-access-verification-v1.json from the frozen target list.

All evidence was retrieved live from official municipal pages on 2026-09-09
(level 0-2 of the discovery ladder). Generic switchboard/footer phones are
excluded as access evidence per protocol rule ACCESS-E2.
"""
import json

D = "2026-09-09"

def ev(quote, url, updated=None, via="KNOWN_PAGE_CONTENT"):
    return {
        "quote": quote,
        "source_url": url,
        "source_page_last_updated": updated,
        "retrieved_date": D,
        "discovered_via": via,
    }

T = {}

T["T1"] = dict(
    outcome="RESOLVED",
    after=dict(
        access_clear="yes",
        canonical_access_methods=["DIRECT_PHONE", "DIRECT_EMAIL"],
        self_referral="CONDITIONAL",
        self_referral_note="Direkte kontakt via Tjenestekontoret er dokumentert som veiledningsinngang; inntak per tjeneste (Lavterskeltjenesten, Samtaletjenesten, ROP, Bolig) er ikke detaljert publisert.",
        route_confidence="ROUTE_FULLY_VERIFIED",
    ),
    evidence=[
        ev("For veiledning - ta kontakt med Tjenestekontoret vårt. Kontaktinformasjon får du ved å trykke her",
           "https://www.alta.kommune.no/tjenester/helse-og-omsorg/psykisk-helse/psykisk-helse-og-rus"),
        ev("E-post: tjenestekontoret@alta.kommune.no ... Avdelingsleder Tjenestekontor Jorunn Sleveland Nordholm ... Telefon: 90 24 32 61",
           "https://www.alta.kommune.no/tjenester/helse-og-omsorg/tjenestekontor", via="NAVIGATION_LINK"),
    ],
    log=dict(level_0=True, level_1=True, level_2=True, level_3=False, level_4=False, level_5=False,
             terminal_state="ACCESS_VERIFIED",
             inspected_urls=["https://www.alta.kommune.no/tjenester/helse-og-omsorg/psykisk-helse/psykisk-helse-og-rus",
                             "https://www.alta.kommune.no/tjenester/helse-og-omsorg/tjenestekontor"],
             edges=[{"from": "psykisk-helse-og-rus", "relation": "link (Kontaktinformasjon får du ved å trykke her)", "to": "tjenestekontor"}],
             queries=[],
             rejected=[{"url": "https://www.alta.kommune.no (footer Tlf 78 45 50 00)", "reason": "generelt sentralbord, ikke tjenestekoblet (protokollregel ACCESS-E2)"}]),
)

T["T2"] = dict(
    outcome="RESOLVED",
    after=dict(
        access_clear="yes",
        canonical_access_methods=["DIRECT_PHONE", "DIRECT_EMAIL"],
        self_referral="YES",
        self_referral_note="Eksplisitt: «Du trenger ingen henvisning»; digital kartlegging danner grunnlag for avklaringssamtale.",
        route_confidence="ROUTE_FULLY_VERIFIED",
    ),
    evidence=[
        ev("Du trenger ingen henvisning, og en digital kartlegging danner grunnlaget for en avklaringssamtale og videre oppfølging.",
           "https://www.alta.kommune.no/tjenester/helse-og-omsorg/psykisk-helse/psykisk-helse-og-rus/lavterskelteam"),
        ev("Mob: 475 19 058 (bemannet man, ons, fre kl. 09.00-11.00 og 13.00-14.00) E-post: lavterskelpsykiskhelse@alta.kommune.no",
           "https://www.alta.kommune.no/tjenester/helse-og-omsorg/psykisk-helse/psykisk-helse-og-rus/lavterskelteam"),
    ],
    log=dict(level_0=True, level_1=True, level_2=False, level_3=False, level_4=False, level_5=False,
             terminal_state="ACCESS_VERIFIED",
             inspected_urls=["https://www.alta.kommune.no/tjenester/helse-og-omsorg/psykisk-helse/psykisk-helse-og-rus/lavterskelteam"],
             edges=[], queries=[],
             rejected=[{"url": "https://www.alta.kommune.no (footer Tlf 78 45 50 00)", "reason": "generelt sentralbord (ACCESS-E2)"}]),
)

T["T3"] = dict(
    outcome="RESOLVED",
    after=dict(
        access_clear="yes",
        canonical_access_methods=["OTHER_PROFESSIONAL_REFERRAL", "DIRECT_EMAIL"],
        self_referral="NO",
        self_referral_note="Lukket negativt: tjenesten har per i dag ikke kapasitet til avklaringssamtaler/behandling av pasienter; e-post er kontaktvei for kommunepsykologens veiledningsrolle.",
        route_confidence="ROUTE_EXISTENCE_ONLY",
    ),
    evidence=[
        ev("Det er for tiden ikke kapasitet til å tilby avklaringssamtaler og/eller behandling av pasienter. Kommunepsykologen innehar klinisk vurderingskompetanse, og bidrar primært med veiledning av annet helsepersonell i kommunen.",
           "https://www.steinkjer.kommune.no/tjenester/helse-omsorg-og-sosiale-tjenester/helsetjenester/legetjenester/kommunepsykologen/",
           updated="2025-09-30"),
        ev("Ønsker du kontakt med kommunepsykologen, send e-post til: Trude Hoff",
           "https://www.steinkjer.kommune.no/tjenester/helse-omsorg-og-sosiale-tjenester/helsetjenester/legetjenester/kommunepsykologen/",
           updated="2025-09-30"),
    ],
    log=dict(level_0=True, level_1=True, level_2=False, level_3=False, level_4=False, level_5=False,
             terminal_state="REFERRAL_VERIFIED",
             inspected_urls=["https://www.steinkjer.kommune.no/tjenester/helse-omsorg-og-sosiale-tjenester/helsetjenester/legetjenester/kommunepsykologen/"],
             edges=[], queries=[],
             rejected=[{"url": "Steinkjer kommune footer Telefon 74 16 90 00", "reason": "generelt sentralbord (ACCESS-E2)"}]),
)

T["T4"] = dict(
    outcome="RESOLVED",
    after=dict(
        access_clear="yes",
        canonical_access_methods=["APPLICATION_FORM", "DIRECT_PHONE", "GP_REFERRAL", "OTHER_PROFESSIONAL_REFERRAL"],
        self_referral="YES",
        self_referral_note="Innbygger kan selv søke via kommunalt skjema eller ringe tjenesten; hjelpeomfang vedtas etter kartleggingssamtale (vedtaksbasert).",
        route_confidence="ROUTE_FULLY_VERIFIED",
    ),
    evidence=[
        ev("Korleis søke om dette tenestetilbodet? Bruk skjema for helse- og omsorgstenester. Du kan også ringe Margaret Bjerkvik ... Eit anna alternativ er at fastlegen din eller ein annan instans sender skriftleg tilvising. Når kan du vente svar? Søknader vert fortløpande behandla.",
           "https://www.ulstein.kommune.no/tenester/helse-og-omsorg/tenester-til-heimebuande/psykisk-helse-og-rus/teneste-for-psykisk-helse-og-rus/",
           updated="2026-04-23"),
    ],
    evidence_edges=[
        {"type": "APPLICATION_FORM", "url": "https://skjema.ulstein.kommune.no/skjema/ULS097/Sknad_om_helse_og_omsorgsteneste_",
         "discovered_via": "NAVIGATION_LINK", "inspected": False,
         "note": "Form-URL hentet fra tjenestesidens lenketekst «skjema for helse- og omsorgstenester»; eksistens er bevist av tjenestesidens eksplisitte tekst."},
    ],
    log=dict(level_0=True, level_1=True, level_2=True, level_3=False, level_4=False, level_5=False,
             terminal_state="ACCESS_VERIFIED",
             inspected_urls=["https://www.ulstein.kommune.no/tenester/helse-og-omsorg/tenester-til-heimebuande/psykisk-helse-og-rus/teneste-for-psykisk-helse-og-rus/"],
             edges=[{"from": "teneste-for-psykisk-helse-og-rus", "relation": "link (skjema for helse- og omsorgstenester)", "to": "skjema.ulstein.kommune.no ULS097"}],
             queries=[],
             rejected=[{"url": "Ulstein sentralbord 70 01 75 00", "reason": "generelt sentralbord (ACCESS-E2); tjenestekoblet telefon finnes via navngitt ansatt"}]),
)

T["T5"] = dict(
    outcome="RESOLVED",
    after=dict(
        access_clear="yes",
        canonical_access_methods=["OTHER_PROFESSIONAL_REFERRAL"],
        self_referral="NO",
        self_referral_note="Lukket negativt: tenesta er systemrettet (førebygging, rettleiing til tilsette, systemarbeid); ingen pasientinntak dokumentert.",
        route_confidence="ROUTE_EXISTENCE_ONLY",
    ),
    intermunicipal_provenance=dict(
        resident_municipality=["Ulstein", "Sande"],
        host_municipality=None,
        service_operator="Ulstein og Sande interkommunal psykologteneste (psykologspesialist og psykolog)",
        eligibility_evidence="Ulstein og Sande samarbeider om ei interkommunal psykologteneste.",
        access_evidence="Rettleiing og fagstøtte til tilsette og faggrupper i kommunen; ingen individuell inngang publisert.",
    ),
    evidence=[
        ev("Hovudoppgåva til kommunepsykologtenesta er førebygging og helsefremmande arbeid. Vi hjelper kommunen i spørsmål om psykisk helse i alle tenester ... Kommunepsykologen tilbyr rettleiing og fagstøtte til tilsette og faggrupper i kommunen.",
           "https://www.ulstein.kommune.no/tenester/helse-og-omsorg/tenester-til-heimebuande/psykisk-helse-og-rus/kommunepsykolog/",
           updated="2026-04-23"),
    ],
    log=dict(level_0=True, level_1=True, level_2=False, level_3=False, level_4=True, level_5=False,
             terminal_state="REFERRAL_VERIFIED",
             inspected_urls=["https://www.ulstein.kommune.no/tenester/helse-og-omsorg/tenester-til-heimebuande/psykisk-helse-og-rus/kommunepsykolog/"],
             edges=[], queries=[],
             rejected=[{"url": "Ulstein sentralbord 70 01 75 00", "reason": "generelt sentralbord (ACCESS-E2)"}]),
)

T["T6"] = dict(
    outcome="RESOLVED",
    after=dict(
        access_clear="yes",
        canonical_access_methods=["DIRECT_PHONE", "DIRECT_EMAIL", "OTHER_PROFESSIONAL_REFERRAL"],
        self_referral="CONDITIONAL",
        self_referral_note="Direkte kontakt er dokumentert («kan Ambulant ungdomsteam kontaktes»), men tjenesten er steg 2: forutsetter at Ungdomslos og Familieteam er forsøkt.",
        route_confidence="ROUTE_FULLY_VERIFIED",
    ),
    evidence=[
        ev("Hvis disse tjenestene allerede er forsøkt, med liten til ingen forbedring kan Ambulant ungdomsteam kontaktes. ... Ta kontakt med ambulant ungdomsteam ... Dorte Beate Solvik Leder (helse og omsorg) ... Mobil 90 89 85 04 ... Nina Anita Loeng Mjelde Fagleder BUF team ... Mobil 47 68 22 36",
           "https://www.orland.kommune.no/vare-tjenester/helse-omsorg-og-sosiale-tjenester/psykisk-helse-og-rus/psykisk-helse/psykisk-helse-ungdom/"),
    ],
    log=dict(level_0=True, level_1=True, level_2=False, level_3=False, level_4=False, level_5=False,
             terminal_state="ACCESS_VERIFIED",
             inspected_urls=["https://www.orland.kommune.no/vare-tjenester/helse-omsorg-og-sosiale-tjenester/psykisk-helse-og-rus/psykisk-helse/psykisk-helse-ungdom/"],
             edges=[], queries=[], rejected=[]),
)

T["T7"] = dict(
    outcome="RESOLVED",
    after=dict(
        access_clear="yes",
        canonical_access_methods=["DIRECT_DROPIN", "DIRECT_PHONE"],
        self_referral="YES",
        self_referral_note="Publiserte drop-in-åpningstider (fast datoformat, to ukers rytme) + tjenestekoblet telefon.",
        route_confidence="ROUTE_FULLY_VERIFIED",
    ),
    evidence=[
        ev("Åpningstider HFU 26. august: kl.14:30 - 17:30 09. september: kl. 14:30 - 17:30 ... 16. desember: kl. 14:30 - 17:30",
           "https://www.orland.kommune.no/vare-tjenester/helse-omsorg-og-sosiale-tjenester/lege-og-helsetjenester/helsestasjonen/helsestasjon-for-ungdom/"),
        ev("HFU finner du i helsestasjonens lokaler, Ørland Medisinske senter, inngang A, 2. etasje. Kontakt oss Telefon til helsestasjon: 72 51 97 80",
           "https://www.orland.kommune.no/vare-tjenester/helse-omsorg-og-sosiale-tjenester/lege-og-helsetjenester/helsestasjonen/helsestasjon-for-ungdom/"),
    ],
    log=dict(level_0=True, level_1=True, level_2=False, level_3=False, level_4=False, level_5=False,
             terminal_state="ACCESS_VERIFIED",
             inspected_urls=["https://www.orland.kommune.no/vare-tjenester/helse-omsorg-og-sosiale-tjenester/lege-og-helsetjenester/helsestasjonen/helsestasjon-for-ungdom/"],
             edges=[], queries=[], rejected=[]),
)

T["T8"] = dict(
    outcome="RESOLVED",
    after=dict(
        access_clear="yes",
        canonical_access_methods=["DIRECT_PHONE"],
        self_referral="YES",
        self_referral_note="Eksplisitt på foreldresiden: «Du treng ikkje tilvising for å få hjelp»; navngitte ansattes telefoner er tjenestekoblet kontakt.",
        route_confidence="ROUTE_FULLY_VERIFIED",
    ),
    evidence=[
        ev("Psykisk helse- og rusteneste for vaksne er eit gratis lågterskeltilbod for unge og vaksne over 18 år. Du treng ikkje tilvising for å få hjelp.",
           "https://www.askvoll.kommune.no/tenestene-vare/helse-og-omsorg/psykisk-helse-og-rusteneste/", via="NAVIGATION_LINK"),
        ev("Linda Kvalheim Psykisk helsearbeider ... Telefon 41 62 13 03 Connie Aven Psykiatrisk sjukepleiar ... Telefon 93 06 64 23 Sidsel Fænn Kongsvik Ruskonsulent ... Telefon 57 73 45 10 Mobil 48 00 41 48",
           "https://www.askvoll.kommune.no/tenestene-vare/helse-og-omsorg/psykisk-helse-og-rusteneste/psykisk-helse-og-rusteneste-for-vaksne/",
           updated="2026-06-19"),
    ],
    log=dict(level_0=True, level_1=True, level_2=True, level_3=False, level_4=False, level_5=False,
             terminal_state="ACCESS_VERIFIED",
             inspected_urls=["https://www.askvoll.kommune.no/tenestene-vare/helse-og-omsorg/psykisk-helse-og-rusteneste/",
                             "https://www.askvoll.kommune.no/tenestene-vare/helse-og-omsorg/psykisk-helse-og-rusteneste/psykisk-helse-og-rusteneste-for-vaksne/"],
             edges=[{"from": "psykisk-helse-og-rusteneste (foreldreside)", "relation": "navigation", "to": "psykisk-helse-og-rusteneste-for-vaksne"}],
             queries=[],
             rejected=[{"url": "Askvoll footer Ring oss: 57 73 07 00", "reason": "generelt sentralbord (ACCESS-E2)"}]),
)

T["T9"] = dict(
    outcome="PARTIALLY_RESOLVED",
    after=dict(
        access_clear="partial",
        canonical_access_methods=["DIRECT_DROPIN", "DIRECT_PHONE"],
        self_referral="CONDITIONAL",
        self_referral_note="Skoleelever: direkte kontakt via helsesykepleiers kontortid på skolene. Ikke-skolegående 19-åring: eksplisitt bokingsvei ikke publisert; legekontor/helsesekretær (78 45 25 00) er dokumentert kontakt-/bockingskanal for helsestasjonspersonell, og helsesykepleiers telefon er publisert på FFR-sidens ansattliste.",
        route_confidence="ROUTE_ACCESS_PARTIAL",
    ),
    evidence=[
        ev("Skolehelsetjenesten ... Helsesykepleier har kontortid på alle skolene i kommunen. Skolehelsetjenesten tilbyr: ... Samtaler med elever, individuelt eller i grupper ... kan henvise eleven videre ved behov.",
           "https://hasvik.kommune.no/tjenester/helse-og-omsorg/helsestasjon", updated="2023-03-01"),
        ev("Hasvik Legestasjon Telefon: 78 45 25 00 ... Jordmor ... time bestilles via legekontoret",
           "https://hasvik.kommune.no/tjenester/helse-og-omsorg/helsestasjon", updated="2023-03-01"),
        ev("Helsesykepleier: Ragnhild Torkildsen Telefon: 78 45 25 56",
           "https://hasvik.kommune.no/tjenester/helse-og-omsorg/helsetjenester/rus-og-psykiatri/psykisk-helse",
           updated="2023-02-16", via="NAVIGATION_LINK"),
    ],
    log=dict(level_0=True, level_1=True, level_2=True, level_3=True, level_4=False, level_5=False,
             terminal_state="PUBLIC_DATA_EXHAUSTED",
             inspected_urls=["https://hasvik.kommune.no/tjenester/helse-og-omsorg/helsestasjon",
                             "https://hasvik.kommune.no/tjenester/helse-og-omsorg/helsetjenester/rus-og-psykiatri/psykisk-helse",
                             "https://hasvik.kommune.no/tjenester/helse-og-omsorg"],
             edges=[{"from": "helsestasjon", "relation": "related link (Familie, Forebygging og Rehabilitering (FFR))", "to": "rus-og-psykiatri/psykisk-helse (FFR)"}],
             queries=[],
             rejected=[{"url": "https://hasvik.kommune.no/sitemap.xml", "reason": "tomt/ikke tilgjengelig (0 bytes)"}]),
)

targets = json.load(open("data/access-unclear-targets-v1.json"))["targets"]

cat = {
    "T1": "voksen psykisk helse og rus",
    "T2": "lavterskel psykisk helse (voksne)",
    "T3": "kommunepsykolog (systemrettet)",
    "T4": "voksen psykisk helse og rus (vedtaksbasert)",
    "T5": "kommunepsykolog (interkommunal, systemrettet)",
    "T6": "ambulant ungdomsteam (steg 2)",
    "T7": "helsestasjon for ungdom",
    "T8": "voksen psykisk helse og rus (lavterskel)",
    "T9": "helsesykepleier (helsestasjon/skolehelsetjeneste)",
}

out = []
for t in targets:
    tid = t["target_id"]
    rec = dict(t)
    rec["service_category"] = cat[tid]
    rec["before"] = {
        "access_clear": "no",
        "existing_access_model": t["existing_access_fields"]["direct_access"],
        "existing_source_url": t["existing_source_url"],
    }
    rec["after"] = T[tid]["after"]
    rec["outcome"] = T[tid]["outcome"]
    rec["evidence"] = T[tid]["evidence"]
    if "evidence_edges" in T[tid]:
        rec["evidence_edges"] = T[tid]["evidence_edges"]
    if "intermunicipal_provenance" in T[tid]:
        rec["intermunicipal_provenance"] = T[tid]["intermunicipal_provenance"]
    rec["search_log"] = T[tid]["log"]
    out.append(rec)

doc = {
    "task_id": "NAV-EXPLORE-LOCAL-ACCESS-DISCOVERY-PROTOCOL-V1",
    "layer_type": "UPDATE_LAYER",
    "created_at": D,
    "parent_artifacts": [
        "data/municipal-mental-health-sample-v1.json",
        "data/18-23-local-routing-gap-v1.json",
        "data/access-unclear-targets-v1.json",
    ],
    "target_count": len(out),
    "targets": out,
}
json.dump(doc, open("data/local-access-verification-v1.json", "w"), ensure_ascii=False, indent=2)
print("wrote targets:", len(out))
