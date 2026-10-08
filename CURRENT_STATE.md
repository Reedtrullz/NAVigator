# NAVigator — source and corpus review

## Refresh — 2026-10-04

Baseline identity captured before documentation edits: `NAVigator`: `main`, `f778090a7a1f`

No implementation change was found in the inventoried application/builder source. New proposal metadata is not implementation. The retrieval and discovery completeness boundaries were reread; their previously recorded concerns remain. All 25 discovered NAV build manifests were rehashed: 963 declared inputs/outputs matched; no generated HTML or source evidence was rewritten.

This repeat review used source/configuration fingerprints, local Git metadata and targeted boundary reads. Earlier structural counts, test statements and dirty-file totals below retain their September observation date; they are not fresh runtime results. See [portfolio coverage](../REVIEW_COVERAGE.md) and [checkout inventory](../WORKTREES.md) for current scope and limits.

## Source analysis retained from 2026-09-25

Reviewed 2026-09-25. **Research workspace plus several private pilot generations, not one finished application.** The local Git repository is on `main`, HEAD `f778090a7a1f151aebcdad1cdd2af7dc51453b41` (2026-09-22), with zero tracked changes at inventory time. Many pilot packages are deliberately ignored by Git. A clean tracked tree does not mean those packages are backed up or part of HEAD.

## What is actually here

- Numbered Markdown chapters and `INNHOLD.md`: a Norwegian welfare/public-service knowledge corpus, extended with family, housing, health, education and local-service research. Some material is personal; this review inventoried that boundary without reading or reproducing case records.
- `data/`: machine-readable service/legal/knowledge indexes, frozen rules, discovery protocols, verification registers and gap tracking. These are source snapshots, not automatically current official rules.
- `runtime/discovery/`: V1 discovery engine, providers, URL safety, evidence ledger, access classification, serialization and replay fixtures.
- `runtime/discovery_v2/`: separate experimental provider/orchestrator versions, including live HTTP/render/search paths. V2.5 is not the measured phase-3 entrypoint.
- `runtime/sut/pipeline.py`: explicitly incomplete phase-1 skeleton. `runtime/sut/phase2/` adds safety, decomposition, knowledge, discovery and route reasoning; `phase3/pipeline.py` imports those S1–S8 stages and adds answer planning/rendering/finalization. Its discovery adapter explicitly invokes frozen V1 **replay**.
- `evaluation/`: large frozen evaluation corpus and historical run evidence (5,154 regular files at baseline after cache exclusions). It was inventoried and entrypoints traced, not individually semantically rejudged.
- `NAVigator-*` subdirectories and `rapporter-2026-09/`: multiple source/candidate/review/export packages. `NAVigator-pilot-privat-2026-09/build/build_pilot.py` is an older generator with embedded application code and a hardcoded Node path. Newer Pilot 3 trees have separate `src/` modules. See [PILOT_LINEAGE.md](PILOT_LINEAGE.md).
- `scripts/pagegrab.sh`, `extract_text.py`, `qa_check.sh`: collection/extraction and a small known-pattern consistency check. The grep-based QA script is not legal validation or content certification.

## Findings verified in source

| Priority | Finding | Evidence / consequence |
|---|---|---|
| High privacy | General knowledge retrieval lacks a private-record gate. | `runtime/sut/phase2/knowledge.py:load_knowledge/retrieve` loads hash-matching indexed content and filters by domain/keywords, not personal-data authorization. Index metadata includes one personal-journal entry classified `SOURCE_DOCUMENTATION` in a general domain. Its contents were not read or copied. This is a potential disclosure path, not an observed external leak. |
| High correctness | Discovery V2.5 can report `COMPLETE` after unsuccessful fetches. | `orchestrator_v25.py` increments `pages_fetched` immediately after `fetch`, before status checks, then uses `pages_fetched > 0` for execution completeness. No useful service result is required. |
| High correctness | Eligibility is inferred from presence of age/group text. | The same orchestrator sets `eligibility` from extracted text booleans rather than comparing the user's age/need with service criteria. A provenance check alone does not establish a suitable route. |
| Medium reproducibility | Pilot generations are unversioned/ignored and non-interchangeable. | `.gitignore` excludes many candidate trees; the newer nested household/income variant differs from the separate `rolig-start` tree. Names such as final/ready do not imply approval or current deployment. |
| Medium build portability | The older pilot builder hardcodes `/usr/local/bin/node`. | Newer Pilot 3 builders resolve `--node`, `NAVIGATOR_NODE` or PATH and verify local AJV. Do not apply instructions from one generation to another. |
| Documentation corrected | The old portfolio described a non-Git `NAV Explore` corpus. | That directory is absent; this directory has a Git repository, runtime code and ignored pilot generations. Historical `NAV Explore` strings remain in code/docs and the external `.codegraph` symlink. |

No safety/clinical/legal rules were changed or revalidated against public authorities. Existing blocker records remain in force. Prior test counts and certification labels are historical evidence, not a current pass issued by this review.

## Working commands and boundaries

The runtime tests use Python `unittest`. From this root, examples include `PYTHONPATH=runtime python3 -m unittest sut.phase3.test_phase3` and `python3 -m unittest runtime.discovery.tests`; these were inspected, **not run**. Live discovery CLI modules may fetch external pages. Read provider/configuration paths before running them. There is no single root npm app or universal build command.

For newer Pilot 3 packages, the source is `src/template.html`, `styles.css`, `safety.js`, `state-plan.js`, `ui.js`, validated by `build/build_pilot.py`; output is `app/NAVigator-pilot.html` and `build/manifest.json`. Generating artifacts changes files. The browser's safety gate, fact/context revisions, explicit draft export/import and source evidence are separate from corpus runtime experimentation.

## Review coverage and limits

Read corpus index/README structure, ignore rules, runtime phase entrypoints, retrieval and V2.5 critical paths, V1 replay adapter, old and Pilot 3 builders, package verifier/packer, Pilot 3 state/safety/UI/export paths and tests/configuration. Compared variant source hashes and newer household/session fields. **All 25 discovered build manifests matched their declared input/output hashes** in an independent read-only check. This establishes local bytes only; it does not prove complete packaging, source validity, browser behavior, live deployment, semantic safety or distribution approval. No personal records, credentials, provider sessions, legal sources, or live endpoints were opened.

## Utviklingskandidat — 08.10.2026

Ny kontrollert kilde er `pilot/` på `codex/navigator-contact-pilot`, basert på selektivt kopierte kode-/schema-/policyfiler fra husholdningsvarianten. Historiske register-, kommune- og korpusinnganger følger ikke automatisk med. Se `releases/next/candidate.json` og `docs/implementation-2026-10-08.md`. Nytt bygg går til lokal `outputs/`; UTKAST/BLOCKED, runtime frakoblet. Ingen eksisterende pilot, frosset måling eller aktiv deploy er endret.
