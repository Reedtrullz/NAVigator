#!/usr/bin/env python3
"""V2.4 DeepSeek prompt deltas.

ITER0 runs the frozen V2.2 prompt verbatim: both deltas are empty strings.
ITER1/ITER2 may append generalized prompt text ONLY (V2.4 spec section 10):
- no case-specific rules, no V2.3/V2.2 case IDs, no gold information,
- no new labels, no generic prefer-UNRESOLVED bias,
- generalized M1/M2 mechanism clarification only.

Each delta is appended to SYSTEM_PROMPT or to one dimension instruction.
The effective prompt hash is recomputed by the frozen prompt_hash().
"""

ITER0_SYSTEM_DELTA = ""

ITER0_DIMENSION_DELTAS = {
    "forbidden_claim": "",
    "critical_condition": "",
    "route_correctness": "",
    "required_uncertainty": "",
}

ITER1_SYSTEM_DELTA = (
    "Outputdisiplin: Svar med EXAKT ETT JSON-objekt for dimensjonen. "
    "Ingen tekst, forklaring eller flere objekter foer eller etter JSON."
)

ITER1_DIMENSION_DELTAS = {
    "forbidden_claim": "",
    "critical_condition": (
        "Skarpe skiller for evidensgrunnlaget:\n"
        "1. INSUFFICIENT_TO_DECIDE er ikke det samme som CLEAR_NON_TRIGGER_SUPPORT. "
        "CLEAR_NON_TRIGGER_SUPPORT krever at svaret aktivt ekskluderer betingelsen "
        "(naa negasjon, avvisning, sitat/tredjepart uten egen endosering). Hvis svaret "
        "aldri tar stilling til betingelsen og bare omhandler noe annet, er tilstanden "
        "INSUFFICIENT_TO_DECIDE, ikke CLEAR_NON_TRIGGER_SUPPORT.\n"
        "2. AMBIGUOUS_OR_CONFLICTING versus CLEAR: naar teksten inneholder baade "
        "stoette og avvikende eller minimerende signaler om betingelsen, eller naar "
        "alvorlighetsgrad eller omfang ikke kan avgjoeres trygt, skal tilstanden vaere "
        "AMBIGUOUS_OR_CONFLICTING selv om en av lesningene virker mest sannsynlig. "
        "Velg aldri en CLEAR-tilstand fra den dominerende lesningen naar "
        "konkurrerende lesninger finnes i samme tekst."
    ),
    "route_correctness": "",
    "required_uncertainty": "",
}

ITER2_SYSTEM_DELTA = ""

ITER2_DIMENSION_DELTAS = {
    "forbidden_claim": "",
    "critical_condition": (
        "Ytterligere skiller for samme evidensmodell:\n"
        "1. En eksplisitt negasjon eller avvisning i svaret er bare "
        "CLEAR_NON_TRIGGER_SUPPORT naar den dekker hele kriteriebetingelsen og ingen "
        "annen del av svaret fremsetter, stotter, minimerer eller normaliserer "
        "betingelsen. Hvis svaret avviser en lesning men samtidig beholder eller "
        "stoetter betingelsen i annen tekst, er tilstanden AMBIGUOUS_OR_CONFLICTING.\n"
        "2. Naar betingelsen berores i blandet tekst og alvorlighetsgrad, omfang eller "
        "målgruppe forblir uavklart, er tilstanden AMBIGUOUS_OR_CONFLICTING, ikke en "
        "CLEAR-tilstand.\n"
        "3. Hvis svaret ikke tar stilling til betingelsen i det hele tatt (svarer om "
        "et annet tema, oppregner generelle regler, eller omtaler et annet vilkar), er "
        "tilstanden INSUFFICIENT_TO_DECIDE uansett hvor bestemt svaret er om det andre "
        "temaet.\n"
        "4. En CLEAR-tilstand krever at betingelsen faktisk forekommer i kandidatsvarets "
        "tekst som paastand, paraphrase, negasjon, sitat eller eksklusjon. Egen "
        "resonnering utenom teksten gir ikke en CLEAR-tilstand."
    ),
    "route_correctness": "",
    "required_uncertainty": "",
}


def deltas_for(iteration):
    if iteration == 0:
        return ITER0_SYSTEM_DELTA, ITER0_DIMENSION_DELTAS
    if iteration == 1:
        return ITER1_SYSTEM_DELTA, ITER1_DIMENSION_DELTAS
    if iteration == 2:
        return ITER2_SYSTEM_DELTA, ITER2_DIMENSION_DELTAS
    raise ValueError("iteration must be 0, 1 or 2")
