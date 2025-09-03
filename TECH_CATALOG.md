# Tech Catalog (Scraper)

Purpose
A quick-reference catalog of techniques, patterns, and terms used in the Scraper project. Each entry includes a definition, why we use it, and where it appears.

1) Manifest file
- What: JSON inventory of produced files (name, sha256, size_bytes, question_count, totals)
- Why: Integrity and completeness check before import; basis for reports
- Where: export_dir/manifest.json (next to quizzes/)

2) Minimal schema (validation)
- What: The minimum fields/types required for a quiz JSON to be considered valid (questions[], options[], correct_answer, difficulty, metadata)
- Why: Fast gate to catch malformed files without heavy schemas
- Where: Validate step; QuizMentor adapter and scripts/harvest-dock.js examples

3) SimHash dedupe
- What: Locality-sensitive hashing of text; near-identical texts have small Hamming distance
- Why: Prevent near-duplicate questions from landing
- Where: Planned in harvesters before saving generated_questions (Hamming < 8–10 → skip)

4) TF‑IDF
- What: Term weighting by frequency and rarity (term frequency × inverse document frequency)
- Why: Build vectors for semantic uniqueness checks; concept ranking; category centroids (future)
- Where: EnhancedHarvester (TF‑IDF + cosine), optional centroid suggestions

5) Cosine similarity
- What: Angle-based similarity on normalized vectors (0..1)
- Why: Semantic uniqueness (reject highly similar), category scoring (future)
- Where: EnhancedHarvester uniqueness; optional research categorization

6) Centroids (text)
- What: Mean TF‑IDF vector of items in a category
- Why: Suggest categories for new items by nearest centroid (blend with tag rules)
- Where: Planned research importer enhancement

7) Normalization (vectors)
- What: Scale vectors to unit length (L2 norm = 1)
- Why: Make cosine similarity meaningful and comparable
- Where: Any TF‑IDF vector usage

8) Canonical list (tags)
- What: The authoritative set of allowed tags for a repo
- Why: Consistency and predictable filtering/search
- Where: AI-Research/docs/research/TAGS.md; importer normalization step

9) Tag normalization
- What: Lowercasing, hyphenation, synonym mapping (llm2.0→llm-2-0), enforcing edition tag
- Why: Normalize user/harvested tags to canonical forms
- Where: Research importer (with optional tags_map.json)

10) Sentinel file (optional)
- What: A simple export_complete.json marker
- Why: Optional explicit “done” signal; redundant with manifest/validation
- Where: Export step (off by default)

11) Symlinks vs copy
- What: Docking files by linking vs copying
- Why: Symlinks save space/time; copy is portable and safe
- Where: QuizMentor importer (--mode link|copy)

12) Idempotency
- What: Running the same import again yields the same end state
- Why: Safe re-runs; no duplicate slugs/rows
- Where: Research importer (skips existing slugs; avoids duplicate index rows)

13) Checksums (sha256)
- What: Cryptographic hash of file content
- Why: Verify file contents didn’t change between export and import
- Where: manifest.json and validate step

14) Hamming distance
- What: Count of differing bits between two equal-length bitstrings
- Why: Compare SimHashes for near-duplicate detection
- Where: SimHash dedupe (threshold 8–10)

15) HTML static report
- What: Single HTML file summarizing a ship run (totals, warnings, previews)
- Why: Human-friendly visibility without a backend
- Where: Planned scraper ship local --report-dir ./reports

16) Levenshtein ratio
- What: Edit-distance similarity (0..1)
- Why: String-level uniqueness and option similarity; fallback when TF‑IDF unavailable
- Where: MassiveHarvester and EnhancedHarvester

17) Readability heuristic
- What: Light proxy for Flesch‑Kincaid (sentence/word length)
- Why: Contribute to difficulty scoring
- Where: Planned MassiveHarvester difficulty upgrade

18) LRU cache
- What: Least-Recently-Used in-memory cache
- Why: Quick SimHash dedupe and recent uniqueness checks
- Where: Planned in harvesters before DB write

19) Deterministic heuristics
- What: Rule-based, transparent algorithms with fixed thresholds
- Why: Predictable, debuggable, local-first pipeline
- Where: Everywhere (concepts, answers, distractors, scoring)

20) ETL (Extract–Transform–Load)
- What: Classic pipeline pattern
- Why: Structure harvest → process → export/import with gates and reports
- Where: Overall project architecture

