---
title: Uniqueness & deduplication
---

# Uniqueness & deduplication

## TL;DR
We ensure generated questions are not duplicates or near‑duplicates of prior content using textual ratio, TF‑IDF semantic similarity, and SimHash fingerprints.

## Methods
- String similarity (Levenshtein ratio)
  - Reject if question text ratio > 0.85 vs existing in the same category/subcategory (Massive)
- Semantic similarity (TF‑IDF + cosine, scikit‑learn)
  - Reject if cosine ≥ 0.85 vs prior questions (Enhanced); fallback to Levenshtein > 0.85 if TF‑IDF path fails
- Near‑duplicate hashing (SimHash 64‑bit over trigrams)
  - Reject if Hamming distance < 8 (Massive)

## Diagram
```mermaid
flowchart LR
  Q[Candidate question] --> L[Levenshtein ratio]
  Q --> T[TF‑IDF cosine]
  Q --> S[SimHash (64‑bit)]
  L -->|>0.85| Reject
  T -->|>=0.85| Reject
  S -->|Ham<8| Reject
  L -->|else| Keep
  T -->|else| Keep
  S -->|else| Keep
```

## See also
- Distractors → /concepts/distractors
- Scoring → /concepts/scoring

