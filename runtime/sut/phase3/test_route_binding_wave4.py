"""W4-RC-A route-target and binding tests (spec sections 8-18).

Generic mechanism coverage only: no case IDs, no burned-corpus strings.
Heading fixtures use temp source docs so the verbatim-line rescue path
is exercised against the real file read.
"""

import os
import tempfile
import unittest

from sut.context import make_context
from sut.phase2.pipeline import (
    s6_route_reasoning,
    s7_evidence_aggregation,
    s8_epistemic_assignment,
)
from sut.phase2.routes import build_national_route_candidates
from sut.phase3.finalize import finalize
from sut.phase3.planner import s9_answer_planning


_FASTLEGE_ROW = (
    "| Fastlege | Somatisk og psykisk grunnvurdering | Direkte time |")


def _rec(claim, evidence_id="E-D001", domain="mental_health",
         path=None, source_type="PROJECT_RESEARCH", gap_state=None,
         historical_research=False):
    return {
        "record_id": "K-D001",
        "source_type": source_type,
        "domain": domain,
        "track_domain": domain,
        "claim": claim,
        "source_reference": {"kind": "REPO_DOC", "path": path},
        "authority": "INTERNAL_DOC",
        "freshness": "CURRENT",
        "evidence_id": evidence_id,
        "gap_state": gap_state,
        "historical_research": historical_research,
    }


class _HeadingDocMixin(unittest.TestCase):
    """Writes a temp source doc and returns records anchored to it."""

    DOC = None

    def _doc_records(self, claims, **rec_kwargs):
        fd, tmp_path = tempfile.mkstemp(suffix=".md")
        self.addCleanup(os.remove, tmp_path)
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(self.DOC)
        return [_rec(claim, path=tmp_path, **rec_kwargs) for claim in claims]


class TestHeadingRescue(_HeadingDocMixin):
    DOC = (
        "# Kommuneoversikt\n"
        "\n"
        "## Skolehelsetjenesten\n"
        "Trivsel, psykososial stott og viderehenvisning ved behov.\n"
        "\n"
        "## Helsestasjon 0-5 ar\n"
        "Innkalte kontroller og drop-in.\n"
        "\n"
        "## Rask psykisk helsehjelp (verifisert)\n"
        "Kommunen tilbyr konsultasjoner for voksne.\n"
        "\n"
        "## PPT\n"
        "Sakkyndig vurdering for spesialpedagogikk.\n"
        "\n"
        "## Barn kan motta samtaler\n"
        "Det arrangeres samtalegrupper i helgene.\n"
        "\n"
        "## Kilder og metode\n"
        "Prosjektinternen dokumentasjon ligger i repositoriet.\n"
        "\n"
        "## Akutt fare for liv og helse\n"
        "Ring 113 ved umiddelbar fare.\n"
        "\n"
        "## NAV\n"
        "Okonomisk stotte via NAV-kontoret.\n"
    )

    def test_heading_is_the_service_name(self):
        routes = build_national_route_candidates(
            self._doc_records(
                ["Trivsel, psykososial stott og viderehenvisning ved behov."]))
        self.assertEqual(len(routes), 1)
        self.assertEqual(routes[0]["service_type"], "Skolehelsetjenesten")
        self.assertEqual(routes[0]["scope"], "NATIONAL")

    def test_heading_with_digits_accepted(self):
        routes = build_national_route_candidates(
            self._doc_records(["Innkalte kontroller og drop-in."]))
        self.assertEqual(len(routes), 1)
        self.assertEqual(routes[0]["service_type"], "Helsestasjon 0-5 ar")

    def test_heading_suffix_and_prefix_stripped(self):
        routes = build_national_route_candidates(
            self._doc_records(["Kommunen tilbyr konsultasjoner for voksne."]))
        self.assertEqual(len(routes), 1)
        self.assertEqual(routes[0]["service_type"],
                         "Rask psykisk helsehjelp")

    def test_resolved_service_acronym_heading(self):
        routes = build_national_route_candidates(
            self._doc_records(["Sakkyndig vurdering for spesialpedagogikk."]))
        self.assertEqual(len(routes), 1)
        self.assertEqual(routes[0]["service_type"], "PPT")

    def test_sentence_fragment_heading_rejected(self):
        routes = build_national_route_candidates(
            self._doc_records(["Det arrangeres samtalegrupper i helgene."]))
        self.assertEqual(routes, [])

    def test_marker_heading_rejected(self):
        routes = build_national_route_candidates(
            self._doc_records(
                ["Prosjektinternen dokumentasjon ligger i repositoriet."]))
        self.assertEqual(routes, [])

    def test_sentence_start_heading_rejected(self):
        routes = build_national_route_candidates(
            self._doc_records(["Ring 113 ved umiddelbar fare."]))
        self.assertEqual(routes, [])

    def test_unresolved_acronym_heading_rejected(self):
        routes = build_national_route_candidates(
            self._doc_records(["Okonomisk stotte via NAV-kontoret."]))
        self.assertEqual(routes, [])

    def test_ambiguous_claim_line_rejected(self):
        self.DOC = (
            "## Tjeneste A\n"
            "Felleslinje med samme tekst.\n"
            "\n"
            "## Tjeneste B\n"
            "Felleslinje med samme tekst.\n"
        )
        doc = (
            "## Tjeneste A\n"
            "Felleslinje med samme tekst.\n"
            "\n"
            "## Tjeneste B\n"
            "Felleslinje med samme tekst.\n"
        )
        routes = build_national_route_candidates(
            self._doc_records(["Felleslinje med samme tekst."]))
        self.assertEqual(routes, [])


class TestQuotedAndAcronymGates(unittest.TestCase):
    def test_quoted_service_accepted(self):
        routes = build_national_route_candidates(
            [_rec("Kontakt 'BUP' ved alvorlige vansker.")])
        self.assertEqual(len(routes), 1)
        self.assertEqual(routes[0]["service_type"], "BUP")

    def test_quoted_sentence_fragment_rejected(self):
        routes = build_national_route_candidates(
            [_rec("Vilkaret er at 'Barn kan motta samtaler' i tilbudet.")])
        self.assertEqual(routes, [])

    def test_quoted_meta_identifier_rejected(self):
        routes = build_national_route_candidates(
            [_rec("Se 'NAV' for okonomisk stotte.")])
        self.assertEqual(routes, [])

    def test_quoted_url_rejected(self):
        routes = build_national_route_candidates(
            [_rec("Informasjon fra 'URL' bekrefter tilbudet.")])
        self.assertEqual(routes, [])

    def test_quoted_sentence_starter_rejected(self):
        routes = build_national_route_candidates(
            [_rec("Regelen gjelder nar 'Akutt fare' er til stede.")])
        self.assertEqual(routes, [])

    def test_quoted_digits_rejected(self):
        routes = build_national_route_candidates(
            [_rec("Se 'Helsestasjon 0-5 ar' for kontroller.")])
        self.assertEqual(routes, [])


def _service(name, source_url, **extra):
    svc = {"name": name, "source_url": source_url,
           "access_methods": ["phone"], "target_group": "voksne",
           "strong_access": False, "age_eligible": None}
    svc.update(extra)
    return svc


def _discovery(services, evidence=None):
    if evidence is None:
        evidence = [{"kind": "municipal_page",
                     "source_url": s["source_url"]} for s in services]
    return {"track_id": "T1", "domain": "mental_health",
            "step": {"state": "COMPLETED", "evidence": evidence,
                     "services": services}}


class TestEvidenceBinding(unittest.TestCase):
    def _routes(self, steps, records=None):
        ctx = make_context({
            "case_id": "W4TEST",
            "user_query": "Hvor kan vi fa hjelp?",
            "profile": {"age": 17},
            "context": {},
            "location_context": {"municipality": "Drammen"},
            "timestamp_context": {"executed_at": "2026-09-17T10:00:00Z"},
        })
        ctx["safety"] = {"priority": "NOT_ACUTE", "signals": [],
                         "suppressed_routing": False}
        ctx["_config"] = {
            "knowledge_index_path": "data/knowledge-index-v1.json",
            "rules_registry_path": "data/rules-v1.json",
            "safety_rules_path": "data/safety-triage-rules-v2.json",
        }
        ctx["_s4_records"] = records or []
        ctx["_s5_steps"] = steps
        ctx["tracks"] = [{"track_id": "T1", "domain": "mental_health",
                          "sub_utterance": ctx["input"]["user_query"],
                          "status": "PENDING",
                          "needs_local_discovery": False}]
        ctx["_s5_incomplete"] = False
        s6_route_reasoning(ctx)
        s7_evidence_aggregation(ctx)
        s8_epistemic_assignment(ctx)
        s9_answer_planning(ctx)
        return ctx, finalize(ctx)

    def test_per_service_evidence_partition(self):
        ev = [{"kind": "municipal_page",
               "source_url": "https://a.kommune.example/bup"},
              {"kind": "municipal_page",
               "source_url": "https://a.kommune.example/skole"}]
        steps = [_discovery(
            [_service("BUP", "https://a.kommune.example/bup"),
             _service("Skolehelsetjenesten",
                      "https://a.kommune.example/skole")],
            evidence=ev)]
        ctx, out = self._routes(steps)
        by_id = {r["route_id"]: r for r in out["evidence"]["structured_routes"]}
        self.assertEqual(
            next(r for r in by_id.values()
                 if r["service_identity"] == "BUP")["evidence_refs"],
            ["E-DISC-01"])
        self.assertEqual(
            next(r for r in by_id.values()
                 if r["service_identity"] == "Skolehelsetjenesten")
            ["evidence_refs"],
            ["E-DISC-02"])

    def test_binding_helper_falls_back_to_all_refs(self):
        from sut.phase2.routes import _bind_discovery_evidence
        svc = {"name": "BUP", "source_url": None}
        disc = {"evidence": [{"kind": "municipal_page"}]}
        self.assertEqual(_bind_discovery_evidence(svc, disc), ["E-DISC-01"])

    def test_structured_routes_survive_serialization(self):
        # Real frozen doc row: identity table mints Fastlege, and the
        # structured object must survive finalize serialization.
        doc = "26-beslutningsstotte-hvor-henvende-seg.md"
        row = open(doc, encoding="utf-8").read().splitlines()[13]
        records = [_rec(row, path=doc)]
        ctx, out = self._routes([], records=records)
        structured = out["evidence"]["structured_routes"]
        self.assertEqual(len(structured), 1)
        entry = structured[0]
        for field in ("route_id", "service_identity", "display_label",
                      "track_domain", "route_state", "access_model",
                      "self_referral", "target_population", "scope",
                      "evidence_refs", "provenance_refs", "dims"):
            self.assertIn(field, entry)
        self.assertEqual(entry["service_identity"], "Fastlege")
        self.assertEqual(entry["display_label"], "Fastlege")
        self.assertEqual(entry["track_domain"], "mental_health")
        self.assertIn("Fastlege", out["routes"])
        self.assertEqual(out["routes"], [r["display_label"]
                                         for r in structured])
        self.assertEqual(entry["evidence_refs"],
                         out["evidence"]["route_evidence"]
                         [entry["route_id"]]["evidence_ids"])

    def test_no_route_yields_empty_structured_routes(self):
        ctx, out = self._routes([])
        self.assertEqual(out["evidence"]["structured_routes"], [])
        self.assertTrue(out["no_route_asserted"])


if __name__ == "__main__":
    unittest.main()
