---
title: Contracts – System-to-System
---

# Contracts – S2S

## Scraper → QuizMentor staging
- Files: quizzes/quiz_<category>_harvested.json, harvest_index.json
- Schema: questions[], options[], correct_answer (0..3), difficulty 1..5

## Scraper → AI-Research repo
- Files: docs/research/summaries/<slug>.md, docs/research/index.md
- Behavior: idempotent – skip existing slugs; once-per-index-row

