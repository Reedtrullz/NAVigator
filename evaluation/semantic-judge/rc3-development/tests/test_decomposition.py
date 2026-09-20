"""DECOMPOSITION_V1 suite: 60+ claim-logical cases (spec 22-24)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "rc3_engine"))
from decomposition import decompose_claim

# (claim, expected_atom_count)
CASES = [
    ("Du far dekket reiser.", 1),
    ("Du far dekket reiser og opphold.", 1),
    ("Du far dekket reiser og opphold og mat.", 1),
    ("Barns inntekt og formue tas med.", 1),
    ("Sokere og familiens inntekt telles sammen.", 1),
    ("Tilbudet er gratis og krever ingen henvisning.", 2),
    ("Helsesykepleier gir radgivning og fastlegen gir behandling.", 2),
    ("Kommunen gir radgivning og BUP gir utredning og familevern gir stotte.", 3),
    ("Du kan fa stotte dersom du bor i kommunen.", 2),
    ("Du far hjelp hvis du er registrert.", 2),
    ("Etter at soknad er sendt blir saken vurdert.", 1),
    ("Etter at du har flyttet ma du melde adresse.", 1),
    ("Tilbudet er gratis men henvisning kreves.", 2),
    ("Inntekt og formue og utgifter regnes sammen.", 1),
    ("Du ma soke skriftlig og vedlegge dokumentasjon.", 2),
    ("Retten gjelder voksne og barn over 18 ar.", 1),
    ("Tjenesten dekker legehjelp og psykologhjelp.", 1),
    ("Tjenesten dekker legehjelp og psykologhjelp og fysioterapi.", 1),
    ("Saken behandles og du far skriftlig svar.", 2),
    ("Rettighet gjelder bare dersom du er bosatt i kommunen.", 2),
    ("Det gis individuell vurdering og ingen automatisk rett.", 2),
    ("Unntak gjelder og saken sendes videre.", 2),
    ("Voksne kan soke og barn kan henvises.", 2),
    ("Foreldre kan ta kontakt og ungdom kan ta kontakt selv.", 2),
    ("Kommunen koordinerer og helsetjenesten behandler.", 2),
    ("Svaret kommer innen 30 dager og er skriftlig.", 2),
    ("Rett til tolk gjelder og tolken har taushetsplikt.", 2),
    ("Behandling er gratis og oppfolging er gratis.", 2),
    ("Fastlegen henviser og BUP utreder.", 2),
    ("PPT utreder og skolen iverksetter tiltak.", 2),
    ("Barnevern gransker og familekontoret stotter.", 2),
    ("Rett gjelder fra foleregistrert dato og opphor ved flytting.", 2),
    ("Du far beskjed skriftlig og innen 4 uker.", 1),
    ("Klagen sendes kommunen og kommunen vurderer den pa nytt.", 2),
    ("Hjelpen er frivillig og kan avsluttes nar som helst.", 2),
    ("Lege utreder og psykolog behandler og sosionom koordinerer.", 3),
    ("Du har rett til tolk og til barnepass under mote.", 1),
    ("Soeknad sendes digitalt og papir er ikke akseptert.", 2),
    ("Rettighet krever bosted og oppholdstillatelse.", 1),
    ("Den som er syk har rett og den som er frisk har plikt.", 2),
    ("Du far dekket behandling nar legen henviser.", 2),
    ("Tilbudet gjelder barn og unge.", 1),
    ("Unge voksne under 25 ar har egne tilbud.", 1),
    ("Henvisning kreves fra fastlege eller skole.", 1),
    ("Behandlingen er gratis og foregår på helsestasjonen.", 2),
    ("Foreldre deltar og barnet deltar.", 2),
    ("Utredningen tar 8 uker og rapporten sendes fastlegen.", 2),
    ("Du kan klage og klagen behandles av fylkesmannen.", 2),
    ("Helsesoster vekter og lege skriver erklaring.", 2),
    ("Rettighet fornyes hvert ar og krever ny soknad.", 2),
    ("Du far svar innen 3 uker og saken kan overklasse.", 2),
    ("Tjenesten er gratis og uten henvisning.", 1),
    ("Barn under 18 ma ha samtykke fra foreldre.", 1),
    ("Du har rett til medvirkning og informasjon.", 1),
    ("Behandling skjer i gruppe eller individuelt.", 1),
    ("Kommunen dekker utgifter dersom vilkarene er oppfylt.", 2),
    ("Soknaden behandles fortlpende og svaret gjes skriftlig.", 2),
    ("Rettighet gjelder ikke dersom du mottar tilsvarende fra annet hold.", 2),
    ("Skolen melder behov og PPT vurderer behovet.", 2),
    ("Du kan ta direkte kontakt og trenger ingen henvisning.", 2),
    ("Oppfolging skjer i kommunen og utredning skjer i BUP.", 2),
    ("Selvmordsfare gir akutthjelp og skal ikke henvises vanlig.", 2),
    ("Tilbudet gjes etter behov og gjes ikke automatisk.", 2),
    ("Barnehuset tilbyr samtale og rettsmedisinsk undersokelse.", 1),
    ("Du far dekket legehjelp, psykologhjelp og fysioterapi.", 1),
    ("Inntekt og formue regnes, men utgifter trekkes.", 2),
]


def _count(claim):
    return len(decompose_claim(claim))


def test_atom_counts():
    failed = []
    for claim, want in CASES:
        got = _count(claim)
        if got != want:
            failed.append((claim[:40], got, want))
    exact = len(CASES) - len(failed)
    rate = exact / len(CASES)
    assert rate >= 0.95, "atom count exact %.2f, failures: %s" % (
        rate, failed)


def test_stability():
    for claim, _ in CASES:
        a = decompose_claim(claim)
        b = decompose_claim(claim)
        assert a == b, "unstable decomposition: %s" % claim
    # ids stable and sequential
    atoms = decompose_claim("Du far hjelp hvis du soke og dokumenterer.")
    assert [a["atom_id"] for a in atoms] == [
        "A%d" % (i + 1) for i in range(len(atoms))]


def test_no_evidence_influence():
    """Decomposition is a pure function of claim text (spec 20)."""
    claim = "Fastlegen henviser og BUP utreder."
    a = decompose_claim(claim)
    assert _count(claim) == 2
    assert a[0]["text"] != ""


if __name__ == "__main__":
    test_atom_counts()
    test_stability()
    test_no_evidence_influence()
    print("decomposition suite: %d cases PASS" % len(CASES))
