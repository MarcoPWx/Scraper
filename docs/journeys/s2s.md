---
title: System-to-System Journeys (S1–S20)
---

# System-to-System Journeys (S1–S20)

These flows connect contracts, gates, and adapters.

- S1. Export → QM Importer
  - Contract: quizzes/quiz_<cat>.json, harvest_index.json; minimal schema
  - See: Contracts → /contracts/S2S; Runbook → ship-local
- S2. Research Importer
  - Contract: summaries/<slug>.md + index.md append; idempotent
  - See: Import rules in README; Lessons 04
- S3. Export → Manifest
  - sha256/size/counts; gate validates
- S4. Validate → Report Card
  - Gate summary in HTML report; strict mode stops
- S5. Harvest → Dedupe (SimHash)
  - Skipped near-dupes list → report; Lessons 05
- S6. Teach Logs → Docs Anchors
  - Labeled decisions mapping back to README sections
- S7. Orchestrator → HTML Report
  - Assemble totals, listings, previews; See: Lesson 08
- S8. GUI (Tauri) → CLI
  - Spawn ship; stream logs; render report; See: Lesson 10, TAURI
- S9. CLI → SQLite
  - Persist harvested_content and generated_questions; exporters consume
- S10. SQLite → CSV
  - Optional CSV report for analysis
- S11. EnhancedHarvester → TF‑IDF Similarity
  - Enforce max cosine; See: Lesson 02
- S12. SimHash → Skipped Samples List
  - Dedupe samples → report; See: Lesson 05
- S13. Mapping File (JSON) → Category Decision
  - Merge with heuristics; See: README, Lesson 04
- S14. CI → Tests → Coverage
  - Enforce thresholds; block on fail; See: Lesson 11
- S15. Tag → Release (Packaging)
  - Build artifacts on tag
- S16. Research Importer → Idempotency Guard
  - Skip existing slugs; once-per-index-row
- S17. QM Importer → Mode (copy|link)
  - Prefer copy; fallback on failure
- S18. Repo Validator → Research Repo Check
  - Verify dirs and template before write
- S19. Strict Mode → Exit Code
  - Non-zero on violation; CI fail
- S20. Previews Assembler → Report
  - Sample previews added to report

See docs/JOURNEYS.md for the full list S1–S20.

