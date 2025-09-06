---
title: Known gaps & quick wins
---

# Known gaps & quick wins

- Helpers referenced in MassiveHarvester
  - extract_documentation_content, extract_subcategory, extract_tags, assess_content_quality — either implemented elsewhere or need to be added. Easy to port from Enhanced patterns.
- Concurrency in harvest_all_sources
  - Parameter max_workers exists but runs sequentially; add concurrent.futures for speed.
- Category taxonomy
  - Distractor pools assume normalized categories. Centralize tag→category map for consistency.

See also
- Roadmap/Board (tasks) → /roadmap/board
- Concepts → /concepts/

