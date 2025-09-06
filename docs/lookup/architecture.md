---
title: Architecture – Meeting Mode
---

# Architecture – One‑pager (Meeting Mode)

## TL;DR
Scraper runs locally: Harvest → SQLite → Export (quiz JSON) → Import (QM/Research) → HTML report. Idempotent adapters, strict gates, search‑first docs.

## Diagram
```mermaid path=null start=null
flowchart LR
  A[Sources] --> B[Harvesters]
  B --> C[(SQLite)]
  C --> D[Export (Quiz JSON)]
  D --> E[Import → QuizMentor]
  C --> F[Import → AI-Research]
  F --> G[Markdown + Index]
```

## Talking points
- Local‑only: privacy‑first; no secrets, no cloud by default
- Deterministic heuristics (TF‑IDF, SimHash, ratio, gates)
- Two harvester modes: Massive (breadth) and Enhanced (quality)
- Exporter filters by confidence (≥ 0.75 default)
- Idempotent importers: no duplicate slugs or index rows
- Strict gates: manifest, minimal schema, sanity stats
- HTML report: totals, warnings, previews, parameters
- Docs are teaching‑first; search‑first flow

## Decisions & tradeoffs
- Heuristics vs models: transparency and speed over opaque accuracy
- Symlink vs copy (QM import): default to copy; fallback resilient
- Category mapping: tags + Drafts fallback; optional centroid assist later

## Pitfalls
- Over‑retrieval (topic drift); under‑retrieval (missing facts)
- Duplicate wording (use SimHash + ratio thresholds)
- Long quotes (respect quote limits in guardrails)

## Snippet
```bash path=null start=null
# One‑shot with teach+preview+strict (local‑only)
scraper ship local \
  --qm /path/to/QuizMentor.ai/quizzes \
  --research /path/to/AI-Research \
  --report-dir ./reports \
  --teach --preview --strict \
  --max-content 200 --questions-per-content 5
```

## See also
- Gallery → /architecture/GALLERY
- Runbook → /ops/runbooks/ship-local
- Contracts → /contracts/S2S
- Lessons 00–03 → /syllabus
