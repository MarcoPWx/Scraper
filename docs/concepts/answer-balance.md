---
title: Answer balance (A/B/C/D)
---

# Answer balance (A/B/C/D)

## TL;DR
We avoid predictable answer positions by tracking counts of A/B/C/D and steering the next correct answer.

## Rules (Enhanced)
- Track counts of correct answer positions
- If skew > 20, force next correct answer into the least‑used slot
- Otherwise, sample with inverse‑frequency weights to smooth distribution

## Diagram
```mermaid
flowchart LR
  C[Counts A/B/C/D] --> K{Skew > 20?}
  K -- yes --> F[Force least‑used slot]
  K -- no --> W[Weighted sample (inverse freq)]
```

## See also
- Distractors → /concepts/distractors
- Scoring → /concepts/scoring

