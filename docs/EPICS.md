# EPICS – Scraper Productization (CE Style + TDD)

This document captures product epics and acceptance criteria for evolving Scraper into a polished, local‑first desktop product in the AI‑OS‑CE style: community‑friendly, local‑first, transparent heuristics, and TDD‑gated delivery.

Principles (CE)
- Local‑first and privacy‑by‑default; no secrets, no cloud dependencies
- Deterministic heuristics and explainability (teach logs map to docs)
- Documentation‑as‑product: onboarding lives in the repo and UI
- TDD as a gate: every epic has acceptance tests (unit + e2e) enforced by CI
- Simple, composable CLIs with idempotent importers/exporters

Testing strategy and gates (TDD)
- Unit tests
  - Algorithms: SimHash/Hamming thresholds; Levenshtein filters; TF‑IDF uniqueness
  - Validators: quiz minimal schema; manifest integrity; category mapping
  - CLI: flag wiring (--teach, --preview, --strict), param validation
- E2E tests (network‑free)
  - Mock harvest inputs to produce deterministic quiz+research outputs
  - Run `scraper ship local` over a temp sandbox
  - Verify: manifest totals, quiz schema, research files created, HTML report shows previews and gate summary
- CI gates (GitHub Actions)
  - Run unit + e2e suites; coverage threshold (initial 70%)
  - No external network calls; use mocks/fixtures
  - PRs must pass CI to merge


Epic 1 — One‑shot Ship UX (MVP)
- Goal: Non‑technical users can run harvest → export → validate → import → report in one place.
- Must have
  - Command: scraper ship local with explicit paths (QM quizzes dir, AI‑Research repo)
  - HTML report with totals, per‑quiz breakdown, research list, warnings
  - Previews: 2 sample questions per category; first bullet of each new summary
  - Teach mode: labeled logs ([teach §E], §F, §B) across pipeline
- Done when
  - A single command produces artifacts in out/ and reports/ with no manual steps
  - A new editor can understand “what shipped” from HTML and logs
  - Acceptance tests pass in CI: unit (CLI wiring), e2e (ship over sandbox with previews)


Epic 2 — Strict Gates (fail‑fast)
- Goal: Catch bad artifacts early; produce actionable errors.
- Must have
  - --strict option propagates to validation gates in ship
  - Gates: manifest checksums, minimal schema, sanity stats
  - Exit non‑zero on violations (configurable)
  - Gate summary in HTML report
- Done when
  - Intentionally corrupting a quiz file stops ship with clear reasons
  - Acceptance tests pass in CI: unit (validators), e2e (ship fails with clear gate reasons)


Epic 3 — Dedupe Report & Teaching Aids
- Goal: Make uniqueness decisions auditable and tunable.
- Must have
  - SimHash dedupe section in report: total skipped near‑dupes + top samples {distance, question}
  - Teach log anchors referencing README sections (e.g., [teach §F. SimHash])
  - Configurable thresholds (Levenshtein ratio, TF‑IDF cosine, SimHash Hamming)
- Done when
  - A reviewer can justify why a question was skipped and tweak thresholds to change outcomes
  - Acceptance tests pass in CI: unit (SimHash/ratio thresholds), e2e (report includes dedupe section with samples)


Epic 4 — Learning Center (Docs-in-App)
- Goal: Provide a self‑contained learning space that mirrors README sections.
- Must have
  - Concepts: glossary, diagrams, algorithms, thresholds
  - Search across docs
  - Link from teach logs to sections (deep links)
- Done when
  - A new user can become productive without leaving the app
  - Acceptance tests pass in CI: unit (doc anchors map), e2e (teach logs link to docs in report or UI)


Epic 5 — Tauri Frontend (Desktop)
- Goal: Cross‑platform GUI with local privacy guarantees.
- Must have
  - Shells out to the scraper CLI for operations (harvest/export/ship)
  - Streams stdout/stderr into a “Teaching Console” panel
  - Renders HTML report in‑app (webview) and links to artifacts folder
  - Basic settings for paths and thresholds
- Nice to have
  - Tail the SQLite DB stats live (read‑only)
  - Dark/light mode; keyboard shortcuts
- Done when
  - A user can run ship from the GUI and view the report without a terminal
  - Acceptance tests pass (separate UI CI later); headless smoke can invoke CLI and capture logs


Epic 6 — Packaging & Distribution
- Goal: Frictionless install on macOS/Linux/Windows.
- Must have
  - Python runtime packaging guidance or embedded runtime
  - Tauri app bundle + code‑signed macOS app (dev cert ok)
  - Versioned changelog + release notes
- Done when
  - A “Download app” + “Open” flow runs a sample ship on a demo project
  - Release pipeline publishes artifacts after tests pass; checksums attached


Epic 7 — Extensibility & Integrations (post‑MVP)
- Goal: Add new harvesters/exporters/importers without core rewrites.
- Must have
  - Clear adapter interfaces and templates
  - Example integration (e.g., flat questions.json, mock fixtures)
  - Optional LLM enhancer clearly separated and off by default
- Done when
  - A contributor can add a new exporter with a small, documented module


Roadmap Phases
- Phase 0 (now): Teach/Preview + HTML report previews + docs (unit tests seed)
- Phase 1 (MVP): Strict gates, dedupe report, Learning Center docs (unit + e2e gates)
- Phase 2 (GUI): Tauri frontend invoking CLI, report rendering, settings (separate UI repo CI)
- Phase 3 (Polish): Packaging, app signing, sample project, tutorials (release CI)
- Phase 4 (Extend): New adapters, optional enhancers, community contributions

Issue taxonomy (labels)
- epic, task, bug, chore, docs, CE, TDD
- domains: ship, harvest, export, import, research, quizmentor, ui, tauri
- testing: test:unit, test:e2e, strict-gates, teach, preview

References
- CI workflow: .github/workflows/ci.yml
- Tests root: /tests
- README (teach/preview quickstart): ../README.md
- Tauri UI proposal: ./TAURI.md


Non‑Goals (for now)
- Cloud services, telemetry, or remote DBs
- Replacing deterministic heuristics with black‑box models
- Editing AI‑Research or QuizMentor repos beyond the current idempotent writes


Links
- README (teach/preview quickstart): ../README.md
- Tauri UI proposal: ./TAURI.md

