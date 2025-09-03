#!/usr/bin/env python3
from __future__ import annotations

"""
AI-Research importer
- Reads harvested_content from SQLite (harvest.db)
- Generates markdown summaries from template and updates index.md
- Places entries under the best-matched category (fallback: Drafts)
- Works without any local LLM; heuristics-only, with optional mapping file
"""

import os
import re
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

from .base import BaseImporter


def _slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text or "entry"


def _domain_from_url(url: str) -> str:
    try:
        return urlparse(url).netloc or ""
    except Exception:
        return ""


class AIResearchImporter(BaseImporter):
    DEFAULT_CATEGORY = "Drafts"

    # Tag→Category rules (simple built-in mapping; can be supplemented via mapping file)
    TAG_CATEGORY_RULES: Dict[str, str] = {
        # LLM theory & uncertainty
        "uncertainty": "LLM Theory & Uncertainty",
        "bayesian": "LLM Theory & Uncertainty",
        # Hallucination taxonomy
        "hallucination": "Hallucination: Taxonomies & Surveys",
        "taxonomy": "Hallucination: Taxonomies & Surveys",
        "survey": "Hallucination: Taxonomies & Surveys",
        # Detection & measurement
        "detection": "Hallucination: Detection & Measurement",
        "metrics": "Hallucination: Detection & Measurement",
        "evaluation": "Hallucination: Detection & Measurement",
        # Context engineering / RAG
        "context-engineering": "Context Engineering",
        "rag": "Context Engineering",
        # Domain
        "healthcare": "Domain: Healthcare/Psychiatry",
        "psychiatry": "Domain: Healthcare/Psychiatry",
        # LLM 2.0
        "llm-2-0": "LLM 2.0 & RAG (Contextual)",
        "knowledge-graph": "LLM 2.0 & RAG (Contextual)",
    }

    def __init__(
        self,
        db_path: str,
        repo_path: str,
        edition: str = "PRO",
        min_quality: float = 0.6,
        mapping_file: Optional[str] = None,
        dry_run: bool = False,
        limit: Optional[int] = None,
        teach: bool = False,
    ) -> None:
        self.db_path = Path(db_path)
        self.repo_path = Path(repo_path)
        self.edition = edition
        self.min_quality = float(min_quality)
        self.dry_run = dry_run
        self.limit = limit
        # Optional user-provided tag→category mapping (JSON)
        self.user_mapping: Dict[str, str] = {}
        if mapping_file:
            try:
                with open(mapping_file, "r") as f:
                    self.user_mapping = json.load(f)
            except Exception:
                self.user_mapping = {}

        # AI-Research paths
        self.docs_root = self.repo_path / "docs" / "research"
        self.summaries_dir = self.docs_root / "summaries"
        self.templates_dir = self.docs_root / "templates"
        self.index_md = self.docs_root / "index.md"
        self.entry_template = self.templates_dir / "ENTRY_TEMPLATE.md"
        self.summaries_dir.mkdir(parents=True, exist_ok=True)
        self.teach = teach

    # --------------------
    # Data access
    # --------------------
    def _load_content(self) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        query = (
            "SELECT source_url, source_type, title, content, category, subcategory, tags, scraped_at, quality_score FROM harvested_content "
            "WHERE quality_score >= ? ORDER BY quality_score DESC, scraped_at DESC"
        )
        params: Tuple[Any, ...] = (self.min_quality,)
        if self.limit is not None and isinstance(self.limit, int) and self.limit > 0:
            query += " LIMIT ?"
            params = (self.min_quality, int(self.limit))
        rows = cursor.execute(query, params).fetchall()
        conn.close()
        items: List[Dict[str, Any]] = []
        for r in rows:
            items.append(
                {
                    "source_url": r[0] or "",
                    "source_type": r[1] or "",
                    "title": r[2] or "",
                    "content": r[3] or "",
                    "category": (r[4] or "").lower(),
                    "subcategory": (r[5] or "").lower(),
                    "tags": json.loads(r[6]) if r[6] else [],
                    "scraped_at": r[7] or "",
                    "quality_score": float(r[8] or 0.0),
                }
            )
        return items

    # --------------------
    # Heuristics
    # --------------------
    def _extract_sentences(self, text: str) -> List[str]:
        parts = re.split(r"(?<=[\.!?])\s+", text)
        return [p.strip() for p in parts if len(p.strip()) > 0]

    def _extract_bullets(self, text: str, n: int = 5) -> List[str]:
        sentences = self._extract_sentences(text)
        # prefer medium-length informative sentences
        candidates = [s for s in sentences if 50 <= len(s) <= 200]
        if len(candidates) < n:
            candidates = sentences
        return candidates[:n]

    def _extract_quotes(self, text: str, n: int = 2) -> List[str]:
        sentences = self._extract_sentences(text)
        # pick longer ones to resemble quotes
        ranked = sorted(sentences, key=lambda s: abs(140 - len(s)))
        chosen = []
        for s in ranked:
            if len(chosen) >= n:
                break
            if len(s) >= 80:
                chosen.append(s)
        return chosen[:n]

    def _extract_concepts(self, text: str, max_concepts: int = 10) -> List[str]:
        patterns = [r"\b[A-Z][a-z]+(?:[A-Z][a-z]+)*\b", r"\b[A-Z]{2,}\b", r"`([^`]+)`", r"\*\*([^*]+)\*\*", r"##+ (.+)"]
        concepts: List[str] = []
        for p in patterns:
            concepts.extend(re.findall(p, text))
        seen, out = set(), []
        stop = {"the", "and", "or", "but", "for", "with", "this", "that", "from"}
        for c in concepts:
            c = c.strip()
            if len(c) > 2 and c.lower() not in stop and c not in seen and not c.isdigit():
                out.append(c)
                seen.add(c)
        return out[:max_concepts]

    def _decide_category(self, tags: List[str]) -> str:
        # Merge built-in and user mapping (user overrides)
        merged = dict(self.TAG_CATEGORY_RULES)
        merged.update(self.user_mapping or {})
        score: Dict[str, int] = {}
        for t in tags:
            key = t.lower()
            if key in merged:
                cat = merged[key]
                score[cat] = score.get(cat, 0) + 1
        if not score:
            if self.teach:
                print("[teach] No category match → Drafts")
            return self.DEFAULT_CATEGORY
        best = max(score.items(), key=lambda kv: kv[1])[0]
        if self.teach:
            print(f"[teach] Category decision: {score} → {best}")
        return best

    # --------------------
    # Markdown + Index
    # --------------------
    def _write_summary(self, slug: str, data: Dict[str, Any]) -> Path:
        md_path = self.summaries_dir / f"{slug}.md"
        if self.dry_run:
            return md_path
        # Create frontmatter from template fields
        today = datetime.now().strftime("%Y-%m-%d")
        frontmatter = [
            "---",
            "# Generated by Scraper AI-Research Importer",
            f"title: {data['title']}",
            f"source: {data['source']}",
            "authors: []",
            "published_at: unknown",
            f"publisher: {data['publisher']}",
            f"source_type: {data['source_type'] or 'site'}",
            "license:",
            f"edition: {self.edition}",
            f"tags: [{', '.join(data['tags_final'])}]",
            f"concepts: [{', '.join(data['concepts'])}]",
            f"related: []",
            "status: todo",
            f"date_added: {today}",
            "---",
            "",
            "summary:",
        ]
        for b in data["bullets"]:
            frontmatter.append(f"- {b}")
        frontmatter.append("")
        frontmatter.append("key_quotes:")
        for q in data["quotes"]:
            frontmatter.append(f"- \"{q}\"")
        frontmatter.append("")
        frontmatter.append("ideas_to_try:")
        frontmatter.append("- ")
        frontmatter.append("- ")
        frontmatter.append("")
        frontmatter.append("links:")
        frontmatter.append("- url: {}".format(data["source"]))
        frontmatter.append("  note: source")
        content = "\n".join(frontmatter) + "\n"
        with open(md_path, "w") as f:
            f.write(content)
        return md_path

    def _update_index(self, title: str, url: str, slug: str, tags: List[str], category: str) -> bool:
        if self.dry_run:
            return False
        if not self.index_md.exists():
            return False
        try:
            with open(self.index_md, "r") as f:
                lines = f.readlines()
            # Avoid duplicate slug
            joined = "".join(lines)
            if slug in joined:
                return False
            row = f"- {title} | {url} | [{', '.join(tags)}] | {self.edition} | todo | {slug} | {datetime.now().strftime('%Y-%m-%d')}\n"
            # Find category header line index
            cat_idx = -1
            for i, line in enumerate(lines):
                txt = line.strip()
                if txt == category or txt.endswith(category) or txt == f"{category}" or (txt and category in txt and txt[0].isdigit() and ")" in txt):
                    cat_idx = i
                    break
            if cat_idx == -1:
                # try Drafts
                for i, line in enumerate(lines):
                    if line.strip().lower().startswith("drafts"):
                        cat_idx = i
                        break
            if cat_idx == -1:
                # append at end
                lines.append("\nDrafts\n")
                lines.append(row)
            else:
                # insert after the header line
                insert_at = cat_idx + 1
                lines.insert(insert_at, row)
            with open(self.index_md, "w") as f:
                f.writelines(lines)
            return True
        except Exception:
            return False

    # --------------------
    # Runner
    # --------------------
    def run(self, **kwargs) -> Dict[str, Any]:
        items = self._load_content()
        created, skipped = 0, 0
        results: List[Dict[str, Any]] = []
        for it in items:
            title = it["title"] or _domain_from_url(it["source_url"]) or "Untitled"
            domain = _domain_from_url(it["source_url"]) or ""
            base_slug = _slugify(f"{domain}-{title}")
            slug = base_slug
            # idempotency on file existence
            md_path = self.summaries_dir / f"{slug}.md"
            if md_path.exists():
                skipped += 1
                continue
            tags_raw = [t for t in (it.get("tags") or []) if isinstance(t, str)]
            # ensure edition tag present
            tags_final = list({*tags_raw, f"edition:{self.edition}"})
            category = self._decide_category(tags_final)
            bullets = self._extract_bullets(it.get("content", ""), 5)
            quotes = self._extract_quotes(it.get("content", ""), 2)
            concepts = self._extract_concepts(it.get("content", ""), 7)
            payload = {
                "title": title,
                "source": it["source_url"],
                "publisher": domain or "",
                "source_type": it.get("source_type") or "site",
                "tags_final": tags_final,
                "concepts": concepts,
                "bullets": bullets,
                "quotes": quotes,
                "category": category,
            }
            # write summary
            out_md = self._write_summary(slug, payload)
            # update index
            self._update_index(title, it["source_url"], slug, tags_final, category)
            created += 1
            results.append({"slug": slug, "file": str(out_md), "category": category})
        return {
            "db": str(self.db_path),
            "repo": str(self.repo_path),
            "created": created,
            "skipped": skipped,
            "items": results,
            "dry_run": self.dry_run,
        }
