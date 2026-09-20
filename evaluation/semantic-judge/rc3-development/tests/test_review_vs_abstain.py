"""Review-vs-abstain suite (spec 12, 36-37): 16 synthetic, non-V4
cases. 8 genuinely insufficient (unrelated evidence) must abstain;
8 relevant-but-unresolved (same topic, no bounded proof) must review.
Drives the frozen routing table only - no reviewer, no labels."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "rc3_engine"))
import routing as rt

# (claim, source, expected_route)
ABSTAIN = [
    ("Kommunen gir oekonomisk radgivning pa tirsdager.",
     "Skolen har ansvar for PPT-vurdering av elever."),
    ("BUP gir диagnostisk utredning av ADHD.",
     "Barnetrygd utbetales den 20. hver maaned."),
    ("Helsestasjonen tilbyr vaksinasjon av barn.",
     "Renovasjon hentes hverandre tirsdag i boligfeltet."),
    ("Familievernkontoret tilbyr mekling ved samlivsbrudd.",
     "Kommunens svimmehall holder apent fra 1. juni."),
    ("Overgangsstonad gis til enslig forsorger.",
     "Vannmalestandarden krever installasjon av vannmaaler."),
    ("Barnevernvakta har dognvakt hele aret.",
     "Byggekode krever soknad for tilbygg over 15 kvadratmeter."),
    ("PPT gir radgivning til skolen.",
     "Renovasjonskostnaden faktureres kvartalsvis."),
    ("Fastlegen henviser til BUP.",
     "Gronnparken stenges for vedlikehold i juli."),
]

REVIEW = [
    ("Kommunen gir oekonomisk radgivning.",
     "Kommunen gir oekonomisk radgivning i begrenset omfang."),
    ("PPT utreder barnets vansker.",
     "PPT vurderer behov for tilrettelegging i skolen."),
    ("BUP gir behandling til barn og unge.",
     "BUP mottar henvisninger og vurderer behovet for utredning."),
    ("Helsestasjon for ungdom er gratis.",
     "Helsestasjon for ungdom tilbyr ravgivning opptil 20 ar."),
    ("Familievernkontoret krever henvisning.",
     "Familievernkontoret kan kontaktes direkte av familier."),
    ("Barnevernet kan gi stotte uten samtykke.",
     "Stottetiltak fra barnevernet bygges vanligvis pa samtykke."),
    ("Skolehelsetjenesten undersoker elever.",
     "Skolehelsetjenesten yter helsefremmende og forebyggende tjenester."),
    ("Overgangsstonad varer i tre ar.",
     "Overgangsstonad gis en begrenset periode avhengig av barnets alder."),
]


def test():
    wrong = []
    for claim, src in ABSTAIN:
        out = rt.route_atom({"proof_state": "ENGINE_NO_PROOF"}, claim, src)
        if out != "ABSTAIN_INSUFFICIENT":
            wrong.append((claim[:35], "ABSTAIN", out))
    for claim, src in REVIEW:
        out = rt.route_atom({"proof_state": "ENGINE_NO_PROOF"}, claim, src)
        if out != "REVIEW_REQUIRED":
            wrong.append((claim[:35], "REVIEW", out))
    n = len(ABSTAIN) + len(REVIEW)
    assert not wrong, "routing mismatches: %s" % wrong
    return n


if __name__ == "__main__":
    n = test()
    print("review-vs-abstain suite: %d/%d PASS" % (n, n))

