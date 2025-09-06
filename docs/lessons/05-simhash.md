---
title: Lesson 05 – SimHash Dedupe
lessonId: lessons/05
---

# Lesson 05 – SimHash Dedupe

Narrative: Fingerprint questions and skip near‑duplicates by Hamming distance.

## Diagram
```mermaid
flowchart LR
  Text --> Trigrams --> SimHash64 --> Hamming
```

## Mini-lab
- Compute simhash; drop items with distance < 8.

## Grok check
- Why combine SimHash with Levenshtein ratio?

## Mastery
<MasteryChecklist id="lessons/05" :items='[
  "Compute SimHash for sample questions",
  "Apply Hamming threshold",
  "Compare to ratio filter",
  "Explain strengths/weaknesses"
]' />

