---
title: Persistence (SQLite tables)
---

# Persistence (SQLite tables)

## Massive
- harvested_content
  - id, source_url (unique), source_type, title, content, category, subcategory, tags (JSON), scraped_at, quality_score, processed
- generated_questions
  - id, fingerprint (unique), question, options (JSON), correct_answer, explanation, category, subcategory, difficulty, confidence, source, created_at, validated, deployed
- harvest_stats
  - timestamp, urls_scraped, content_harvested, questions_generated, unique_questions, categories_covered, quality_avg

## Enhanced
- enhanced_questions
  - question, options (JSON), correct_answer, explanation, category, subcategory, difficulty, confidence, source_url, source_type, distractor_quality, answer_distribution, semantic_fingerprint (unique), concepts (JSON), created_at
- source_usage
  - source_url (PK), last_used, times_used, questions_generated

## CSV export (Massive)
- Columns include: id, category, subcategory, difficulty, question, option_1..option_4, correct_answer, explanation, confidence, source, created_at

