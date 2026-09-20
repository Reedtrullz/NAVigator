#!/usr/bin/env python3
"""Build 18-23-routing-deep-a.json - all 12 municipalities, evidence captured 2026-09-08."""
import json

def svc(name, age, c19, c22, access, sev, pub, url, quote, notes=""):
    return {
        "service_name": name, "target_age_text": age,
        "covers_age_19": c19, "covers_age_22": c22,
        "direct_access": access, "severity_fit": sev,
        "pub_info": pub, "source_url": url,
        "evidence_quote": quote, "notes": notes,
    }

LOG = {"municipal_service_catalog": True, "mental_health_page": True, "hfu": True,
       "rph": True, "intermunicipal_search": True, "adult_mental_health": True}
V = "VERIFIED_LOCAL_ROUTE"
U = "VERIFIED_LOCAL_SERVICE_ACCESS_UNCLEAR"
S = "SPECIALIST_GATEWAY"

M = []

M.append({
 "kommunenummer": "2021", "kommune": "Alta", "ssb_sentralitetsklasse": 4,
 "search_log": dict(LOG),
 "gap_classification": V, "gap_classification_c_19": V, "gap_classification_d_22": V,
 "gap_classification_v1_c": "NO_MATCHING_LOCAL_SERVICE_FOUND",
 "gap_classification_v1_d": "NO_MATCHING_LOCAL_SERVICE_FOUND",
 "local_delivery_model": "MUNICIPAL",
 "services_18_23": [
  svc("Psykisk helse og rus (voksentilbud, fire tjenester)", "Personer over 18 år", True, True,
      ["DIRECT_PHONE"], "BROAD",
      {"age_clear": "yes", "target_group_clear": "yes", "access_clear": "no", "contact_clear": "yes", "cost_clear": "yes", "service_content_clear": "yes"},
      "https://www.alta.kommune.no/tjenester/helse-og-omsorg/psykisk-helse/psykisk-helse-og-rus",
      "Psykisk helse og rus gir ulike hjelpetilbud til deg over 18 år ... Virksomheten består av fire tjenester: Lavterskeltjenesten, Samtaletjenesten, ROP oppfølgingstjenesten og Boligtjenesten. For veiledning - ta kontakt med Tjenestekontoret",
      "Inntaksløp per tjeneste er ikke detaljert; Tjenestekontor (hverdager 08:30-15:00) dokumentert som veiledningsinngang."),
  svc("Lavterskelteam", "Voksne, lavterskel psykisk helse", True, True,
      ["DIRECT_PHONE"], "MILD_MODERATE",
      {"age_clear": "no", "target_group_clear": "yes", "access_clear": "no", "contact_clear": "yes", "cost_clear": "no", "service_content_clear": "yes"},
      "https://www.alta.kommune.no/tjenester/helse-og-omsorg/psykisk-helse/psykisk-helse-og-rus/lavterskelteam",
      "E-post: lavterskelpsykiskhelse@alta.kommune.no Avdelingsleder: Renathe Aspeli Simonsen ... Mob: 418 78 928",
      "Kontortid publisert; eksplisitt beskrivelse av inntakskriterier mangler på siden."),
  svc("Helsestasjon for ungdom", "Ungdom 13-25 år", True, True,
      ["DIRECT_DROPIN", "DIRECT_PHONE"], "MILD_MODERATE",
      {"age_clear": "yes", "target_group_clear": "yes", "access_clear": "yes", "contact_clear": "yes", "cost_clear": "yes", "service_content_clear": "yes"},
      "https://www.alta.kommune.no/tjenester/helse-og-omsorg/helsetjenester/helsestasjon--og-skolehelsetjenesten/helsestasjon-for-ungdom",
      "Her treffer du helsesykepleier, jordmor og lege. Målgruppen er ungdom 13-25 år. Telefon i åpningstiden er 406 22 473"),
 ],
 "intermunicipal": None,
 "rph_status": "Kommunalt PHR-tilbud (fire tjenester); ingen interkommunal avhengighet dokumentert.",
 "notes": "V1 registrerte NO_MATCH på begge scenarier; dyp kartlegging viser kommunalt voksentilbud 18+ og HFU 13-25. C-rute: PHR/lavterskel; D-rute: HFU + lavterskelteam."
})

M.append({
 "kommunenummer": "5421", "kommune": "Steinkjer", "ssb_sentralitetsklasse": 4,
 "search_log": dict(LOG),
 "gap_classification": V, "gap_classification_c_19": V, "gap_classification_d_22": V,
 "gap_classification_v1_c": "NO_MATCHING_LOCAL_SERVICE_FOUND",
 "gap_classification_v1_d": "NO_MATCHING_LOCAL_SERVICE_FOUND",
 "local_delivery_model": "MUNICIPAL",
 "services_18_23": [
  svc("Psykisk helse (voksentilbud)", "Personer over 18 år", True, True,
      ["APPLICATION_FORM", "GP_REFERRAL"], "MODERATE",
      {"age_clear": "yes", "target_group_clear": "yes", "access_clear": "yes", "contact_clear": "no", "cost_clear": "no", "service_content_clear": "yes"},
      "https://www.steinkjer.kommune.no/tjenester/helse-omsorg-og-sosiale-tjenester/psykisk-helse-og-rus/psykisk-helse/",
      "Psykisk helsehjelp gis til personer over 18 år ... Hjelpen ytes etter behov beskrevet i søknad. ... Ved akutt sykdom eller selvmordstanker Kontakt din fastlege",
      "Tilbud: veiledet selvhjelp, støtte-/terapisamtaler, fysioterapi m.m. Inntak via søknad, ikke drop-in."),
  svc("Helsestasjon for ungdom", "Ungdom 13-20 år; høgskolestudenter til 25", True, "unknown",
      ["DIRECT_DIGITAL"], "MILD_MODERATE",
      {"age_clear": "yes", "target_group_clear": "yes", "access_clear": "yes", "contact_clear": "yes", "cost_clear": "yes", "service_content_clear": "yes"},
      "https://www.steinkjer.kommune.no/tjenester/helse-omsorg-og-sosiale-tjenester/helsetjenester/helsetjenester-for-barn-og-unge-og-familieteam/helsestasjon-for-ungdom/",
      "Helsestasjon for ungdom er et gratis tilbud for ungdom i alderen 13-20 år, og gjelder også for høgskolestudenter opp til 25 år. ... Timeavtaler: Du kan bestille time på e-post: HFU@steinkjer.kommune.no",
      "covers_age_22 = unknown: 22-åring er dekket kun hvis student."),
  svc("Kommunepsykologen", "Ikke publisert", "unknown", "unknown",
      ["UNCLEAR"], "UNKNOWN",
      {"age_clear": "no", "target_group_clear": "no", "access_clear": "no", "contact_clear": "no", "cost_clear": "no", "service_content_clear": "no"},
      "https://www.steinkjer.kommune.no/tjenester/helse-omsorg-og-sosiale-tjenester/helsetjenester/legetjenester/kommunepsykologen/",
      "Kommunen har en kommunepsykolog som er lokalisert på rådhuset i 3.etg.",
      "Tynn side; rolle/inntak ikke beskrevet. Telt som systemrettet tilbud, ikke brukt som hovedbevis."),
 ],
 "intermunicipal": None,
 "rph_status": "Ingen RPH-ordning dokumentert; kommunalt voksentilbud dekker moderat behov via søknad.",
 "notes": "D-klassifisering: VERIFIED_LOCAL_ROUTE tross søknadsinngang - tilbud og tilgangsmåte er dokumentert, men umiddelbar drop-in finnes ikke (merk dette i produktkontekst)."
})

M.append({
 "kommunenummer": "4208", "kommune": "Farsund", "ssb_sentralitetsklasse": 4,
 "search_log": dict(LOG),
 "gap_classification": V, "gap_classification_c_19": V, "gap_classification_d_22": V,
 "gap_classification_v1_c": "LOCAL_ROUTING_UNCLEAR",
 "gap_classification_v1_d": "LOCAL_ROUTING_UNCLEAR",
 "local_delivery_model": "MUNICIPAL",
 "services_18_23": [
  svc("Helsestasjon for ungdom", "Ungdom opp til 25 år", True, True,
      ["DIRECT_DROPIN"], "MILD_MODERATE",
      {"age_clear": "yes", "target_group_clear": "yes", "access_clear": "yes", "contact_clear": "yes", "cost_clear": "yes", "service_content_clear": "yes"},
      "https://www.farsund.kommune.no/tjenester/helse-og-omsorg/helsestasjon/helsestasjon-for-ungdom/",
      "Helsestasjon for ungdom er et åpent, gratis tilbud for ungdom opp til 25 år. Du trenger ikke å bestille time på forhånd. ... treffer du lege og helsesykepleier"),
 ],
 "intermunicipal": None,
 "rph_status": "RPH etablert per Statsforvalteren (aldersgrense uklar lokalt); ikke brukt som hovedbevis i denne runden.",
 "notes": "Kommunens meny viser i tillegg lavterskeltilbud/familieteam for voksne («du kan ta direkte kontakt»), men detaljsider ble ikke fullverifisert i QA-runden; HFU dekker både C og D kildebasert."
})

M.append({
 "kommunenummer": "1573", "kommune": "Ulstein", "ssb_sentralitetsklasse": 4,
 "search_log": dict(LOG),
 "gap_classification": U, "gap_classification_c_19": U, "gap_classification_d_22": S,
 "gap_classification_v1_c": "LOCAL_ROUTING_UNCLEAR",
 "gap_classification_v1_d": "NO_MATCHING_LOCAL_SERVICE_FOUND",
 "local_delivery_model": "MUNICIPAL",
 "services_18_23": [
  svc("Teneste for psykisk helse og rus", "Ingen aldersgrense publisert («oppfølging av unge personar»)", True, True,
      ["DIRECT_PHONE"], "UNKNOWN",
      {"age_clear": "no", "target_group_clear": "yes", "access_clear": "no", "contact_clear": "yes", "cost_clear": "no", "service_content_clear": "yes"},
      "https://www.ulstein.kommune.no/tenester/helse-og-omsorg/tenester-til-heimebuande/psykisk-helse-og-rus/teneste-for-psykisk-helse-og-rus/",
      "Tenesta er eit lågterskeltilbod ... Med fokus på førebygging gir teamet også oppfølging av unge personar. ... det vert skrive vedtak på timetal og innhald i hjelpe",
      "Tverrfaglig team; kontakt via sentralbord 70 01 75 00 / navngitte ansatte. Vedtaksbasert; hverken «rask» hjelp eller eksplisitt aldersgrense er publisert."),
  svc("Kommunepsykolog (interkommunal Ulstein/Sande)", "Systemrettet", "unknown", "unknown",
      ["UNCLEAR"], "UNKNOWN",
      {"age_clear": "no", "target_group_clear": "no", "access_clear": "no", "contact_clear": "no", "cost_clear": "no", "service_content_clear": "yes"},
      "https://www.ulstein.kommune.no/tenester/helse-og-omsorg/tenester-til-heimebuande/psykisk-helse-og-rus/kommunepsykolog/",
      "Ulstein og Sande samarbeider om ei interkommunal psykologteneste. ... Hovudoppgåva ... er førebygging og helsefremmande arbeid. ... rettleiing og systemarbeid",
      "Ikke dokumentert som behandlingstilbud for enkeltinnbyggere."),
  svc("Helsestasjon for ungdom (SSIKT-portal)", "Barn og ungdom 0-25 år", True, True,
      ["DIRECT_PHONE"], "MILD_MODERATE",
      {"age_clear": "yes", "target_group_clear": "yes", "access_clear": "yes", "contact_clear": "no", "cost_clear": "yes", "service_content_clear": "yes"},
      "https://www.ssikt.no/helsestasjonsportal/ulstein-kommune/",
      "Vi gir tenester til barn og ungdom i alderen 0-25 år og deira føresette, samt gravide.",
      "Kommunal tjeneste presentert på interkommunal portal (SSIKT)."),
 ],
 "intermunicipal": {
  "name": "SSIKT (Søre Sunnmøre interkommunale IKT/partnerportal); Ulstein/Sande kommunepsykolog",
  "role": "Portal for HFU; interkommunal kommunepsykolog (systemrettet)",
  "source_url": "https://www.ssikt.no/helsestasjonsportal/ulstein-kommune/"
 },
 "rph_status": "Ingen lokal RPH. Kommune sider peker vaksne til fastlege -> Volda DPS og ungdom til BUP.",
 "notes": "C: PHR-teneste finnes, men inntak/aldersgrense/ventetid er uklar -> ACCESS_UNCLEAR. D: dokumentert «rask»-rute mangler; offentlig info peker mot fastlege -> Volda DPS -> SPECIALIST_GATEWAY."
})

M.append({
 "kommunenummer": "5620", "kommune": "Sør-Varanger", "ssb_sentralitetsklasse": 5,
 "search_log": dict(LOG),
 "gap_classification": V, "gap_classification_c_19": V, "gap_classification_d_22": V,
 "gap_classification_v1_c": "LOCAL_ROUTING_UNCLEAR",
 "gap_classification_v1_d": "NO_MATCHING_LOCAL_SERVICE_FOUND",
 "local_delivery_model": "MUNICIPAL",
 "services_18_23": [
  svc("Psykisk helse og rus (ROP-tjenesten)", "Personer i alle aldre", True, True,
      ["DIRECT_PHONE"], "BROAD",
      {"age_clear": "yes", "target_group_clear": "yes", "access_clear": "yes", "contact_clear": "yes", "cost_clear": "no", "service_content_clear": "yes"},
      "https://sor-varanger.kommune.no/tjenester/helse-omsorg-og-velferd/enhet-for-helse-og-forebygging/psykisk-helse-og-rus/",
      "Tjenesten gir støttesamtaler og behandling til personer i alle aldre ... Når du tar kontakt med oss, starter vi som regel med en mottakssamtale ... Telefon: 400 17 800 (telefontid kl. 12-14, mandag-fredag)",
      "Adresse Riiser Larsens gate 8."),
  svc("Ettervern/ungdomsoppfølging til 25", "Ungdom opp til 25 år (ettervern barnevern eller videregående skole)", True, True,
      ["DIRECT_PHONE"], "UNKNOWN",
      {"age_clear": "yes", "target_group_clear": "yes", "access_clear": "yes", "contact_clear": "yes", "cost_clear": "no", "service_content_clear": "yes"},
      "https://sor-varanger.kommune.no/tjenester/helse-omsorg-og-velferd/enhet-for-helse-og-forebygging/psykisk-helse-og-rus/",
      "Oppfølging kan også gis til ungdom opp til 25 år som mottar ettervern fra barnevernet, eller går på videregående skole.",
      "Betinget målgruppe."),
  svc("Helsestasjon for ungdom", "Ungdom 13-25 år", True, True,
      ["DIRECT_DROPIN"], "MILD_MODERATE",
      {"age_clear": "yes", "target_group_clear": "yes", "access_clear": "yes", "contact_clear": "no", "cost_clear": "yes", "service_content_clear": "yes"},
      "https://sor-varanger.kommune.no/tjenester/helse-omsorg-og-velferd/enhet-for-helse-og-forebygging/helsestasjon/helsestasjon-for-ungdom-hfu/",
      "Ingen timeavtale, vi har drop-in torsdager fra 16.00-18.00. Helsestasjon for ungdom er et GRATIS tilbud til ungdom mellom 13-25 år."),
 ],
 "intermunicipal": None,
 "rph_status": "Kommunal PHR/ROP dekker; ingen interkommunal avhengighet dokumentert.",
 "notes": "V1-UNCLEAR/NO_MATCH reversert: direkte telefon til PHR + HFU drop-in 13-25."
})

M.append({
 "kommunenummer": "3867", "kommune": "Sauda", "ssb_sentralitetsklasse": 5,
 "search_log": dict(LOG),
 "gap_classification": V, "gap_classification_c_19": V, "gap_classification_d_22": V,
 "gap_classification_v1_c": "LOCAL_ROUTING_UNCLEAR",
 "gap_classification_v1_d": "NO_MATCHING_LOCAL_SERVICE_FOUND",
 "local_delivery_model": "MUNICIPAL",
 "services_18_23": [
  svc("Psykisk helse voksne", "Voksne (ingen eksplisitt aldersgrense publisert)", "unknown", True,
      ["DIRECT_PHONE", "GP_REFERRAL"], "BROAD",
      {"age_clear": "no", "target_group_clear": "yes", "access_clear": "yes", "contact_clear": "yes", "cost_clear": "yes", "service_content_clear": "yes"},
      "https://www.sauda.kommune.no/tjenester/helse-og-velferd/rus-og-psykisk-helsetjeneste/psykisk-helse-voksne/",
      "Dersom du har behov for å komme i kontakt med oss kan du be fastlegen din om en henvisning eller du kan ta kontakt med vår kontakt tlf på tlf nr: 456 35 068, åpningstider mandager og onsdager",
      "«Voksne» antatt å omfatte 18+; eksplisitt nedre/øvre grense ikke publisert. Individuell oppfølging/samtaler på kontor eller hjem; gratis."),
  svc("Helsestasjon for ungdom", "Ungdom 13-20 år", True, False,
      ["DIRECT_DROPIN"], "MILD_MODERATE",
      {"age_clear": "yes", "target_group_clear": "yes", "access_clear": "yes", "contact_clear": "no", "cost_clear": "yes", "service_content_clear": "yes"},
      "https://www.sauda.kommune.no/tjenester/helse-og-velferd/helsetjenester/helsestasjon/helsestasjon-for-ungdom/",
      "Helsestasjon for ungdom er et gratis drop-in tilbud til ungdom mellom 13-20 år, og er et tillegg til skolehelsetjenesten."),
  svc("ROP-team (rus og psykisk helse)", "Ikke publisert", "unknown", "unknown",
      ["GP_REFERRAL", "APPLICATION_FORM"], "BROAD",
      {"age_clear": "no", "target_group_clear": "no", "access_clear": "yes", "contact_clear": "yes", "cost_clear": "yes", "service_content_clear": "yes"},
      "https://www.sauda.kommune.no/tjenester/helse-og-velferd/rus-og-psykisk-helsetjeneste/rop-team-rus-og-psykisk-helse/",
      "Dette er et gratis helsetilbud i kommunen som er vedtaksbasert. Dersom du har behov for å komme i kontakt med oss kan du be fastlegen din om henvisning, eller søke tjenester via Tildelingskontoret.",
      "Mobil 48 99 00 23."),
 ],
 "intermunicipal": None,
 "rph_status": "Kommunale tilbud (voksen + ROP) dekker; ingen RPH-tidsordre dokumentert.",
 "notes": "19-åring: HFU drop-in + voksen-tjeneste. 22-åring: voksen-tjeneste direkte telefon (HFU grense 20)."
})

M.append({
 "kommunenummer": "3421", "kommune": "Tynset", "ssb_sentralitetsklasse": 5,
 "search_log": dict(LOG),
 "gap_classification": V, "gap_classification_c_19": V, "gap_classification_d_22": V,
 "gap_classification_v1_c": "LOCAL_ROUTING_UNCLEAR",
 "gap_classification_v1_d": "NO_MATCHING_LOCAL_SERVICE_FOUND",
 "local_delivery_model": "MUNICIPAL",
 "services_18_23": [
  svc("Psykisk helse- og rustjenester (voksen PHR)", "Ingen aldersgrense publisert", True, True,
      ["DIRECT_PHONE", "APPLICATION_FORM", "GP_REFERRAL"], "MODERATE",
      {"age_clear": "no", "target_group_clear": "yes", "access_clear": "yes", "contact_clear": "yes", "cost_clear": "yes", "service_content_clear": "yes"},
      "https://www.tynset.kommune.no/tjenester/helse/helsetjenester/psykisk-helse-og-rustjenester/",
      "Du kan henvende deg til psykisk helse- og rustjenester selv ved direkte kontakt, søknadsskjema eller fastlege. Innen to uker etter henvendelsen skal det være gjort kontakt for tilbud om vurderingssamtale. Tjenesten er gratis.",
      "Leder Jeanne Solvang tlf 47 79 18 49; Servicetorget 624 85 000. Lavterskeltilbud (Nystua, uten vedtak) er også omtalt i kommunens kilder, ikke separat verifisert i QA-runden."),
  svc("Helsestasjon for ungdom", "Ungdom 13-25 år", True, True,
      ["DIRECT_DROPIN"], "MILD_MODERATE",
      {"age_clear": "yes", "target_group_clear": "yes", "access_clear": "yes", "contact_clear": "yes", "cost_clear": "yes", "service_content_clear": "yes"},
      "https://www.tynset.kommune.no/tjenester/helse/helsetjenester/helsestasjon-skolehelsetjeneste-helsestasjon-for-ungdom-jordmor/",
      "Helsestasjon for ungdom Gratis tilbud til ungdom mellom 13-25 år Åpent mandager fra kl 14.30-16.00"),
 ],
 "intermunicipal": {
  "name": "FARTT (Folldal/Alvdal/Rendalen/Tynset/Tolga) kommunepsykolog",
  "role": "Systemrettet; tar ikke imot henvisning til utredning eller behandling",
  "source_url": "https://www.tynset.kommune.no/tjenester/helse/helsetjenester/psykisk-helse-og-rustjenester/"
 },
 "rph_status": "Ingen RPH dokumentert; kommunal PHR har 2-ukers kontaktnorm.",
 "notes": "Begge scenarier reversert: direkte kontakt + søknadsskjema + HFU 13-25 drop-in."
})

M.append({
 "kommunenummer": "5042", "kommune": "Ørland", "ssb_sentralitetsklasse": 5,
 "search_log": dict(LOG),
 "gap_classification": V, "gap_classification_c_19": V, "gap_classification_d_22": V,
 "gap_classification_v1_c": "MULTIPLE_VALID_ROUTES",
 "gap_classification_v1_d": "MULTIPLE_VALID_ROUTES",
 "local_delivery_model": "INTERMUNICIPAL_HOST",
 "services_18_23": [
  svc("Rask psykisk helsehjelp (Fosen Helse IKS)", "Personer over 16 år (Indre Fosen, Åfjord, Ørland)", True, True,
      ["DIRECT_PHONE", "DIRECT_DIGITAL"], "MILD_MODERATE",
      {"age_clear": "yes", "target_group_clear": "yes", "access_clear": "yes", "contact_clear": "yes", "cost_clear": "yes", "service_content_clear": "yes"},
      "https://fosen-helse.no/tjenester/rask-psykisk-hjelp/",
      "Vi er et tilbud for innbyggere i Indre Fosen, Åfjord og Ørland. Man kan ta kontakt selv, det trengs ikke henvisning fra lege. ... Du er over 16 år ... Tilbudet er gratis.",
      "KVT-basert korttidsterapi; tlf 979 69 620, online bestilling, kontor i Brekstad. Side hentet via r.jina.ai (Cloudflare blokkerte direkte curl)."),
  svc("Psykisk helseteam for voksne (kommunalt)", "Voksne (kriterier listet på side)", True, True,
      ["DIRECT_PHONE", "GP_REFERRAL"], "MODERATE",
      {"age_clear": "no", "target_group_clear": "yes", "access_clear": "yes", "contact_clear": "no", "cost_clear": "yes", "service_content_clear": "yes"},
      "https://www.orland.kommune.no/vare-tjenester/helse-omsorg-og-sosiale-tjenester/psykisk-helse-og-rus/psykisk-helse/psykisk-helse-voksne/",
      "For å komme i kontakt med psykisk helseteam for voksne kan tjenesten kontaktes direkte eller fastlege kan henvise til oppfølging. ... Tjenesten er gratis."),
  svc("Ambulant ungdomsteam", "Barn og unge 10-20 år", True, False,
      ["UNCLEAR"], "BROAD",
      {"age_clear": "yes", "target_group_clear": "yes", "access_clear": "no", "contact_clear": "no", "cost_clear": "no", "service_content_clear": "yes"},
      "https://www.orland.kommune.no/vare-tjenester/helse-omsorg-og-sosiale-tjenester/psykisk-helse-og-rus/psykisk-helse/psykisk-helse-ungdom/",
      "Målgruppen for teamet er barn og unge mellom 10 til 20 år, hvor tjenestene familieterapi og ungdomslos er forsøkt uten at det har ført til ønsket endring.",
      "Steg 2-tilbud etter forsøkte lavere nivåer."),
  svc("Helsestasjon for ungdom", "Ungdom fra 13 år (ingen øvre grense publisert)", True, "unknown",
      ["UNCLEAR"], "MILD_MODERATE",
      {"age_clear": "yes", "target_group_clear": "yes", "access_clear": "no", "contact_clear": "no", "cost_clear": "yes", "service_content_clear": "yes"},
      "https://www.orland.kommune.no/vare-tjenester/helse-omsorg-og-sosiale-tjenester/lege-og-helsetjenester/helsestasjonen/helsestasjon-for-ungdom/",
      "Helsestasjon for ungdom (HFU) Gratis tilbud til ungdommer fra 13 år.",
      "Inngang (drop-in/time) ikke spesifisert på siden."),
 ],
 "intermunicipal": {
  "name": "Fosen Helse IKS (Indre Fosen, Åfjord, Ørland)",
  "role": "INTERMUNICIPAL_HOST for Rask psykisk helsehjelp",
  "source_url": "https://fosen-helse.no/tjenester/rask-psykisk-hjelp/"
 },
 "rph_status": "INTERMUNICIPAL RPH: Fosen Helse IKS RPH >16 år med selvhenvisning.",
 "notes": "Kontroll-kommune: forble CLEAR/MULTIPLE i V1; dyp kartlegging bekrefter med nytt funn (Fosen RPH)."
})

M.append({
 "kommunenummer": "5610", "kommune": "Osen", "ssb_sentralitetsklasse": 6,
 "search_log": dict(LOG),
 "gap_classification": V, "gap_classification_c_19": V, "gap_classification_d_22": V,
 "gap_classification_v1_c": "NO_MATCHING_LOCAL_SERVICE_FOUND",
 "gap_classification_v1_d": "NO_MATCHING_LOCAL_SERVICE_FOUND",
 "local_delivery_model": "MUNICIPAL",
 "services_18_23": [
  svc("Psykisk helse og rus (lavterskel)", "Mennesker i alle aldre", True, True,
      ["DIRECT_PHONE"], "BROAD",
      {"age_clear": "yes", "target_group_clear": "yes", "access_clear": "yes", "contact_clear": "yes", "cost_clear": "no", "service_content_clear": "yes"},
      "https://www.osen.kommune.no/vare-tjenester/helse-omsorg-og-sosiale-tjenester/helsetjenester/psykisk-helse-og-rus/",
      "Tjenesten er et lavterskeltilbud. Du trenger ikke henvisning for å ta kontakt. ... Det tilbys hjelp/støtte til mennesker i alle aldre. ... Ta direkte kontakt via telefon eller SMS: 48 88 52 12 ... hverdager mellom kl. 08:00 og 15:00.",
      "Støttesamtaler, veilednings- og oppfølgingssamtaler; psykiatrisk koordinator; Kommunehuset 3. etg."),
 ],
 "intermunicipal": None,
 "rph_status": "Ingen RPH dokumentert; kommunalt lavterskeltilbud dekker alle aldre.",
 "notes": "V1 NO_MATCH til tross for eksisterende tjenesteside - klassisk discovery-svikt, ikke tjenestehull."
})

M.append({
 "kommunenummer": "1432", "kommune": "Askvoll", "ssb_sentralitetsklasse": 6,
 "search_log": dict(LOG),
 "gap_classification": V, "gap_classification_c_19": V, "gap_classification_d_22": V,
 "gap_classification_v1_c": "LOCAL_ROUTING_UNCLEAR",
 "gap_classification_v1_d": "LOCAL_ROUTING_UNCLEAR",
 "local_delivery_model": "MUNICIPAL",
 "services_18_23": [
  svc("Psykisk helse- og rusteneste for vaksne", "Vaksne (ingen eksplisitt aldersgrense publisert)", True, True,
      ["DIRECT_PHONE"], "BROAD",
      {"age_clear": "no", "target_group_clear": "yes", "access_clear": "no", "contact_clear": "yes", "cost_clear": "yes", "service_content_clear": "yes"},
      "https://www.askvoll.kommune.no/tenestene-vare/helse-og-omsorg/psykisk-helse-og-rusteneste/psykisk-helse-og-rusteneste-for-vaksne/",
      "Psykisk helse- og rusteneste i Askvoll er ei teneste til deg som av ulike årsaker har det vanskeleg. ... Tilbodet er gratis og vi har teieplikt. ... Ved samtale, rettleie deg å meistre kvardagen",
      "Direkte kontakt via navngitte ansatte (psykisk helsearbeider 41 62 13 03, psykiatrisk sjukepleiar 93 06 64 23), kontor Sentrumsgarden. Inntakskriterier/inngangsprosessen ikke publisert."),
  svc("Helsestasjon for ungdom", "Ungdom 13-20 år", True, False,
      ["DIRECT_DROPIN"], "MILD_MODERATE",
      {"age_clear": "yes", "target_group_clear": "yes", "access_clear": "yes", "contact_clear": "no", "cost_clear": "yes", "service_content_clear": "yes"},
      "https://www.askvoll.kommune.no/tenestene-vare/helse-og-omsorg/born-og-familiar/helsestasjon/helsestasjon-for-ungdom/",
      "Helsestasjon for ungdom (HFU) er eit drop-in-tilbod for både gutar og jenter mellom 13 og 20 år ... Kvar tysdag mellom 14.00-15.30."),
 ],
 "intermunicipal": None,
 "rph_status": "Ingen RPH dokumentert; voksen-tenesten dekker.",
 "notes": "19-åring rutes til voksen-tenesten (direkte telefon); 22-åring likt. «Rask» hjelp er ikke eksplisitt lovet - valgt VERIFIED_LOCAL_ROUTE fordi tjeneste, kontakt og kostnad er dokumentert."
})

M.append({
 "kommunenummer": "4232", "kommune": "Bykle", "ssb_sentralitetsklasse": 6,
 "search_log": dict(LOG),
 "gap_classification": V, "gap_classification_c_19": V, "gap_classification_d_22": V,
 "gap_classification_v1_c": "NO_MATCHING_LOCAL_SERVICE_FOUND",
 "gap_classification_v1_d": "NO_MATCHING_LOCAL_SERVICE_FOUND",
 "local_delivery_model": "MUNICIPAL",
 "services_18_23": [
  svc("Psykisk helse og rus (tverrfagleg team)", "Barn, unge og vaksne med psykiske vanskar eller lidingar, samt rusproblem", True, True,
      ["DIRECT_PHONE"], "MILD_MODERATE",
      {"age_clear": "yes", "target_group_clear": "yes", "access_clear": "yes", "contact_clear": "yes", "cost_clear": "yes", "service_content_clear": "yes"},
      "https://www.bykle.kommune.no/tenester/helse-og-omsorg/helsetenesta-i-bykle-og-valle/psykisk-helse-og-familiestotte/",
      "Kven er tilbodet for: Barn, unge og vaksne med psykiske vanskar eller lidingar, samt rusproblem ... Samtaletilbod på inntil 8 samtalar i året ... Tilbodet er gratis. Tilvising: Alle kan tilvise til oss (til dømes leg[e])",
      "Tenestekoordinator Tone Avdal 986 76 933, kontortid 08-15.30. Korttidsgrense 8 samtaler; «rask» hjelp ikke eksplisitt lovet."),
  svc("Helsestasjon for ungdom (Bykle/Valle felles)", "Ungdom 13-25 år", True, True,
      ["DIRECT_PHONE"], "MILD_MODERATE",
      {"age_clear": "yes", "target_group_clear": "yes", "access_clear": "yes", "contact_clear": "yes", "cost_clear": "yes", "service_content_clear": "yes"},
      "https://www.bykle.kommune.no/tenester/helse-og-omsorg/helsetenesta-i-bykle-og-valle/helsestasjonen-og-skulehelsetenesta/",
      "Helsestasjon for ungdom (13-25 år): Timebestilling Valle HFU på telefon eller SMS til 915 87 989 Timebestilling Bykle HFU på telefon eller SMS til 948 13 245",
      "Felles tjeneste med Valle kommune."),
 ],
 "intermunicipal": {
  "name": "Bykle/Valle felles HFU",
  "role": "INTERMUNICIPAL_PARTNER (delt ungdomshelsestjeneste)",
  "source_url": "https://www.bykle.kommune.no/tenester/helse-og-omsorg/helsetenesta-i-bykle-og-valle/helsestasjonen-og-skulehelsetenesta/"
 },
 "rph_status": "Ingen RPH dokumentert.",
 "notes": "PHR er kommunal; HFU deles med Valle (registrert i intermunicipal-feltet)."
})

M.append({
 "kommunenummer": "5614", "kommune": "Hasvik", "ssb_sentralitetsklasse": 6,
 "search_log": dict(LOG),
 "gap_classification": V, "gap_classification_c_19": V, "gap_classification_d_22": V,
 "gap_classification_v1_c": "CLEAR_LOCAL_ROUTE",
 "gap_classification_v1_d": "CLEAR_LOCAL_ROUTE",
 "local_delivery_model": "MUNICIPAL",
 "services_18_23": [
  svc("FFR - Rus og psykisk helse (lavterskel)", "Ingen aldersgrense publisert", True, True,
      ["DIRECT_PHONE"], "BROAD",
      {"age_clear": "no", "target_group_clear": "yes", "access_clear": "yes", "contact_clear": "yes", "cost_clear": "no", "service_content_clear": "yes"},
      "https://hasvik.kommune.no/tjenester/helse-og-omsorg/helsetjenester/rus-og-psykiatri/psykisk-helse",
      "Familie, forebygging og rehabilitering (FFR) i Hasvik kommune tilbyr oppfølging av mennesker som har utfordringer knyttet til psykiske helse og rus. Tjenesten er et lavterskeltilbud ... kan ta kontakt direkte. Oppfølgingen ... kan bestå av: Samtaler Miljøarbeid Turer Klubb Trening ... Botrening",
      "FFR-avdeling tlf 78 45 25 59 (kontaktblokk på helsestasjon-siden). Eldre FFR-detaljside (hasvik2019.custompublish.com) er ikke lenger tilgjengelig."),
  svc("Helsesykepleier (helsestasjon/skolehelsetjeneste)", "Barn og unge 0-20 år", True, False,
      ["OTHER_PROFESSIONAL"], "MILD",
      {"age_clear": "yes", "target_group_clear": "yes", "access_clear": "no", "contact_clear": "yes", "cost_clear": "yes", "service_content_clear": "yes"},
      "https://hasvik.kommune.no/tjenester/helse-og-omsorg/helsestasjon",
      "Helsesykepleier Jobber med barn og unge i alderen 0-20 år.",
      "Skolehelsetjenesten: samtaler med elever, henvise videre ved behov."),
 ],
 "intermunicipal": None,
 "rph_status": "Ingen RPH dokumentert; FFR lavterskeltilbud dekker.",
 "notes": "Kontroll-kommune forble clear. Nyhet 2026-09-01: «Nytt lavterskeltilbud for barn og unge i Hasvik» (oppstart informeres fortløpende) - relevant for under-20, ikke brukt som bevis for 18-23."
})

json.dump(M, open("data/18-23-routing-deep-a.json", "w"), ensure_ascii=False, indent=1)
print(f"wrote data/18-23-routing-deep-a.json with {len(M)} municipalities")
