---
title: Guardrails Cheatsheet
---

# Guardrails Cheatsheet

- Robots/ToS
  - Honor robots.txt; include contact in UA
  - Record ToS snapshot (URL + hash + timestamp)
- Licensing & attribution
  - SPDX/license detection; require attribution; block unknown in strict mode
- PII/Secrets
  - Regex + entropy detectors; redact (normal) or block (strict)
- Quotes
  - max_chars, percent reproduced thresholds; favor summaries

