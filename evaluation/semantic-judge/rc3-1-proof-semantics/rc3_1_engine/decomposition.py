"""Canonical claim decomposition (deterministic, claim-logical)."""
import re

VERB_START = {
    "er", "har", "kan", "skal", "ma", "krever", "gir", "tar", "utbetales",
    "varer", "gjelder", "tilbyr", "yter", "passer", "overgar", "gis",
    "soker", "mote", "vaere", "vil", "blir", "far", "lager", "fastsettes",
    "omfatter", "dekker", "retter", "utgjor", "betaler", "stiller",
    "skriver", "utarbeider", "utreder", "bidrar", "setter", "motes",
    "erstattes", "kvalifisere", "samtykker", "soker",
    "mottar", "motta",
    "sette", "lager", "utbetales", "betalings", "oppnas",
}
DET_START = {"egen", "eget", "egne", "sin", "sitt", "si", "sine", "deres",
             "denne", "dette"}
AUX = {"ma", "skal", "kan", "vil", "ha", "har", "far", "blir", "vaere"}
PRONOUN_START = {"den", "det", "dette", "de"}
SUBORD = {"hvis", "nar", "dersom"}


def _first_verb_index(tokens):
    for i, t in enumerate(tokens):
        if t in VERB_START:
            return i
    return None


def _subject_of(part):
    tl = part.split()
    vi = _first_verb_index(tl)
    if vi is None or vi == 0:
        return None
    return " ".join(tl[:vi])


def _carryover(first_part, second_part):
    st = _subject_of(first_part)
    words = second_part.split()
    if not words or not st:
        return second_part
    w0 = words[0]
    if w0 in PRONOUN_START:
        return second_part
    if w0 in DET_START:
        tl = first_part.split()
        vi = _first_verb_index(tl)
        aux = [t for t in tl[vi:vi + 3] if t in AUX]
        return " ".join([st] + aux + words)
    if w0 in VERB_START or w0 in AUX:
        return st + " " + second_part
    return second_part


def _split_shared_subject(part):
    """Split 'X ... og <verb-start/det-start> ...' into atoms."""
    if any(" " + w + " " in " " + part + " " for w in SUBORD):
        return [part]
    out = [part]
    changed = True
    while changed:
        changed = False
        for idx, p in enumerate(out):
            for m in re.finditer(r"\s+og\s+", p):
                nxt = p[m.end():].split()
                if nxt and (nxt[0] in VERB_START or nxt[0] in AUX or nxt[0] in DET_START or nxt[0] in PRONOUN_START):
                    a, b = p[:m.start()].strip(), p[m.end():].strip()
                    out[idx:idx + 1] = [a, _carryover(a, b)]
                    changed = True
                    break
            if changed:
                break
    return out


def decompose_claim(claim):
    """Return ordered atom texts; same input always gives same output."""
    claim = claim.strip().rstrip(".")
    # 0. 'selv om' exception tail
    m = re.search(r"\s+selv om\s+", claim)
    if m:
        return [claim[:m.start()].strip().rstrip(","),
                "Gjelder " + claim[m.start():].strip()]
    # 0b. 'med unntak for' exception tail
    m = re.search(r",\s*med unntak for\s+", claim)
    if m:
        return [claim[:m.start()].strip().rstrip(","),
                "Unntak: " + claim[m.end():].strip()]
    # 1. 'men' coordination
    m = re.search(r",?\s+men\s+", claim)
    if m:
        parts = [claim[:m.start()].strip(), claim[m.end():].strip()]
        parts = [p for part in parts for p in _split_shared_subject(part)]
        return parts
    # 2. comma-coordinated og clauses
    if re.search(r",\s+og\s+", claim):
        raw = re.split(r",\s+og\s+", claim)
        parts = []
        for i, p in enumerate(raw):
            p = p.strip()
            if i > 0:
                words = p.split()
                if words and words[0] in PRONOUN_START:
                    parts.append(p)
                elif words and (words[0] in VERB_START or words[0] in AUX):
                    parts.append(_carryover(raw[0].strip(), p))
                else:
                    parts.append(p)
            else:
                parts.extend(_split_shared_subject(p) if re.search(r"\s+og\s+", p) else [p])
        return parts
    # 3. shared-subject og split inside a single clause
    if re.search(r"\s+og\s+", claim):
        parts = _split_shared_subject(claim)
        if len(parts) > 1:
            return parts
    # 4. ', ikke Y' tail with subject carryover (negation preserved)
    m = re.search(r",\s*ikke\s+(.+)$", claim)
    if m:
        head = claim[:m.start()].strip()
        st = _subject_of(head)
        tail = m.group(1).strip()
        atoms = [head]
        if st:
            atoms.append(st + " er ikke " + tail)
        else:
            atoms.append("er ikke " + tail)
        return atoms
    # 5. fronted condition ', vil/kan/skal ...'
    m = re.match(r"^([^,]+),\s*(vil|kan|skal|ma|har|blir|gir)\b", claim)
    if m:
        return [m.group(1).strip(), claim[m.start(2):].strip()]
    return [claim]
