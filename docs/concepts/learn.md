---
title: Learn the ideas (plain English)
---

# Learn the ideas (plain English)

- TF‑IDF + cosine
  - Represent each question by the words it uses (weighted), then compare direction similarity. High cosine ≈ similar meaning.
- SimHash + Hamming
  - Hash text into a 64‑bit “fingerprint” where similar text produces similar bits. Count bit differences to catch near‑duplicates fast.
- Levenshtein (edit distance)
  - Few edits (insert/delete/replace) to turn one string into another → very similar.
- Distractor quality
  - Wrong answers should be plausible but distinct—balanced lengths and meanings; neither trivially wrong nor nearly identical.
- Answer balance
  - Evenly distribute positions A/B/C/D to avoid guessable patterns.
- Heuristic difficulty
  - Longer/denser questions, similar options, and high-quality distractors are harder.

See also
- Concepts index → /concepts/
- Cheatsheets (thresholds, CLI) → /cheatsheets/thresholds, /cheatsheets/cli

