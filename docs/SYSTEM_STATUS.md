# System Status – Scraper CE

Snapshot time: 2025-09-03T23:04:07Z

Branches
- main (default)
- feat/preview-teach-docs-tauri (active): adds teach/preview wiring, HTML previews, docs updates

CI
- Workflow: .github/workflows/ci.yml – pytest with coverage
- Coverage target (planned): >= 70% (see issue #25)

Docs
- README: onboarding + teach/preview quickstart
- DEVLOG: updated with teach/preview and docs work
- EPICS: CE + TDD principles, epics with acceptance criteria
- JOURNEYS: 20 user + 20 S2S journeys
- TAURI: UI proposal

Open Epics
- #1 Ship UX (MVP)
- #2 Strict Gates (fail-fast)
- #3 Dedupe Report & Teaching Aids
- #4 Learning Center (Docs-in-App)
- #5 Tauri Frontend (Desktop)
- #6 Packaging & Distribution
- #7 Extensibility & Integrations

Recent Changes
- Added --preview to ship, teach logs labeled, report previews
- Updated README, DEVLOG, EPICS; added JOURNEYS and TAURI docs
- Created CI workflow and initial unit test (SimHash)
- Created labels and issues for epics/tasks

Next Actions
- Implement Gate Summary report card (#8)
- Add e2e ship test harness with fixtures (#9)
- Add strict gates unit + e2e tests (#11–#13)

Links
- Repo: https://github.com/MarcoPWx/Scraper
- PR: https://github.com/MarcoPWx/Scraper/pull/new/feat/preview-teach-docs-tauri
- Issues: https://github.com/MarcoPWx/Scraper/issues

