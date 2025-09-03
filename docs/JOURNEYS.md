# Journeys – User and System-to-System (CE Style)

This document describes 20 user journeys (U1–U20) and 20 system-to-system journeys (S1–S20) for Scraper CE. Each journey lists goals, preconditions, steps, gates, success/failure signals, and artifacts.


User Journeys (U1–U20)

U1. Quick Ship (Local)
- Role: Quiz Engineer
- Goal: Produce fresh quizzes and research summaries locally
- Preconditions: Python installed; QM quizzes dir and AI-Research repo paths
- Steps:
  1) scraper ship local --qm <path> --research <path> --report-dir ./reports --teach --preview --strict
- Gates: manifest OK; quiz schema OK; sanity stats acceptable
- Success: quizzes copied/linked; summaries created; report with previews
- Failure: strict gates fail with clear reasons
- Artifacts: out/quizzes/*.json, reports/ship-report.html

U2. Research Import (Dry Run)
- Role: Research Editor
- Goal: Validate summaries and categories without writing
- Steps: scraper import research --db <db> --repo <repo> --dry-run --teach --limit 10
- Gates: category mapping explainable; quality >= min
- Success: printed plan with categories and reasons
- Failure: unknown tags escalate under --strict

U3. Strict Gate Failure → Fix → Pass
- Role: Engineer
- Steps:
  1) Run ship --strict
  2) Intentionally corrupt a quiz file, rerun -> fail
  3) Fix file, rerun -> pass
- Gates: strict-gates block with actionable errors

U4. Dedupe Review (SimHash)
- Role: MLE/Editor
- Steps: Run ship; open report; inspect dedupe section (skipped near-dupes + distances)
- Success: Understand and justify skips

U5. Teach-Driven Learning
- Role: New User
- Steps: Run ship --teach; follow [teach §X] links to README anchors
- Success: Concepts learned without leaving repo

U6. Category Subset Export
- Role: Quiz Engineer
- Steps: Export, then import only selected categories to QM (filter at importer)
- Success: Only targeted categories docked

U7. QA: Schema Spot Check
- Role: QA
- Steps: Validate quiz directory; sample open quiz_*.json
- Gates: minimal schema, question count

U8. Threshold Tuning Session
- Role: MLE
- Steps: Adjust thresholds; run e2e fixtures; compare dedupe and uniqueness
- Success: Fewer duplicates, acceptable uniqueness

U9. PM Report Review
- Role: PM
- Steps: Open reports/ship-report.html; review totals, warnings, previews

U10. First-Time Setup
- Role: New User
- Steps: pip install -e .; run help; run a minimal ship to sample outputs

U11. Tag Normalization Review
- Role: Research Editor
- Steps: Check tag→category mapping; add overrides JSON; re-run import

U12. CSV Report for Analysis
- Role: Data Analyst
- Steps: Use generate_csv_report; load into spreadsheet for pivot tables

U13. Scheduled Local Ship (Manual)
- Role: DevOps
- Steps: Write a cron job/launchd to run ship daily into timestamped out/

U14. Source Rate-Limit Audit
- Role: Security/Infra
- Steps: Review harvester sleeps and headers; run small batch; confirm no spikes

U15. Curation Loop (Idempotency)
- Role: Editor
- Steps: Delete a specific slug.md; re-run import to regenerate

U16. Mock Fixtures for App Dev
- Role: App Dev
- Steps: Export flat questions.json (optional feature) for local app mocks

U17. Regression Across Releases
- Role: Release Eng
- Steps: Run e2e suite before tagging; compare artifacts/manifest to baseline

U18. GUI Trial (Tauri)
- Role: Any
- Steps: Use GUI to run ship; view Teaching Console; open report in-app

U19. Learning Center Search
- Role: New User
- Steps: Use docs index/search to find topics quickly

U20. Troubleshoot Unknown Tags
- Role: Editor
- Steps: Run import; see tag warnings; add to mapping or whitelist; re-run


System-to-System Journeys (S1–S20)

S1. Scraper → Exporter → QuizMentor Importer
- Flow: SQLite (generated_questions) → quizzes/*.json → copy/link into QM/quizzes
- Gates: schema validation; manifest

S2. Scraper → AI-Research Importer
- Flow: harvested_content → summaries/*.md + index.md append (idempotent)
- Gates: min_quality; tag mapping; repo structure check

S3. Export → Manifest
- Flow: Write manifest.json with sha256, size, question counts
- Gates: sha256 recomputed matches on validate

S4. Validate → Gate Summary
- Flow: Validation results summarized into HTML Report card

S5. Harvest → Dedupe (SimHash)
- Flow: Compute 64-bit SimHash; skip near-duplicates by Hamming threshold
- Output: dedupe_skipped count + sample list for report

S6. Teach Logs → Docs Anchors
- Flow: Emit [teach §X] markers; map to README anchors in report

S7. Orchestrator → HTML Report
- Flow: Collect totals, warnings, previews; render static report

S8. GUI (Tauri) → CLI
- Flow: Tauri spawns `scraper ship local` and streams stdout/stderr

S9. CLI → SQLite
- Flow: Insert harvested_content and generated_questions; query for export/import

S10. SQLite → CSV
- Flow: generate_csv_report writes flattened questions for analysis

S11. EnhancedHarvester → TF-IDF Similarity
- Flow: Vectorize existing questions; enforce max cosine threshold

S12. SimHash → Skipped Samples List
- Flow: Record skipped near-dupes with {distance, question} (truncated) for report

S13. Mapping File (JSON) → Category Decision
- Flow: Merge user mapping with heuristics to decide categories

S14. GitHub Actions → pytest → Coverage
- Flow: CI runs tests, enforces >= 70% coverage, blocks merge on fail

S15. Tag → Release (Packaging)
- Flow: On tag, build artifacts, upload with checksums, draft release (future)

S16. Research Importer → Idempotency Guard
- Flow: Skip existing slug.md and existing index row

S17. QM Importer → Mode (copy|link)
- Flow: Choose symlink or copy; fallback to copy on failure

S18. Repo Validator → Research Repo Check
- Flow: Verify directories and template presence before writing

S19. Strict Mode → Exit Code
- Flow: Gate failures produce non-zero exit; CI fails accordingly

S20. Previews Assembler → Report
- Flow: Sample 1–2 quiz questions and first bullet per summary into report


Acceptance Mapping
- U1–U20 and S1–S20 must be covered by a combination of unit and e2e tests.
- Minimal coverage per phase (see EPICS Roadmap):
  - Phase 1: U1–U5, S1–S7, S12, S19
  - Phase 2: U18–U19, S8; add smoke for GUI

