# Legal Guardrails – Design (CE Style)

Purpose
- Provide privacy‑first, compliant harvesting and packaging with explainable decisions, fully local and testable.

Scope (gates and policies)
- Source policy and robots/ToS compliance
  - Allow/deny lists per domain, path, topic; robots.txt honoring; rate limiting; contact email in UA
  - ToS/licensing snapshot recorded per source (URL + hash + timestamp)
- Licensing and attribution
  - License detection: repo LICENSE/SPDX; web footer/meta; unknown when not determinable
  - Per‑artifact license + attribution fields required
  - Compatibility matrix (intended use: quiz vs research)
  - Strict mode: block unknown/incompatible licenses; Normal: warn and queue for review
- Content hygiene and PII
  - PII/secret detectors (regex + entropy) on inputs/outputs; redaction or block in strict
  - Quote length and percent reproduced thresholds; bias toward summaries; max quote chars
  - Unsafe patterns flagged (e.g., unsafe code snippets) with reason codes
- Provenance and audit
  - Chain‑of‑custody: source URL, timestamps, content hash, simhash/fingerprint, license state at capture
  - Immutable audit log of gate outcomes and overrides (who/why/when)
- Jurisdiction toggles
  - GDPR/CCPA purge hooks; export of data subjects list if applicable
- Report & risk
  - HTML Legal Summary card: per‑gate status (robots, license, attribution, PII, quotes), counts, reason codes, docs links
  - Overall risk score: allow/warn/block

Artifacts
- policy.yaml: project policy (allow/deny, license matrix, PII rules, thresholds, strict behaviors)
- GateResults: structured results with IDs, reason codes, remediation hints
- Audit log: append‑only records of results and overrides

CLI additions
- --policy policy.yaml, --profile <name>, --compliance-only, --remediate=redact|exclude

TDD
- Unit: license detection (spdx/heuristics), attribution required, PII detectors, quote thresholds
- E2E: strict blocks unknown license; redaction removes PII; quote reduction passes; robots honored for disallowed domains

References
- POLICY_TEMPLATE.yaml (this folder)
- README (Product positioning and quickstart)

