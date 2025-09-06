---
title: Contracts Cheatsheet
---

# Contracts Cheatsheet

- Scraper → QuizMentor staging
  - Files: quizzes/quiz_<category>_harvested.json, harvest_index.json
  - Minimal schema: questions[], options[], correct_answer (0..3)
- Scraper → AI-Research repo
  - Files: summaries/<slug>.md, index.md append
  - Idempotent writes; Drafts fallback
- SSE/Resilience patterns
  - Retry with backoff; heartbeat comments; last-event-id

