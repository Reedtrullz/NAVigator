# Leakage Audit (V4)

## Method

Full-project scan for case-ID regex (RC2B- plus 4 digits) co-occurring with label
vocabulary (verdict and slot names), plus a structural JSON walk and a
180-character window check for derivable ID-to-verdict mappings.

## Results

- Raw scan hits before cleanup: 24 flagged files; 16 were true per-case
  label-bearing files (V3 construction/pilot surfaces). All 16 plaintext originals
  were deleted after roundtrip-verified sealing of the V4 answer key and
  construction audit.
- Remaining hits: 8, all incidental and allowlisted:
  - 7 old V2/V3 report and manifest files whose case-ID mentions are quota counts
    or historical narrative, with no per-case verdict derivable:
    `RC2-V2-set/annotation-summary.md`, `RC2-V2-set/blind-manifest.json`,
    `RC2-V2-set/final-report.md`, `RC2-V2-set/quota-report.md`,
    `RC2-V3-set/final-report.md`, `RC2-V3-set/v2-selection-qa-root-cause.md`,
    `V2-construction-audit.md`
  - `RC2-V3-set/construction/annot-prompt.txt`: contains 5 gap-wave case IDs with
    claims and sources only; label tokens are the generic schema line
- Per-case label files remaining: 0. The structural check found no derivable
  ID-to-verdict mapping in any remaining file.
- Machine-readable findings: `label-leakage-inventory.json`.
- `qa-tests/test_v4_qa.py` uses RCXX-0000 fixture IDs so the test file itself can
  never become a leak.
