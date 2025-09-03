# Tauri UI Proposal – Scraper Desktop

This document outlines a local‑first desktop UI for Scraper using Tauri (Rust core + WebView). It mirrors the AI‑OS‑PRO style: a left navigation, top toolbar, and content panels with streaming logs and rich reports.


Goals
- Run the full pipeline locally with clear, teach‑first feedback
- Zero secrets, zero cloud dependencies by default
- Cross‑platform (macOS, Linux, Windows) with small binary size
- Provide a Legal Center to configure policies, review flags, and maintain audit trails


Information Architecture
- Navigation
  - Dashboard: quick actions, last run status, recent reports
  - Harvest: configure and run Massive/Enhanced, view content counts
  - Quizzes: browse exported quiz_* files by category; quick sample questions
  - Research: list new/updated summaries; link to index.md
  - Ship (One‑shot): orchestrate harvest → export → validate → import → report
  - Reports: open reports/ship-report.html and history
  - Legal Center: policy wizard, flagged items queue, audit trail
  - Settings: paths (output_dir, quizzes dir, research repo), thresholds, strict gates, policy/profile
  - Learning Center: embedded docs mirroring README and EPICS (searchable)

- Panels
  - Teaching Console: real‑time stream of --teach logs with anchors to docs
  - Artifacts Explorer: tree of out/ and reports/
  - Preview Cards: inline sample questions and summary bullets
  - Legal Summary: table of legal gates and counts; click through to flagged items
  - Review Queue: triage UI (Fix/Redact/Exclude) with reason codes


Technical Design
- Invocation model
  - The UI calls the bundled scraper CLI as a subprocess (e.g., `scraper ship local ...`)
  - Stream stdout/stderr via Tauri Command API to the Teaching Console
  - Read artifacts (manifest.json, quizzes/*.json, reports/ship-report.html) from disk
  - Policy/Profile awareness: pass --policy and --profile to CLI; persist settings in app config

- IPC & Permissions
  - Minimal IPC: only run whitelisted commands with validated parameters
  - Never display or log secrets; no network access required

- Rendering
  - Use the OS webview to render the HTML report directly
  - Lightweight UI components (Svelte/React) for lists, forms, and consoles

- State & Config
  - Store user settings (paths, thresholds) in the app config dir
  - Remember last run parameters and report location for quick reopen

- Packaging
  - Tauri bundler for macOS app; sign with a developer cert
  - Include a quickstart sample project (optional) for first‑run demo


MVP Scope
- Launch app; configure paths
- Run `ship local` with `--teach --preview --strict`
- Show streaming logs and a link to open the generated HTML report
- Render basic previews (read from artifacts)


Stretch Goals
- Embedded report viewer (render HTML within the app)
- Threshold sliders with live preview of how they would affect decisions (simulated)
- Live stats from SQLite (read‑only), e.g., total questions by category
- Keyboard shortcuts and dark mode


Risks & Mitigations
- Cross‑platform path differences → use Tauri APIs for path joins; validate paths at form level
- Long‑running processes → stream logs, allow safe cancel, detect non‑zero exit codes and show actionable errors
- Binary size creep → keep dependencies minimal; reuse system Python or document runtime requirements


Open Questions
- Should we embed Python or require a local Python? (lean: require local Python with clear onboarding)
- Do we ship a sample dataset to demonstrate the UI without network access? (lean: yes, small sample)


References
- README: teach/preview quickstart
- EPICS: high‑level goals and acceptance criteria

