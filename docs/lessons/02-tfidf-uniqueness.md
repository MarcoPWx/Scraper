---
title: Lesson 02 – TF‑IDF & Uniqueness
lessonId: lessons/02
---

# Lesson 02 – TF‑IDF & Uniqueness

Narrative: Vectorize questions; ensure semantic uniqueness via cosine and ratio.

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

## Mini-lab
- Compute cosine max to existing; enforce < 0.85.

Commands (inspect uniqueness via report)
```bash
# One-shot run with previews to inspect uniqueness decisions in the report
scraper ship local \
  --qm /path/to/QuizMentor.ai/quizzes \
  --research /path/to/AI-Research \
  --report-dir ./reports \
  --preview --strict --max-content 60 --questions-per-content 5
# Open: ./reports/ship-report.html and review dedupe/uniqueness sections
```

Code (Massive: Levenshtein and SimHash)
```python path=/Users/betolbook/Documents/github/Scraper/src/scraper/harvesters/massive.py start=535
def is_unique_question(self, question: QuestionCandidate, threshold: float = 0.85) -> bool:
    # fingerprint and category/subcategory Levenshtein ratio check (fuzzywuzzy)
    # ... returns False if similarity > threshold
```
```python path=/Users/betolbook/Documents/github/Scraper/src/scraper/harvesters/massive.py start=563
# SimHash helpers (64-bit over trigrams)
def _trigrams(self, text: str) -> List[str]:
    ...
```

Code (Enhanced: TF‑IDF + cosine, fallback to Levenshtein)
```python path=/Users/betolbook/Documents/github/Scraper/src/scraper/harvesters/enhanced.py start=226
def check_semantic_uniqueness(self, question: str, threshold: float = 0.85) -> bool:
    # vectorize existing, cosine_similarity, fallback to fuzzy ratio
```

## Grok check
- Why normalize vectors before cosine?

## Mastery
<MasteryChecklist id="lessons/02" :items='[
  "Build TF‑IDF vectors",
  "Compute cosine to nearest",
  "Apply threshold < 0.85",
  "Explain normalization"
]' />

