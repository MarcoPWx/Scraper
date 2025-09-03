#!/usr/bin/env python3
"""
Massive Harvester module extracted from QuizMentor.ai scripts/python/local_harvester.py
"""

from __future__ import annotations

import json
import csv
import sqlite3
import hashlib
import time
import re
import random
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
from collections import defaultdict
from pathlib import Path

# Web scraping
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import feedparser  # noqa: F401 (kept for future RSS sources)

# Data processing
import pandas as pd
from fuzzywuzzy import fuzz

# Progress tracking
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

console = Console()


@dataclass
class HarvestedContent:
    source_url: str
    source_type: str  # documentation, blog, github, stackoverflow, etc.
    title: str
    content: str
    category: str
    subcategory: str
    tags: List[str]
    scraped_at: str
    quality_score: float


@dataclass
class QuestionCandidate:
    question: str
    options: List[str]
    correct_answer: int
    explanation: str
    source: str
    category: str
    subcategory: str
    difficulty: int
    confidence: float
    fingerprint: str  # For uniqueness checking


class MassiveHarvester:
    """Massive content harvester for quiz and learning content generation"""

    def __init__(self, output_dir: str = "./harvest_output", teach: bool = False):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Database for tracking
        self.db_path = self.output_dir / "harvest.db"
        self._init_database()

        # Caches and stats
        self.url_cache = set()
        self.content_cache: Dict[str, str] = {}
        self.question_fingerprints = set()
        self.stats = defaultdict(int)
        self.teach = teach
        # SimHash dedupe (in-memory, per-run)
        self._simhashes: List[int] = []
        self._simhash_threshold: int = 8

        # HTTP session
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Scraper/0.1) Educational Content Collector",
        })

    # -----------------
    # Database schema
    # -----------------
    def _init_database(self) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS harvested_content (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_url TEXT UNIQUE,
                source_type TEXT,
                title TEXT,
                content TEXT,
                category TEXT,
                subcategory TEXT,
                tags TEXT,
                scraped_at TIMESTAMP,
                quality_score REAL,
                processed BOOLEAN DEFAULT FALSE
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS generated_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fingerprint TEXT UNIQUE,
                question TEXT,
                options TEXT,
                correct_answer INTEGER,
                explanation TEXT,
                category TEXT,
                subcategory TEXT,
                difficulty INTEGER,
                confidence REAL,
                source TEXT,
                created_at TIMESTAMP,
                validated BOOLEAN DEFAULT FALSE,
                deployed BOOLEAN DEFAULT FALSE
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS harvest_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP,
                urls_scraped INTEGER,
                content_harvested INTEGER,
                questions_generated INTEGER,
                unique_questions INTEGER,
                categories_covered INTEGER,
                quality_avg REAL
            )
            """
        )

        conn.commit()
        conn.close()

    # -----------------
    # Source discovery
    # -----------------
    def get_massive_source_list(self) -> Dict[str, List[Dict]]:
        """Return a dictionary of curated sources to harvest."""
        sources = {
            "documentation": [
                {"name": "AWS", "urls": [
                    "https://docs.aws.amazon.com/ec2/",
                    "https://docs.aws.amazon.com/lambda/",
                    "https://docs.aws.amazon.com/s3/",
                    "https://docs.aws.amazon.com/dynamodb/",
                    "https://docs.aws.amazon.com/rds/",
                    "https://docs.aws.amazon.com/ecs/",
                    "https://docs.aws.amazon.com/eks/",
                    "https://docs.aws.amazon.com/cloudformation/",
                ]},
                {"name": "Azure", "urls": [
                    "https://docs.microsoft.com/azure/virtual-machines/",
                    "https://docs.microsoft.com/azure/app-service/",
                    "https://docs.microsoft.com/azure/storage/",
                    "https://docs.microsoft.com/azure/cosmos-db/",
                    "https://docs.microsoft.com/azure/aks/",
                ]},
                {"name": "GCP", "urls": [
                    "https://cloud.google.com/compute/docs",
                    "https://cloud.google.com/functions/docs",
                    "https://cloud.google.com/storage/docs",
                    "https://cloud.google.com/kubernetes-engine/docs",
                ]},
                {"name": "Kubernetes", "urls": [
                    "https://kubernetes.io/docs/concepts/",
                    "https://kubernetes.io/docs/tasks/",
                    "https://kubernetes.io/docs/tutorials/",
                ]},
                {"name": "Docker", "urls": [
                    "https://docs.docker.com/engine/",
                    "https://docs.docker.com/compose/",
                    "https://docs.docker.com/registry/",
                ]},
                {"name": "Python", "urls": [
                    "https://docs.python.org/3/tutorial/",
                    "https://docs.python.org/3/library/",
                ]},
                {"name": "JavaScript", "urls": [
                    "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide",
                    "https://nodejs.org/en/docs/",
                ]},
                {"name": "Go", "urls": [
                    "https://go.dev/doc/effective_go",
                    "https://go.dev/doc/tutorial/",
                ]},
                {"name": "PostgreSQL", "urls": [
                    "https://www.postgresql.org/docs/current/tutorial.html",
                ]},
                {"name": "MongoDB", "urls": [
                    "https://www.mongodb.com/docs/manual/",
                ]},
                {"name": "Redis", "urls": [
                    "https://redis.io/docs/",
                ]},
                {"name": "Terraform", "urls": [
                    "https://developer.hashicorp.com/terraform/docs",
                ]},
                {"name": "Ansible", "urls": [
                    "https://docs.ansible.com/ansible/latest/",
                ]},
                {"name": "Jenkins", "urls": [
                    "https://www.jenkins.io/doc/",
                ]},
            ],
            "tutorials": [
                "https://www.tutorialspoint.com/index.htm",
                "https://www.w3schools.com/",
                "https://www.geeksforgeeks.org/",
                "https://www.baeldung.com/",
                "https://realpython.com/",
            ],
            "blogs": [
                "https://engineering.fb.com/",
                "https://netflixtechblog.com/",
                "https://aws.amazon.com/blogs/aws/",
                "https://cloud.google.com/blog/",
                "https://github.blog/",
                "https://stackoverflow.blog/",
            ],
            "github_awesome_lists": [
                "https://github.com/sindresorhus/awesome",
                "https://github.com/vinta/awesome-python",
                "https://github.com/sorrycc/awesome-javascript",
                "https://github.com/avelino/awesome-go",
                "https://github.com/dastergon/awesome-reliability",
                "https://github.com/mfornos/awesome-microservices",
            ],
            "stackoverflow_tags": [
                "python", "javascript", "java", "c#", "php", "android", "ios",
                "sql", "r", "node.js", "c++", "typescript", "swift", "objective-c",
                "mongodb", "postgresql", "mysql", "redis", "elasticsearch",
                "docker", "kubernetes", "aws", "azure", "google-cloud-platform",
                "react", "angular", "vue.js", "django", "flask", "spring-boot",
                "machine-learning", "deep-learning", "data-science", "pandas", "numpy",
                "git", "linux", "bash", "powershell", "nginx", "apache",
                "terraform", "ansible", "jenkins", "ci-cd", "devops",
            ],
            "certification_topics": [
                "AWS Solutions Architect", "AWS Developer Associate", "AWS SysOps Administrator",
                "Azure Administrator", "Azure Developer", "Google Cloud Engineer",
                "Kubernetes CKA", "Kubernetes CKAD", "Docker DCA", "Terraform Associate",
                "Red Hat RHCSA", "CompTIA Security+", "CompTIA Network+", "CISSP", "PMP",
            ],
        }
        return sources

    # -----------------
    # Harvesters
    # -----------------
    def harvest_all_sources(self, max_workers: int = 10, limit_per_source: Optional[int] = None) -> List[HarvestedContent]:
        console.print("[bold green]Starting Massive Harvest Operation[/bold green]")
        sources = self.get_massive_source_list()
        all_content: List[HarvestedContent] = []

        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), BarColumn(), console=console) as progress:
            doc_task = progress.add_task("[cyan]Harvesting Documentation...", total=len(sources["documentation"]))
            for doc_source in sources["documentation"]:
                content = self.harvest_documentation_site(doc_source, limit_per_source)
                all_content.extend(content)
                progress.advance(doc_task)
                self.stats["documentation_sources"] += 1

            so_task = progress.add_task("[yellow]Harvesting Stack Overflow...", total=len(sources["stackoverflow_tags"]))
            for tag in sources["stackoverflow_tags"][:20]:
                content = self.harvest_stackoverflow(tag, limit=limit_per_source or 50)
                all_content.extend(content)
                progress.advance(so_task)
                self.stats["stackoverflow_tags"] += 1

            gh_task = progress.add_task("[magenta]Harvesting GitHub...", total=len(sources["github_awesome_lists"]))
            for repo_url in sources["github_awesome_lists"]:
                content = self.harvest_github_repo(repo_url)
                if content:
                    all_content.append(content)
                progress.advance(gh_task)
                self.stats["github_repos"] += 1

        self.save_harvested_content(all_content)
        console.print(f"[bold green]✓ Harvested {len(all_content)} pieces of content[/bold green]")
        return all_content

    def harvest_documentation_site(self, doc_source: Dict, limit: Optional[int] = None) -> List[HarvestedContent]:
        harvested: List[HarvestedContent] = []
        name = doc_source["name"]

        for url in doc_source["urls"][:limit] if limit else doc_source["urls"]:
            try:
                console.print(f"  Scraping {name}: {url}")
                response = self.session.get(url, timeout=10)
                soup = BeautifulSoup(response.content, "html.parser")
                content = self.extract_documentation_content(soup)
                if content and len(content) > 500:
                    harvested_item = HarvestedContent(
                        source_url=url,
                        source_type="documentation",
                        title=soup.find("title").text if soup.find("title") else name,
                        content=content,
                        category=name.lower(),
                        subcategory=self.extract_subcategory(url),
                        tags=self.extract_tags(content),
                        scraped_at=datetime.now().isoformat(),
                        quality_score=self.assess_content_quality(content),
                    )
                    harvested.append(harvested_item)
                    self.stats["pages_scraped"] += 1
                time.sleep(0.5)
            except Exception as e:  # pragma: no cover
                console.print(f"[red]Error harvesting {url}: {e}[/red]")
                continue
        return harvested

    def harvest_stackoverflow(self, tag: str, limit: int = 50) -> List[HarvestedContent]:
        harvested: List[HarvestedContent] = []
        try:
            api_url = "https://api.stackexchange.com/2.3/questions"
            params = {"order": "desc", "sort": "votes", "tagged": tag, "site": "stackoverflow", "filter": "withbody", "pagesize": min(limit, 100)}
            response = requests.get(api_url, params=params)
            data = response.json()
            for item in data.get("items", []):
                content = BeautifulSoup(item.get("body", ""), "html.parser").get_text()
                harvested_item = HarvestedContent(
                    source_url=item["link"],
                    source_type="stackoverflow",
                    title=item["title"],
                    content=content,
                    category="programming",
                    subcategory=tag,
                    tags=item.get("tags", []),
                    scraped_at=datetime.now().isoformat(),
                    quality_score=min(item.get("score", 0) / 100, 1.0),
                )
                harvested.append(harvested_item)
        except Exception as e:  # pragma: no cover
            console.print(f"[red]Error harvesting Stack Overflow {tag}: {e}[/red]")
        return harvested

    def harvest_github_repo(self, repo_url: str) -> Optional[HarvestedContent]:
        try:
            parts = repo_url.replace("https://github.com/", "").split("/")
            if len(parts) >= 2:
                owner, repo = parts[0], parts[1]
                readme_urls = [
                    f"https://raw.githubusercontent.com/{owner}/{repo}/main/README.md",
                    f"https://raw.githubusercontent.com/{owner}/{repo}/master/README.md",
                    f"https://raw.githubusercontent.com/{owner}/{repo}/main/readme.md",
                ]
                for readme_url in readme_urls:
                    response = requests.get(readme_url)
                    if response.status_code == 200:
                        return HarvestedContent(
                            source_url=repo_url,
                            source_type="github",
                            title=f"{owner}/{repo}",
                            content=response.text,
                            category="repository",
                            subcategory=repo,
                            tags=self.extract_tags(response.text),
                            scraped_at=datetime.now().isoformat(),
                            quality_score=0.8,
                        )
        except Exception as e:  # pragma: no cover
            console.print(f"[red]Error harvesting GitHub {repo_url}: {e}[/red]")
        return None

    # -----------------
    # Question generation
    # -----------------
    def generate_questions_from_content(self, content_list: List[HarvestedContent], questions_per_content: int = 5) -> List[QuestionCandidate]:
        all_questions: List[QuestionCandidate] = []
        console.print("[bold cyan]Generating Questions from Content...[/bold cyan]")
        for content in content_list:
            concepts = self.extract_key_concepts(content.content)
            if self.teach and concepts:
                console.print(f"[yellow]Concepts extracted (top){' '}: {concepts[:min(5,len(concepts))]}[/yellow]")
            for concept in concepts[:questions_per_content]:
                question = self.generate_question_for_concept(concept, content.content, content.category, content.subcategory)
                if not question:
                    continue
                # Levenshtein-based uniqueness
                if not self.is_unique_question(question):
                    if self.teach:
                        console.print(f"[red]Rejected (Levenshtein similarity > 0.85):[/red] {question.question}")
                    continue
                # SimHash near-duplicate check
                simh = self._simhash64(question.question)
                nearest = min((self._hamming(simh, h) for h in self._simhashes), default=64)
                if nearest < self._simhash_threshold:
                    if self.teach:
                        console.print(f"[red]Using SimHash dedupe[/red] distance={nearest} < {self._simhash_threshold} → skip")
                    continue
                self._simhashes.append(simh)
                if self.teach:
                    console.print(f"[green]Accepted[/green] diff={question.difficulty} src={question.source} fp={question.fingerprint[:8]}…")
                all_questions.append(question)
                self.stats["questions_generated"] += 1
        return all_questions

    def extract_key_concepts(self, text: str, max_concepts: int = 20) -> List[str]:
        concepts: List[str] = []
        patterns = [r"\b[A-Z][a-z]+(?:[A-Z][a-z]+)*\b", r"\b[A-Z]{2,}\b", r"`([^`]+)`", r"\*\*([^*]+)\*\*", r"##+ (.+)"]
        for pattern in patterns:
            concepts.extend(re.findall(pattern, text))
        seen = set()
        filtered = []
        for concept in concepts:
            concept = concept.strip()
            if len(concept) > 2 and concept not in seen and concept.lower() not in {"the", "and", "or", "but", "for"}:
                filtered.append(concept)
                seen.add(concept)
        return filtered[:max_concepts]

    def generate_question_for_concept(self, concept: str, context: str, category: str, subcategory: str) -> Optional[QuestionCandidate]:
        templates = {
            "definition": [f"What is {concept}?", f"Which of the following best describes {concept}?", f"In {category}, what does {concept} refer to?"],
            "purpose": [f"What is the primary purpose of {concept}?", f"Why would you use {concept} in {subcategory}?", f"What problem does {concept} solve?"],
            "comparison": [f"How does {concept} differ from alternatives?", f"What is the main advantage of {concept}?", f"When should you use {concept}?"],
            "implementation": [f"How is {concept} typically implemented?", f"What is required to use {concept}?", f"Which approach is best for {concept}?"],
        }
        q_type = random.choice(list(templates.keys()))
        question_text = random.choice(templates[q_type])
        correct_answer = self.extract_answer_from_context(concept, context, q_type)
        if not correct_answer:
            return None
        distractors = self.generate_smart_distractors(concept, correct_answer, category, q_type)
        if len(distractors) < 3:
            return None
        options = [correct_answer] + distractors[:3]
        random.shuffle(options)
        correct_index = options.index(correct_answer)
        explanation = self.generate_explanation(concept, correct_answer, context)
        fingerprint = hashlib.md5(f"{question_text}{sorted(options)}".encode()).hexdigest()
        return QuestionCandidate(
            question=question_text,
            options=options,
            correct_answer=correct_index,
            explanation=explanation,
            source=subcategory,
            category=category,
            subcategory=subcategory,
            difficulty=self.assess_difficulty(question_text, options),
            confidence=0.8,
            fingerprint=fingerprint,
        )

    def extract_answer_from_context(self, concept: str, context: str, q_type: str) -> Optional[str]:
        sentences = context.split(".")
        relevant = [s for s in sentences if concept in s]
        if not relevant:
            return None
        best = max(relevant, key=lambda s: len(s.split()))[:150]
        if q_type == "definition":
            if not best.startswith(("A ", "An ", "The ")):
                best = f"A {best.lower()}"
        return best.strip()

    def generate_smart_distractors(self, concept: str, correct: str, category: str, q_type: str) -> List[str]:
        category_distractors = {
            "aws": ["An EC2 instance type", "A Lambda function trigger", "An S3 storage class", "A VPC component"],
            "kubernetes": ["A Pod controller", "A Service type", "A Volume plugin", "A Network policy"],
            "docker": ["A container runtime", "An image layer", "A compose directive", "A registry feature"],
            "python": ["A built-in function", "A standard library module", "A data structure", "A decorator pattern"],
            "database": ["A query optimization", "An index type", "A transaction level", "A replication method"],
        }
        base_distractors = category_distractors.get(category, [
            f"A different approach to {concept}", f"An alternative to {concept}", f"A component of {concept}", f"A prerequisite for {concept}",
        ])
        distractors: List[str] = []
        target_len = len(correct)
        for d in base_distractors:
            if len(d) < target_len * 0.5:
                d += " with additional configuration"
            elif len(d) > target_len * 1.5:
                d = d[: int(target_len * 1.2)] + "..."
            distractors.append(d)
        return distractors[:4]

    def generate_explanation(self, concept: str, answer: str, context: str) -> str:
        explanation = f"{concept} is correctly described as: {answer[:100]}"
        sentences = context.split(".")
        relevant = [s for s in sentences if concept in s and answer[:20] in s]
        if relevant:
            explanation = relevant[0].strip()[:200]
        return explanation

    def assess_difficulty(self, question: str, options: List[str]) -> int:
        complexity_score = 0
        if len(question.split()) > 15:
            complexity_score += 1
        if any(word in question.lower() for word in ["explain", "compare", "analyze", "evaluate"]):
            complexity_score += 1
        avg_option_length = sum(len(opt) for opt in options) / len(options)
        if avg_option_length > 50:
            complexity_score += 1
        if self.calculate_option_similarity(options) > 0.6:
            complexity_score += 1
        return min(complexity_score + 1, 5)

    def calculate_option_similarity(self, options: List[str]) -> float:
        if len(options) < 2:
            return 0.0
        similarities: List[float] = []
        for i in range(len(options)):
            for j in range(i + 1, len(options)):
                sim = fuzz.ratio(options[i], options[j]) / 100
                similarities.append(sim)
        return sum(similarities) / len(similarities) if similarities else 0.0

    def is_unique_question(self, question: QuestionCandidate, threshold: float = 0.85) -> bool:
        if question.fingerprint in self.question_fingerprints:
            if self.teach:
                console.print("[red]Duplicate fingerprint found → skip[/red]")
            return False
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT question, options FROM generated_questions
            WHERE category = ? AND subcategory = ?
            """,
            (question.category, question.subcategory),
        )
        existing = cursor.fetchall()
        conn.close()
        for existing_q, _ in existing:
            similarity = fuzz.ratio(question.question, existing_q) / 100
            if similarity > threshold:
                if self.teach:
                    console.print(f"[red]Levenshtein ratio {similarity:.2f} > {threshold:.2f} (not unique)[/red]")
                return False
        self.question_fingerprints.add(question.fingerprint)
        return True

    # -----------------
    # SimHash helpers
    # -----------------
    def _trigrams(self, text: str) -> List[str]:
        s = text.lower()
        return [s[i:i+3] for i in range(max(0, len(s)-2))]

    def _simhash64(self, text: str) -> int:
        vec = [0] * 64
        for tg in self._trigrams(text):
            h = int.from_bytes(hashlib.md5(tg.encode()).digest()[:8], 'big')
            for b in range(64):
                if (h >> b) & 1:
                    vec[b] += 1
                else:
                    vec[b] -= 1
        out = 0
        for b in range(64):
            if vec[b] > 0:
                out |= (1 << b)
        return out

    def _hamming(self, a: int, b: int) -> int:
        return (a ^ b).bit_count()

    # -----------------
    # Persistence & reports
    # -----------------
    def save_harvested_content(self, content_list: List[HarvestedContent]) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        for content in content_list:
            try:
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO harvested_content
                    (source_url, source_type, title, content, category, subcategory, tags, scraped_at, quality_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        content.source_url,
                        content.source_type,
                        content.title,
                        content.content,
                        content.category,
                        content.subcategory,
                        json.dumps(content.tags),
                        content.scraped_at,
                        content.quality_score,
                    ),
                )
            except Exception as e:  # pragma: no cover
                console.print(f"[red]Error saving content: {e}[/red]")
        conn.commit()
        conn.close()

    def save_questions(self, questions: List[QuestionCandidate]) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        for q in questions:
            try:
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO generated_questions
                    (fingerprint, question, options, correct_answer, explanation,
                     category, subcategory, difficulty, confidence, source, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        q.fingerprint,
                        q.question,
                        json.dumps(q.options),
                        q.correct_answer,
                        q.explanation,
                        q.category,
                        q.subcategory,
                        q.difficulty,
                        q.confidence,
                        q.source,
                        datetime.now().isoformat(),
                    ),
                )
            except Exception as e:  # pragma: no cover
                console.print(f"[red]Error saving question: {e}[/red]")
        conn.commit()
        conn.close()

    def generate_csv_report(self, output_file: Optional[str] = None) -> Path:
        if not output_file:
            output_file = self.output_dir / f"quiz_harvest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query(
            """
            SELECT * FROM generated_questions
            ORDER BY category, subcategory, difficulty
            """,
            conn,
        )
        conn.close()
        df["options"] = df["options"].apply(json.loads)
        df["option_1"], df["option_2"], df["option_3"], df["option_4"] = (
            df["options"].apply(lambda x: x[0] if len(x) > 0 else ""),
            df["options"].apply(lambda x: x[1] if len(x) > 1 else ""),
            df["options"].apply(lambda x: x[2] if len(x) > 2 else ""),
            df["options"].apply(lambda x: x[3] if len(x) > 3 else ""),
        )
        export_columns = [
            "id",
            "category",
            "subcategory",
            "difficulty",
            "question",
            "option_1",
            "option_2",
            "option_3",
            "option_4",
            "correct_answer",
            "explanation",
            "confidence",
            "source",
            "created_at",
        ]
        df_export = df[export_columns]
        df_export.to_csv(output_file, index=False)
        console.print(f"[green]✓ Exported {len(df_export)} questions to {output_file}[/green]")
        return Path(output_file)

    def generate_statistics_report(self) -> Dict:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        stats: Dict[str, object] = {}
        cursor.execute("SELECT COUNT(*) FROM harvested_content")
        stats["total_content"] = cursor.fetchone()[0]
        cursor.execute("SELECT source_type, COUNT(*) FROM harvested_content GROUP BY source_type")
        stats["content_by_type"] = dict(cursor.fetchall())
        cursor.execute("SELECT category, COUNT(*) FROM harvested_content GROUP BY category")
        stats["content_by_category"] = dict(cursor.fetchall())
        cursor.execute("SELECT COUNT(*) FROM generated_questions")
        stats["total_questions"] = cursor.fetchone()[0]
        cursor.execute("SELECT category, COUNT(*) FROM generated_questions GROUP BY category")
        stats["questions_by_category"] = dict(cursor.fetchall())
        cursor.execute("SELECT difficulty, COUNT(*) FROM generated_questions GROUP BY difficulty")
        stats["questions_by_difficulty"] = dict(cursor.fetchall())
        cursor.execute("SELECT AVG(confidence) FROM generated_questions")
        stats["average_confidence"] = cursor.fetchone()[0]
        conn.close()

        table = Table(title="Harvest Statistics Report")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        table.add_row("Total Content Harvested", str(stats.get("total_content", 0)))
        table.add_row("Total Questions Generated", str(stats.get("total_questions", 0)))
        table.add_row("Average Confidence", f"{stats.get('average_confidence', 0):.2f}")
        table.add_row("", "")
        table.add_row("[bold]Content by Type[/bold]", "")
        for content_type, count in stats.get("content_by_type", {}).items():
            table.add_row(f"  {content_type}", str(count))
        table.add_row("", "")
        table.add_row("[bold]Questions by Category[/bold]", "")
        for category, count in sorted(stats.get("questions_by_category", {}).items(), key=lambda x: x[1], reverse=True)[:10]:
            table.add_row(f"  {category}", str(count))
        table.add_row("", "")
        table.add_row("[bold]Difficulty Distribution[/bold]", "")
        for difficulty in range(1, 6):
            count = stats.get("questions_by_difficulty", {}).get(difficulty, 0)
            bar = "█" * (count // 10) if count > 0 else ""
            table.add_row(f"  Level {difficulty}", f"{count} {bar}")
        console.print(table)
        return stats

    # -----------------
    # Orchestration
    # -----------------
    def run_complete_harvest(self, max_content: int = 1000, questions_per_content: int = 5, parallel_workers: int = 10) -> Dict:
        console.print("""
[bold cyan]╔══════════════════════════════════════════════════════════╗
║           MASSIVE QUIZ CONTENT HARVESTER                  ║
║  Documentation • StackOverflow • GitHub • Tutorials       ║
╚══════════════════════════════════════════════════════════╝[/bold cyan]
""")
        start_time = time.time()
        content = self.harvest_all_sources(max_workers=parallel_workers, limit_per_source=max_content // 20)
        questions = self.generate_questions_from_content(content, questions_per_content)
        self.save_questions(questions)
        csv_file = self.generate_csv_report()
        stats = self.generate_statistics_report()
        elapsed = time.time() - start_time
        console.print(f"""
[bold green]╔══════════════════════════════════════════════════════════╗
║                    HARVEST COMPLETE!                      ║
╠══════════════════════════════════════════════════════════╣
║  Content Harvested: {stats.get('total_content', 0):,}                     
║  Questions Generated: {stats.get('total_questions', 0):,}                  
║  Categories Covered: {len(stats.get('questions_by_category', {})):,}        
║  Time Elapsed: {elapsed/60:.1f} minutes                          
╚══════════════════════════════════════════════════════════╝[/bold green]
""")
        return {
            "content_harvested": stats.get("total_content", 0),
            "questions_generated": stats.get("total_questions", 0),
            "csv_file": str(csv_file),
            "database": str(self.db_path),
            "elapsed_time": elapsed,
        }

