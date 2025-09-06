---
title: Runbook – Ship (Local)
---

# Runbook – Ship (Local)

## Preconditions
- Python 3.10+
- Paths for QuizMentor quizzes dir and AI-Research repo

## Steps
1. Harvest (quick path)
   ```bash
   scraper harvest massive --output-dir /tmp/harvest --max-content 200 --questions-per-content 5 --workers 8 --complete
   ```
2. Export quizzes
   ```bash
   scraper export quizmentor --db /tmp/harvest/harvest.db --out ./out
   ```
3. Import (choose one)
   - QuizMentor:
     ```bash
     scraper import quizmentor --from ./out --to /path/to/QuizMentor.ai/quizzes --mode copy
     ```
   - AI-Research (dry-run first):
     ```bash
     scraper import research --db /tmp/harvest/harvest.db --repo /path/to/AI-Research --edition PRO --min-quality 0.75 --dry-run --limit 10
     ```
4. One-shot (optional)
   ```bash
   scraper ship local \
     --qm /path/to/QuizMentor.ai/quizzes \
     --research /path/to/AI-Research \
     --report-dir ./reports \
     --teach --preview --strict \
     --max-content 200 --questions-per-content 5
   ```

## Verify
- Quiz files present under target quizzes/
- Summaries created and index.md appended in AI-Research
- reports/ship-report.html exists and opens
- Optional: minimal schema validation passes

```bash
python3 scripts/validate_quiz_dir.py --from ./out/quizzes
```

## Rollback
- Delete generated artifacts in target repos (if needed) and re-run

