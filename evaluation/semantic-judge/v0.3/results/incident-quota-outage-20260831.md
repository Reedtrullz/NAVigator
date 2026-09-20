# INCIDENT: upstream quota exhaustion during v0.3 runs (2026-08-31)

## Timeline (CEST, Europe/Oslo)

- 01:25:53  Last successful upstream call (calibration CAL032, ts 23:25:53 UTC).
- 01:26:11  First failed call (stability CAL088 run 3, ts 23:26:11 UTC). Both
  concurrent sessions (calibration PID session 25513, stability session 17031)
  broke at the same wall-clock moment.
- 01:26-02:35  Every model call returned HTTP 200 at the proxy level but with an
  empty/invalid upstream body; judge transport recorded
  "parse-error: missing verdict key" via the v0.2 fallback validator.
- 02:31  Direct proxy chat completion probe: HTTP 502
  "upstream stream ended early (adapter_eof)".
- 02:33  Proxy quota cache: shortPercent = 100 (5-hour window, started ~23:22
  CEST on 30-08), weeklyPercent = 33. Onset matches window exhaustion.
- 02:35  Stability session interrupted by operator; both result files
  quarantined as *.superseded-quota-20260831-* and trimmed to valid rows only.
- 04:21:55  Expected 5-hour window reset (shortResetAt epoch 1788142915).

## Valid rows preserved

- Calibration: 32/84 (CAL001-CAL032), all decompose+judge status ok.
- Stability: 32/150, all decompose+judge status ok.

## Handling

Outage rows were NOT deleted; they are preserved in the quarantined copies.
Clean files contain only pre-outage rows. Both runners are resumable by
(claim id, run) so the post-reset relaunch fills exactly the missing rows.
No prompt or logic changes were made in response to the outage.
