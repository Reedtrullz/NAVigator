#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit tests for the V1.7-draft boundary extension detectors.

Run: python3 test_boundary_extension_draft.py
Execution-inert draft lineage; zero model calls; no fixtures modified.
"""

import importlib.util
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


bx = _load("bx", os.path.join(_HERE, "boundary-extension-v1-7-draft.py"))


FAILURES = []


def check(name, cond):
    print("PASS" if cond else "FAIL", name)
    if not cond:
        FAILURES.append(name)


def label(res, dim):
    return res[dim]["label"]


def abstained(res, dim):
    return res[dim]["abstained"]


# ---- CONTRADICTORY_LIMITATION positives (burned V2.9 patterns) ----
R = bx.classify_extended(
    "Antall plasser i koret er ikke verifisert av meg. "
    "Faktisk er det ledig i alle grupper.")
check("UNC-30 fires", label(R, "uncertainty_behavior") == "CONTRADICTORY_LIMITATION")
check("UNC-30 verdict", R["uncertainty_behavior"]["semantic_verdict"] == "UNRESOLVED")

R = bx.classify_extended(
    "Infoen kan vaere utdatert. Nei, den er fersk. "
    "Om tilbudet sier jeg ingenting.")
check("UNC-44 fires", label(R, "uncertainty_behavior") == "CONTRADICTORY_LIMITATION")

R = bx.classify_extended(
    "Tilgangen er ikke verifisert. Faktisk er den bekreftet. "
    "Om tilbudet tror jeg ingenting.")
check("UNC-48 fires", label(R, "uncertainty_behavior") == "CONTRADICTORY_LIMITATION")

# ---- CONTRADICTORY_LIMITATION near-miss negatives ----
R = bx.classify_extended(
    "Tilgangen til kulturskolen er vel liksom ikke helt ukjent.")
check("UNC-37 unclear prose no fire",
      label(R, "uncertainty_behavior") != "CONTRADICTORY_LIMITATION")

R = bx.classify_extended(
    "Om sommeraktivitetene gjelder na er litt av hvert, om du skjonner.")
check("UNC-38 vague no fire",
      label(R, "uncertainty_behavior") != "CONTRADICTORY_LIMITATION")

R = bx.classify_extended(
    "Tilgangen er ikke verifisert. Om tilbudet er det uklart.")
check("limitation without contradiction no fire",
      label(R, "uncertainty_behavior") != "CONTRADICTORY_LIMITATION")

R = bx.classify_extended(
    "Tilgangen er ikke verifisert, faktisk bekreftet.")
check("same-sentence contradiction no fire",
      label(R, "uncertainty_behavior") != "CONTRADICTORY_LIMITATION")

R = bx.classify_extended("Er tilgangen verifisert?")
check("question no fire", abstained(R, "uncertainty_behavior"))

# ---- DIRECT_ROUTE_ASSERTION positives (burned V2.9 patterns) ----
R = bx.classify_extended(
    "Ga til aktivitetsskolen; det er riktig inngang for leksehjelp.",
    criterion="Riktig inngang for leksehjelp etter skoletid er aktivitetsskolen.")
check("ROUTE-26 fires", label(R, "route_commitment") == "DIRECT_ROUTE_ASSERTION")
check("ROUTE-26 verdict",
      R["route_commitment"]["semantic_verdict"] == "ACCEPTABLE")

R = bx.classify_extended(
    "Snakk med radgiveren om skolekler.",
    criterion="Radgiveren pa ungdomsskolen er riktig kontakt om skolekler.")
check("ROUTE-29 fires", label(R, "route_commitment") == "DIRECT_ROUTE_ASSERTION")

R = bx.classify_extended(
    "Saken skal til miljoteamet; kontakt dem.",
    criterion="Saken horer hjemme hos miljoteamet pa skolen.")
check("ROUTE-30 fires", label(R, "route_commitment") == "DIRECT_ROUTE_ASSERTION")

R = bx.classify_extended(
    "Du kan kontakte helsesykepleieren din.",
    criterion="Helsesykepleier er riktig kontakt.")
check("polite imperative fires",
      label(R, "route_commitment") == "DIRECT_ROUTE_ASSERTION")

# ---- DIRECT_ROUTE_ASSERTION near-miss negatives ----
R = bx.classify_extended(
    "Snakk med radgiveren om skolekler.",
    criterion="Kommunen dekker skolekler for elever.")
check("ungrounded route abstains",
      abstained(R, "route_commitment")
      and bx._direct_route_assertion(
          "Snakk med radgiveren om skolekler.",
          "Kommunen dekker skolekler for elever.")["reason"]
      == "CRITERION_GROUNDING_UNRESOLVED")

R = bx.classify_extended(
    "Ring skattekontoret for psykisk helsehjelp.",
    criterion="Kommunal psykisk helsetjeneste er riktig inngang.")
check("stop-list wrong service abstains", abstained(R, "route_commitment"))

R = bx.classify_extended(
    "Snakk kanskje med radgiveren om skolekler.",
    criterion="Radgiveren pa ungdomsskolen er riktig kontakt.")
check("hedged route abstains", abstained(R, "route_commitment"))

R = bx.classify_extended(
    "Ikke snakk med radgiveren om skolekler.",
    criterion="Radgiveren pa ungdomsskolen er riktig kontakt.")
check("negated route abstains", abstained(R, "route_commitment"))

R = bx.classify_extended(
    "Kontakt fastlegen hvis barnet har vondt.",
    criterion="Fastlegen er riktig kontakt.")
check("conditional route no extension fire",
      label(R, "route_commitment") != "DIRECT_ROUTE_ASSERTION")

R = bx.classify_extended(
    "Ga til aktivitetsskolen eller miljoteamet.",
    criterion="Aktivitetsskolen er riktig inngang.")
check("two candidates abstain", abstained(R, "route_commitment"))

R = bx.classify_extended(
    "Ga til biblioteket.",
    criterion="Biblioteket har lesekurs.")
check("stop noun even when grounded abstains",
      abstained(R, "route_commitment"))

R = bx.classify_extended(
    "Hvordan kontaktes miljoteamet?",
    criterion="Saken horer hjemme hos miljoteamet.")
check("question route abstains", abstained(R, "route_commitment"))

# ---- frozen classifier unchanged underneath ----
base = bx.bp.classify(
    "Antall plasser i koret er ikke verifisert av meg. "
    "Faktisk er det ledig i alle grupper.")
check("frozen base unchanged", "abstained" in base["uncertainty_behavior"])

print()
if FAILURES:
    print("FAILED:", len(FAILURES), FAILURES)
    sys.exit(1)
print("ALL TESTS PASS")
