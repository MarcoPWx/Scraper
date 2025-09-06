---
title: CLI commands
---

# CLI commands (scraper/cli.py)

Harvest
- Non‑interactive (Massive):
  ```bash
  scraper harvest massive --output-dir ./harvest_output --max-content 200 --questions-per-content 5 --workers 8 --complete
  ```
- Interactive (Enhanced):
  ```bash
  scraper harvest enhanced --output-dir ./harvest_output
  ```

Export
```bash
scraper export quizmentor --db ./harvest_output/harvest.db --out ./out
```

Import
- Into QuizMentor repo:
  ```bash
  scraper import quizmentor --from ./out --to ../QuizMentor.ai/quizzes --mode copy
  ```
- Into AI‑Research notes:
  ```bash
  scraper import research --db ./harvest_output/harvest.db --repo ../AI-Research --edition PRO --min-quality 0.6 --mapping file.json --limit 50 --teach
  ```

Validate (planned)
```bash
scraper validate quiz|harvest|research ...
```

One‑shot pipeline
```bash
scraper ship local --qm ../QuizMentor.ai/quizzes --research ../AI-Research \
  --report-dir ./reports --teach --preview --strict \
  --max-content 200 --questions-per-content 5
```

