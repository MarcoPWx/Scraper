# Dev Log – Scraper

Date: 2025-09-03

Scope: Local-first harvesting → quizzes (QuizMentor) and research markdown (AI-Research) with deterministic heuristics. No LLMs, no remote DBs.

What shipped today
- Importers (local docking)
  - QuizMentor importer: copies/links quiz_*.json into <quizmentor_repo>/quizzes/
  - AI-Research importer: writes docs/research/summaries/<slug>.md and appends docs/research/index.md (idempotent)
- CLI additions
  - scraper import quizmentor --from <export_dir> --to <quizmentor_repo>/quizzes --mode copy|link [--no-verify]
  - scraper import research --db <harvest.db> --repo <ai_research_repo> --edition PRO|CE --min-quality <float> [--mapping path] [--dry-run] [--limit N]
- README rewrite (onboarding manual)
  - Glossary and definitions (idempotent, normalization, centroids, metadata enrichment)
  - Detailed algorithms (extraction, distractors, difficulty, confidence, uniqueness)
  - ASCII diagrams per stage and adapter interface specs for both repos

Design decisions
- Local-only by default: keep all workflows runnable without Supabase/Ollama/cloud
- Idempotent importers: re-runs skip existing slugs/files and avoid duplicate index rows
- Deterministic heuristics: transparent rules, documented formulas, tunable constants

Heuristics (current)
- MassiveHarvester
  - Concepts: regex patterns for ProperCase/ALLCAPS/code/bold/headings; de-dup, top N
  - Answer: pick longest relevant sentence for concept (definition mode clamps length)
  - Distractors: category-informed + length balancing + similarity banding
  - Difficulty: +length +keywords +option_length +option_similarity → 1..5
  - Uniqueness: Levenshtein ratio threshold (0.85), plus md5 fingerprint
- EnhancedHarvester
  - Semantic uniqueness: TF‑IDF cosine < 0.85 (fallback to string ratio)
  - Answer position balance: keep A/B/C/D counts; correct goes to least-used if imbalance > 20
  - Distractor quality q ∈ [0,1], confidence σ(β0 + β1*q + β2*(1−cos) + …)

Adapters (today)
- QuizMentor staging
  - Source: <export_dir>/quizzes/quiz_*.json, harvest_index.json
  - Target: <quizmentor_repo>/quizzes/
  - Schema: questions[], options[], correct_answer (index), explanation, difficulty(1..5)
- AI-Research staging
  - Writes: docs/research/summaries/<slug>.md and docs/research/index.md
  - Slugify: lowercase, non-alnum → dash, collapse, trim

Verification checklist
- QuizMentor: quizzes/ contains quiz_*.json; sample file has questions[] with options[4] and correct_answer
- AI-Research: summaries/<slug>.md created; index.md appended exactly one row under category; re-run shows skipped

Next up (short-term)
- Importer reports
  - --report-dir <path> to emit JSON/CSV of {created, skipped, issues}; include category decisions and reasons
- Answer extraction upgrades
  - Definitional scoring with pattern verbs ("is", "refers to") and proximity weight; context window for continuity
- Uniqueness+ speed
  - SimHash trigram fingerprints with Hamming threshold; maintain LRU for fast recent dedupe
- Category placement (research)
  - Optional centroid-based suggestion blended with tag→category; thresholds documented; still local-only
- Flat questions export (optional)
  - --format questions produces a single questions.json matching dev/mock schema (correctAnswer + incorrectAnswers)

Future (deferred)
- Optional metadata enrichment (author/publisher/date) behind a --enrich-meta flag, with rate limits
- Optional Supabase adapter for QuizMentor (schema push) when DB is available

Notes
- All new behavior is documented in README with examples and ASCII flows
- Keep imports idempotent; add --update-existing later only when there’s a reviewer workflow

---

Date: 2025-09-03 (Teach + Preview upgrade)

What changed
- Ship command: added --teach and --preview flags to scraper ship local
- HTML report: added Previews cards (2 sample questions per category; first bullet for each new summary)
- Teach logs: labeled decisions for learning
  - [teach §E. Validate] Levenshtein > 0.85 → reject
  - [teach §F. SimHash] Hamming < 8 → skip near-duplicate question
  - [teach §B. Heuristics] Enhanced TF‑IDF cosine max < 0.85 → unique
- Orchestrator: fixed signature and CLI wiring; pass teach/preview through to harvesters/importers
- Import (research): supports --teach to print category decision scoring

Why
- Improve explainability while running (teaching-first)
- Provide fast visual sampling before full review (previews)

How to use
  scraper ship local \
    --qm /path/to/QuizMentor.ai/quizzes \
    --research /path/to/AI-Research \
    --report-dir ./reports \
    --teach --preview --strict \
    --max-content 200 --questions-per-content 5

Follow-ups
- Strict gates (fail-fast) toggles for manifest/schema/tag mismatches
- SimHash dedupe report section listing skipped questions with distances
- Inline README anchors in teach logs like [teach §F. SimHash]

---

Date: 2025-09-03 (Journeys + CE/TDD docs update)

What changed
- Added docs/JOURNEYS.md with 20 user + 20 S2S journeys
- Updated docs/EPICS.md with CE principles, TDD gates, and references to journeys
- Linked JOURNEYS and SYSTEM_STATUS from README
- Added docs/SYSTEM_STATUS.md status snapshot
- Created GitHub labels and issues for epics and tasks

Why
- Move to AI-OS-CE style with clear acceptance scenarios and TDD gates

Notes
- Phase 1 acceptance: cover U1–U5, S1–S7, S12, S19 via unit+e2e

---

Date: 2025-09-03 (Legal guardrails seed)

What changed
- Added docs/LEGAL_GUARDRAILS.md and docs/POLICY_TEMPLATE.yaml
- README: product positioning and legal overview appendix
- TAURI: Legal Center, policy/profile wiring, review queue panels
- Ship report: Legal Summary card placeholder, orchestrator passes legal context
- Seeded epics (#30–#32) and tasks (#33–#42) for legal, format studio, and review/audit

Why
- Position Scraper as a “Local Knowledge Harvester & Compliance Packager” with CE/TDD guardrails

Next up
- Implement policy loader + --policy flag (issue #33)
- Gate engine stub for PII+quotes (issue #34)
- License detection + attribution (issue #35)
- Robots/ToS snapshot + enforcement (issue #36)

---

Date: 2025-09-03 (Pause checkpoint / Resume plan)

Snapshot (main)
- Docs: positioning, CE/TDD EPICS, JOURNEYS (20+20), SYSTEM_STATUS, LEGAL_GUARDRAILS, POLICY_TEMPLATE, TAURI updates
- Code: ship --preview, teach logs improvements, HTML report (previews + Legal Summary placeholder), orchestrator wiring, CI workflow, SimHash unit test
- GitHub: labels; epics (#1–#7, #30–#32); tasks seeded (#8–#29, #33–#42)

Resume sequence (TDD)
1) #33 Policy loader + --policy flag
   - Add src/scraper/policy.py (load_policy)
   - CLI: add --policy to ship local; pass policy_path to orchestrator
   - Orchestrator: load policy; expose ctx["legal"] basics (honor_robots, require_attribution)
   - Tests: tests/test_policy.py (load success/missing sections); tests/test_cli_policy_flag.py
   - Acceptance: running with docs/POLICY_TEMPLATE.yaml shows policy-loaded values in Legal Summary card

2) #34 Legal gates stub: PII (regex+entropy) + quotes
   - Add src/scraper/legal_gates.py (evaluate_text: pii_hits, secrets_hits, long_quotes, percent_reproduced)
   - Integrate into orchestrator: aggregate counts across quiz/research text
   - Tests: tests/test_legal_gates.py (regex/entropy/quotes); e2e tests/e2e/test_legal_summary.py
   - Acceptance: fixture data triggers counts; Legal Summary shows nonzero totals

3) #35 License detection + attribution required
   - SPDX/heuristic detection; require attribution fields on artifacts
   - Strict policy blocks Unknown/incompatible; normal warns and queues
   - Unit + e2e; Legal Summary reports license counts

4) #36 Robots/ToS snapshot + enforcement
   - Record ToS snapshot; honor allow/deny and robots.txt (mocked parser in tests)
   - Strict blocks disallowed; Legal Summary reports robots_disallow

Branches
- Create feature branch per task: feat/policy-loader → feat/legal-gates → feat/license-detect → feat/robots-tos

Commands (reference)
- git checkout -b feat/policy-loader
- pip install -e .[test]
- pytest -q
- git add -A && git commit -m "feat(policy): loader + --policy" && git push -u origin feat/policy-loader

Definition of Done (resume milestone)
- Running `scraper ship local --policy ./docs/POLICY_TEMPLATE.yaml --teach --preview` produces a report where the Legal Summary card shows policy-loaded fields and aggregate counts for PII/quotes gates; unit+e2e tests pass in CI.
