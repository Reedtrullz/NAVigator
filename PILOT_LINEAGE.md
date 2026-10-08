# NAVigator pilot lineage — 2026-09-25

This is a local source/artifact inventory, not a deployment selector. All 25 build manifests below had matching declared input and output hashes during the review. No generated HTML, frozen inputs, manifest, checksum file or archive was rewritten. A matching manifest does not prove all extra files are safe to distribute.

## How the generations relate

- Older `NAVigator-pilot-privat-2026-09` and B1/B3/B4 packages use a Python generator containing the template/script. Seventeen declared inputs are typical of that generation.
- `NAVigator-pilot3-autonom-2026-09-22` separates template, CSS, safety, state/plan and UI source; its review-package HTML is byte-identical to the working root at this snapshot.
- `NAVigator-pilot3-ferdigstilling-2026-09-22` retains original/work and four named packages. The named clean/final/ready variants share HTML bytes; this does not establish that their complete package contents are identical.
- `NAVigator-pilot3-fire-restpunkter-2026-09-22` contains subsequent fixes, language and guided-UI variants. Safety and state/UI hashes differ across generations. Its `work` and guided-ui-v3 HTML match.
- `NAVigator-rolig-start-2026-09-23` uses the guided-v3 safety/state modules with different UI/template styling. `DEPLOY-2026-09-23.md` records a historical private deployment; no remote readback was performed now.
- The nested `NAVigator-household-income-2026-09-23` work/delivery family adds optional household/income fields and session-v2 handling, with legacy session-v1 support. Its `work` HTML matches `NAVigator-enklere-veiviser-2026-09-23`, not `rolig-start`. Do not assume the last top-level folder is the newest implementation or the deployed selection.

## Manifest inventory

Paths are relative to Projectos. Hash prefixes identify the local HTML for comparison; full hashes remain in each original manifest. All rows are local integrity matches only.

| Package root | Declared inputs | HTML SHA-256 prefix | Result |
|---|---:|---|---|
| `NAVigator/NAVigator-B3B4-V1fix-2026-09-22` | 17 | `19a83444ed9d4c82` | MATCH |
| `NAVigator/NAVigator-bolig-okonomi-B1B4-2026-09-22` | 17 | `c3d723435a52e759` | MATCH |
| `NAVigator/NAVigator-bolig-okonomi-B3B4-fullforing-2026-09-22` | 17 | `e544316e9d5cb306` | MATCH |
| `NAVigator/NAVigator-pilot-privat-2026-09/NAVigator-household-income-2026-09-23/baseline` | 44 | `27161a2cd1a10d9d` | MATCH |
| `NAVigator/NAVigator-pilot-privat-2026-09/NAVigator-household-income-2026-09-23/delivery/NAVigator-Pilot3-husstand-inntekt-2026-09-23` | 44 | `b3eaa13c8dee4185` | MATCH |
| `NAVigator/NAVigator-pilot-privat-2026-09/NAVigator-household-income-2026-09-23/delivery/NAVigator-enklere-veiviser-2026-09-23` | 44 | `203136c9c513999a` | MATCH |
| `NAVigator/NAVigator-pilot-privat-2026-09/NAVigator-household-income-2026-09-23/work` | 44 | `203136c9c513999a` | MATCH |
| `NAVigator/NAVigator-pilot-privat-2026-09` | 17 | `19a83444ed9d4c82` | MATCH |
| `NAVigator/rapporter-2026-09/NAVigator-pilot-bolig-okonomi-overlevering-2026-09-22` | 17 | `ac86612fabe6e571` | MATCH |
| `NAVigator-pilot3-autonom-2026-09-22/baseline/original/NAVigator-B3B4-V1fix-2026-09-22` | 17 | `19a83444ed9d4c82` | MATCH |
| `NAVigator-pilot3-autonom-2026-09-22` | 44 | `a2e1ef1bf629fb21` | MATCH |
| `NAVigator-pilot3-autonom-2026-09-22/review-package` | 44 | `a2e1ef1bf629fb21` | MATCH |
| `NAVigator-pilot3-ferdigstilling-2026-09-22/NAVigator-pilot3-kontrollor-ferdigstilling-2026-09-22` | 44 | `dfbcfd8ef6d01d5c` | MATCH |
| `NAVigator-pilot3-ferdigstilling-2026-09-22/NAVigator-pilot3-kontrollor-ferdigstilling-2026-09-22-clean` | 44 | `dfbcfd8ef6d01d5c` | MATCH |
| `NAVigator-pilot3-ferdigstilling-2026-09-22/NAVigator-pilot3-kontrollor-ferdigstilling-2026-09-22-final` | 44 | `dfbcfd8ef6d01d5c` | MATCH |
| `NAVigator-pilot3-ferdigstilling-2026-09-22/NAVigator-pilot3-kontrollor-ferdigstilling-2026-09-22-ready` | 44 | `dfbcfd8ef6d01d5c` | MATCH |
| `NAVigator-pilot3-ferdigstilling-2026-09-22/original` | 44 | `a2e1ef1bf629fb21` | MATCH |
| `NAVigator-pilot3-ferdigstilling-2026-09-22/work` | 44 | `dfbcfd8ef6d01d5c` | MATCH |
| `NAVigator-pilot3-fire-restpunkter-2026-09-22/NAVigator-pilot3-guided-ui-2026-09-23-v3` | 44 | `27161a2cd1a10d9d` | MATCH |
| `NAVigator-pilot3-fire-restpunkter-2026-09-22/NAVigator-pilot3-kontrollor-fire-restpunkter-2026-09-22` | 44 | `cdae2280ca4f25e3` | MATCH |
| `NAVigator-pilot3-fire-restpunkter-2026-09-22/NAVigator-pilot3-sprak-2026-09-22` | 44 | `99a695b251279423` | MATCH |
| `NAVigator-pilot3-fire-restpunkter-2026-09-22/NAVigator-pilot3-sprak-2026-09-22-v2` | 44 | `daac9fdf16bf911e` | MATCH |
| `NAVigator-pilot3-fire-restpunkter-2026-09-22/original` | 44 | `dfbcfd8ef6d01d5c` | MATCH |
| `NAVigator-pilot3-fire-restpunkter-2026-09-22/work` | 44 | `27161a2cd1a10d9d` | MATCH |
| `NAVigator-rolig-start-2026-09-23` | 44 | `9a1ce8d2144ccbcf` | MATCH |

## Working rules

For the separated-source Pilot 3 generation, inspect `src/{template.html,styles.css,safety.js,state-plan.js,ui.js}`, then `build/build_pilot.py`, `data`, `kilder` and source snapshots. The builder embeds the data and scripts into a single HTML and writes a sidecar manifest. Its input enumeration includes all non-hidden files under source/data/evidence directories, so adding documents there would change the input set of a future rebuild. Review guides therefore live at outer roots/build tooling boundaries, and sealed child packages are preserved.

Use the exact generation's tools. `tools/verify_package.py` checks listed hashes and forbidden members; running it against a development tree containing node_modules, reports or .DS_Store can fail for package hygiene despite matching declared inputs. `tools/pack_review.py` writes a new tree/ZIP; it is not a read-only check. No public distribution gate or professional approval was changed.

## Utviklingskandidat — 08.10.2026

Ny kontrollert kilde er `pilot/` på `codex/navigator-contact-pilot`, basert på selektivt kopierte kode-/schema-/policyfiler fra husholdningsvarianten. Historiske register-, kommune- og korpusinnganger følger ikke automatisk med. Se `releases/next/candidate.json` og `docs/implementation-2026-10-08.md`. Nytt bygg går til lokal `outputs/`; UTKAST/BLOCKED, runtime frakoblet. Ingen eksisterende pilot, frosset måling eller aktiv deploy er endret.
