---
title: RAG – Meeting Mode
---

# RAG – One‑pager (Meeting Mode)

## TL;DR
Retrieve 3–5 diverse passages, ground answers with citations, and refuse when context is insufficient. Prefer diversity (MMR), enforce provenance.

## Diagram
```mermaid path=null start=null
flowchart LR
  Q[Question] --> R[Retrieve top‑k]
  R --> D[MMR diversify]
  D --> C[Compose prompt + citations]
  C --> A[Answer]
```

## Talking points
- Retrieval settings: k=3–5; prefer MMR for diversity
- Index: keep source URL and excerpt for provenance
- Prompting: require citations; define refusal when missing context
- Confidence: surface retrieval scores and gaps
- Summaries: 50–200 char bullets; quotes ≥80 chars (see importer template)

## Decisions & tradeoffs
- Recall vs precision (k size)
- Extractive vs abstractive summaries
- Citation strictness vs answer fluency

## Pitfalls
- Over‑retrieval (topic drift) vs under‑retrieval (miss facts)
- Missing provenance links or weak quotes

## Snippet
```yaml path=null start=null
# Importer summary layout (excerpt)
summary:
- bullet 1 (<=200 chars)
- bullet 2
key_quotes:
- ">=80 chars quote"
```

## See also
- Cheatsheet → /cheatsheets/rag
- Lessons (Uniqueness & TF‑IDF) → /syllabus
- Contracts → /contracts/S2S

