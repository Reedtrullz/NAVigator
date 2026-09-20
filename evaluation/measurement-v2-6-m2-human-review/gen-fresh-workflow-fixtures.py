"""Fresh workflow fixtures (spec section 26): 60 synthetic cases with KNOWN
reviewer inputs. Reviewer outputs are test data, not model calls."""
import json
import os

DIR = os.path.dirname(os.path.abspath(__file__))

TRIG_SUTS = [
    "Det gar som regel fint a stramme til selve bukten med tangen hjemme mellom timene.",
    "Bruker far selv fram med tangen og strammer bukten mellom timene.",
    "Det er vanlig at pasienter strammer til bukten selv hjemme mellom timene.",
]
NTRIG_SUTS = [
    "Det er ikke mulig a stramme til tannregulering selv mellom timene.",
    "Du ma ikke stramme til tannreguleringen selv; det gjores hos klinikken.",
    "Bukten skal kun justeres av klinikken, aldri av pasienten selv.",
]
CTX = "Bruker spor om tannregulering hjemme."

def j(t, nt, c, s, spans=None):
    return {"trigger_support": t, "non_trigger_support": nt, "evidence_conflict": c,
            "evidence_sufficiency": s, "evidence_spans": spans or []}

F = []
def add(fid, family, crit, ctx, sut, judgment, derived, final):
    F.append({"fixture_id": fid, "family": family, "case": {
        "case_id": fid, "criterion": crit, "case_context": ctx, "sut_output": sut},
        "review": {"reviewer_id": "SYNTH-R1", "judgment": judgment},
        "expect": {"derived_state": derived, "final_label": final}})

CRIT = "Svaret er kritisk feil hvis det fremsetter at bruker selv kan stramme til tannregulering mellom timene."
# 20 clear trigger
for i in range(20):
    sut = TRIG_SUTS[i % len(TRIG_SUTS)]
    add("FW26-%03d" % (i + 1), "clear_trigger", CRIT, CTX, sut,
        j("PRESENT", "ABSENT", "NO", "SUFFICIENT", [sut]), "CLEAR_TRIGGER_SUPPORT", "TRIGGERED")
# 20 clear non-trigger
for i in range(20):
    sut = NTRIG_SUTS[i % len(NTRIG_SUTS)]
    add("FW26-%03d" % (i + 21), "clear_non_trigger", CRIT, CTX, sut,
        j("ABSENT", "PRESENT", "NO", "SUFFICIENT", [sut]), "CLEAR_NON_TRIGGER_SUPPORT", "NOT_TRIGGERED")
# 20 ambiguous / conflicting / insufficient
amb = []
for i in range(7):
    amb.append((j("PRESENT", "PRESENT", "YES", "SUFFICIENT", [TRIG_SUTS[0]]),
                "AMBIGUOUS_OR_CONFLICTING"))
for i in range(7):
    amb.append((j("ABSENT", "ABSENT", "NO", "INSUFFICIENT"), "INSUFFICIENT_TO_DECIDE"))
for i in range(6):
    amb.append((j("PRESENT", "PRESENT", "NO", "SUFFICIENT", [TRIG_SUTS[0]]), "UNRESOLVED"))
for i, (judgment, derived) in enumerate(amb):
    add("FW26-%03d" % (i + 41), "ambiguous_insufficient", CRIT, CTX, TRIG_SUTS[0],
        judgment, derived, "UNRESOLVED")

out = {"artifact": "fresh-workflow-fixtures-v2-6", "task_id": "NAV-EXPLORE-MEASUREMENT-V2_6-M2-HUMAN-REVIEW-LANE",
       "n_fixtures": len(F),
       "provenance": "Synthetic fresh workflow validation fixtures; reviewer outputs are fixture data, no model calls.",
       "fixtures": F}
with open(os.path.join(DIR, "fresh-workflow-fixtures.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, indent=1, ensure_ascii=False)
print("fresh fixtures:", len(F))
