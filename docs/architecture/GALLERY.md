---
title: Architecture Gallery
---

# Architecture Gallery

## At a glance

```mermaid
flowchart LR
  A[Sources\n(docs, SO, GitHub)] --> B[Harvesters\nMassive/Enhanced]
  B --> C[(SQLite\nharvest.db)]
  C --> D[Export\nquizzes JSON]
  D -->|dock| E[QuizMentor\nquizzes/]
  C --> F[Import\nAI-Research]
  F --> G[Markdown summaries]
```

### SVGs

<SvgGallery />

## Ship sequence (text)

```mermaid
sequenceDiagram
  participant U as User
  participant S as Scraper CLI
  U->>S: ship local (paths, thresholds, report-dir)
  S->>S: harvest → export → validate
  S->>S: import quizmentor / import research
  S->>U: write ship-report.html
```

## Cross-links
- README (pipeline and adapters)
- [EPICS](/specs/) (see Epics for productization goals)
- [JOURNEYS](/specs/) (user and S2S journeys)
- [System Status](/SYSTEM_STATUS)

