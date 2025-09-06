---
title: Common Q&A – Meeting Mode
---

# Common Q&A – One‑pager (Meeting Mode)

## TL;DR
Short answers and links for the most frequent questions in meetings.

## Q&A
- What is idempotency? Running an import twice yields the same end state—no duplicate files/rows.
- What is SimHash? A near‑duplicate fingerprint using Hamming distance; we use it to skip similar Qs.
- What is TF‑IDF? Scores tokens high if frequent in a doc but rare across docs; used for uniqueness.
- How are categories decided? Tags → canonical map; Drafts fallback; optional centroid assist (future).
- Where do quizzes land? quizzes/quiz_<category>_harvested.json in the QuizMentor repo.
- Where do research summaries go? docs/research/summaries/<slug>.md + index.md row in AI‑Research.
- How do we check quality? confidence ≥ 0.75 (export), gates (manifest, schema, sanity), teach logs.

## Snippet
```bash
scraper export quizmentor --db ./harvest/harvest.db --out ./out
```

## See also
- Quick Cards → /quick-cards
- Contracts → /contracts/S2S
- Runbook → /ops/runbooks/ship-local

