#!/usr/bin/env python3
"""
Enhanced Harvester module extracted from QuizMentor.ai scripts/python/enhanced_harvester.py
"""

from __future__ import annotations

import json
import sqlite3
import hashlib
import time
import re
import random
import requests
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
from collections import defaultdict, Counter
from pathlib import Path
from urllib.parse import urlparse

# Data processing
import pandas as pd
import numpy as np  # noqa: F401
from fuzzywuzzy import fuzz
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Web scraping
from bs4 import BeautifulSoup
import feedparser  # noqa: F401

# Progress tracking
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.prompt import Confirm

console = Console()


@dataclass
class EnhancedQuestion:
    question: str
    options: List[str]
    correct_answer: int
    explanation: str
    category: str
    subcategory: str
    difficulty: int
    confidence: float
    source_url: str
    source_type: str
    distractor_quality: float
    answer_distribution: str
    semantic_fingerprint: str
    concepts: List[str]
    created_at: str


class EnhancedHarvester:
    """Enhanced harvester with better source management and quality control"""

    def __init__(self, output_dir: str = "./harvest_output", teach: bool = False):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        self.used_sources = set()
        self.source_rotation = defaultdict(int)
        self.answer_distribution = Counter()
        self.semantic_cache: Dict[str, float] = {}
        self.teach = teach
        self.vectorizer = TfidfVectorizer(max_features=1000)
        self.question_vectors = None
        self.existing_questions: List[str] = []

        self.db_path = self.output_dir / "enhanced_harvest.db"
        self._init_enhanced_database()

        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Educational Quiz Harvester) AppleWebKit/537.36",
        })

    def _init_enhanced_database(self) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS enhanced_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                options TEXT NOT NULL,
                correct_answer INTEGER NOT NULL,
                explanation TEXT,
                category TEXT,
                subcategory TEXT,
                difficulty INTEGER,
                confidence REAL,
                source_url TEXT,
                source_type TEXT,
                distractor_quality REAL,
                answer_distribution TEXT,
                semantic_fingerprint TEXT UNIQUE,
                concepts TEXT,
                created_at TIMESTAMP,
                UNIQUE(semantic_fingerprint)
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS source_usage (
                source_url TEXT PRIMARY KEY,
                last_used TIMESTAMP,
                times_used INTEGER DEFAULT 0,
                questions_generated INTEGER DEFAULT 0
            )
            """
        )
        conn.commit()
        conn.close()

    def get_expanded_sources(self) -> Dict[str, List]:
        sources = {
            "documentation": {
                "cloud": [
                    "https://docs.aws.amazon.com/vpc/",
                    "https://docs.aws.amazon.com/sqs/",
                    "https://docs.aws.amazon.com/sns/",
                    "https://docs.aws.amazon.com/kinesis/",
                    "https://docs.aws.amazon.com/elasticache/",
                    "https://docs.aws.amazon.com/redshift/",
                    "https://docs.microsoft.com/azure/devops/",
                    "https://docs.microsoft.com/azure/logic-apps/",
                    "https://docs.microsoft.com/azure/functions/",
                    "https://docs.microsoft.com/azure/sql-database/",
                    "https://cloud.google.com/bigquery/docs",
                    "https://cloud.google.com/dataflow/docs",
                    "https://cloud.google.com/pubsub/docs",
                    "https://cloud.google.com/ml-engine/docs",
                ],
                "languages": [
                    "https://docs.djangoproject.com/",
                    "https://flask.palletsprojects.com/",
                    "https://fastapi.tiangolo.com/",
                    "https://numpy.org/doc/",
                    "https://pandas.pydata.org/docs/",
                    "https://reactjs.org/docs/",
                    "https://vuejs.org/guide/",
                    "https://angular.io/docs",
                    "https://expressjs.com/",
                    "https://spring.io/docs",
                    "https://docs.oracle.com/javase/",
                    "https://doc.rust-lang.org/book/",
                    "https://en.cppreference.com/",
                ],
                "databases": [
                    "https://dev.mysql.com/doc/",
                    "https://mariadb.com/kb/",
                    "https://cassandra.apache.org/doc/",
                    "https://neo4j.com/docs/",
                    "https://www.elastic.co/guide/",
                    "https://clickhouse.com/docs/",
                ],
                "devops": [
                    "https://www.vaultproject.io/docs",
                    "https://www.consul.io/docs",
                    "https://prometheus.io/docs/",
                    "https://grafana.com/docs/",
                    "https://www.packer.io/docs",
                    "https://helm.sh/docs/",
                    "https://istio.io/latest/docs/",
                    "https://linkerd.io/docs/",
                ],
                "security": [
                    "https://owasp.org/www-project-top-ten/",
                    "https://portswigger.net/web-security",
                ],
                "ml_ai": [
                    "https://scikit-learn.org/stable/",
                    "https://pytorch.org/docs/",
                    "https://www.tensorflow.org/api_docs",
                ],
            },
            "tutorials": [
                "https://www.digitalocean.com/community/tutorials",
                "https://www.linode.com/docs/",
                "https://learn.microsoft.com/",
                "https://developers.google.com/learn",
                "https://aws.amazon.com/getting-started/",
                "https://www.freecodecamp.org/learn/",
            ],
            "stackoverflow_tags": [
                "rust", "kotlin", "scala", "haskell", "erlang", "elixir",
                "nextjs", "nuxtjs", "nestjs", "fastify", "graphql", "grpc",
                "cloudflare", "digitalocean", "linode", "vultr", "heroku",
                "cockroachdb", "timescaledb", "influxdb", "dynamodb",
                "sre", "observability", "chaos-engineering", "gitops",
                "penetration-testing", "cryptography", "oauth2", "jwt",
                "apache-spark", "apache-kafka", "apache-flink", "databricks",
                "flutter", "react-native", "xamarin", "swiftui",
            ],
            "github_repos": [
                "https://github.com/donnemartin/system-design-primer",
                "https://github.com/binhnguyennus/awesome-scalability",
                "https://github.com/yangshun/tech-interview-handbook",
                "https://github.com/jwasham/coding-interview-university",
                "https://github.com/goldbergyoni/nodebestpractices",
                "https://github.com/airbnb/javascript",
                "https://github.com/DovAmir/awesome-design-patterns",
                "https://github.com/simskij/awesome-software-architecture",
            ],
            "certification_guides": [
                "AWS Certified Solutions Architect Professional",
                "Google Cloud Professional Cloud Architect",
                "Azure Solutions Architect Expert",
                "Certified Kubernetes Security Specialist",
                "HashiCorp Certified Terraform Associate",
                "Certified Ethical Hacker",
                "CCNA", "CCNP", "CISSP",
            ],
        }
        return sources

    def check_semantic_uniqueness(self, question: str, threshold: float = 0.85) -> bool:
        if not self.existing_questions:
            return True
        if self.question_vectors is None and self.existing_questions:
            self.question_vectors = self.vectorizer.fit_transform(self.existing_questions)
        try:
            new_vector = self.vectorizer.transform([question])
            similarities = cosine_similarity(new_vector, self.question_vectors)
            max_similarity = similarities.max()
            if self.teach:
                console.print(f"[blue][teach §B. Heuristics][/blue] TF‑IDF cosine max={max_similarity:.2f} < {threshold:.2f} → {'unique' if max_similarity < threshold else 'not unique'}")
            return max_similarity < threshold
        except Exception:
            for existing in self.existing_questions[-100:]:
                if fuzz.ratio(question, existing) > 85:
                    if self.teach:
                        console.print("[red]Fallback Levenshtein > 85 → not unique[/red]")
                    return False
            if self.teach:
                console.print("[green]Fallback uniqueness passed[/green]")
            return True

    def generate_quality_distractors(self, correct_answer: str, concept: str, category: str, context: str) -> List[str]:
        distractors: List[str] = []
        misconceptions = {
            "programming": {
                "loop": ["infinite recursion", "stack overflow", "memory leak"],
                "async": ["blocking operation", "synchronous call", "race condition"],
                "api": ["REST endpoint", "GraphQL query", "WebSocket connection"],
            },
            "cloud": {
                "storage": ["object storage", "block storage", "file storage"],
                "compute": ["virtual machine", "container", "serverless function"],
                "network": ["VPC", "subnet", "security group"],
            },
            "database": {
                "sql": ["SELECT", "INSERT", "UPDATE", "DELETE"],
                "nosql": ["document store", "key-value", "graph", "column-family"],
                "index": ["B-tree", "hash", "bitmap", "full-text"],
            },
        }
        patterns = [
            lambda x: x.replace("is", "is not"),
            lambda x: x.replace("can", "cannot"),
            lambda x: x.replace("synchronous", "asynchronous"),
            lambda x: x.replace("stateful", "stateless"),
            lambda x: x.replace("mutable", "immutable"),
            lambda x: x.replace("public", "private"),
            lambda x: x.replace("client", "server"),
        ]
        if category in misconceptions:
            for key in misconceptions[category]:
                if key in concept.lower():
                    distractors.extend(misconceptions[category][key])
        for pattern in patterns:
            try:
                variant = pattern(correct_answer)
                if variant != correct_answer and len(variant) > 5:
                    distractors.append(variant)
            except Exception:
                pass
        technical_terms = re.findall(r"\b[A-Z][a-z]+(?:[A-Z][a-z]+)*\b", context)
        for term in technical_terms:
            if term.lower() not in correct_answer.lower():
                distractors.append(f"A {term}-based solution")
        unique_distractors: List[str] = []
        for d in distractors:
            if d != correct_answer and d not in unique_distractors:
                if fuzz.ratio(d, correct_answer) < 70:
                    unique_distractors.append(d)
        generic_distractors = [
            "A legacy implementation that is deprecated",
            "An experimental feature not yet stable",
            "A third-party library solution",
            "A platform-specific implementation",
            "An enterprise-only feature",
            "A community-contributed module",
        ]
        random.shuffle(unique_distractors)
        random.shuffle(generic_distractors)
        final_distractors = unique_distractors[:3]
        if len(final_distractors) < 3:
            final_distractors.extend(generic_distractors[: 3 - len(final_distractors)])
        return final_distractors[:3]

    def balance_answer_distribution(self, correct_index: int) -> int:
        distribution = self.answer_distribution
        positions = [0, 1, 2, 3]
        position_counts = [distribution[p] for p in positions]
        if max(position_counts) - min(position_counts) > 20:
            return position_counts.index(min(position_counts))
        weights = [1.0 / (count + 1) for count in position_counts]
        return random.choices(positions, weights=weights)[0]

    def assess_distractor_quality(self, correct: str, distractors: List[str]) -> float:
        quality_score = 1.0
        lengths = [len(d) for d in distractors]
        if min(lengths, default=1) > 0 and max(lengths) / max(1, min(lengths)) > 3:
            quality_score -= 0.2
        for distractor in distractors:
            similarity = fuzz.ratio(correct, distractor)
            if similarity > 80:
                quality_score -= 0.3
            elif similarity < 20:
                quality_score -= 0.1
        for i, d1 in enumerate(distractors):
            for d2 in distractors[i + 1 :]:
                if fuzz.ratio(d1, d2) > 85:
                    quality_score -= 0.2
        generic_terms = ["something", "anything", "nothing", "everything", "stuff"]
        for distractor in distractors:
            if any(term in distractor.lower() for term in generic_terms):
                quality_score -= 0.2
        return max(0.0, min(1.0, quality_score))

    def harvest_with_rotation(self, max_content: int = 100) -> List[Dict]:
        sources = self.get_expanded_sources()
        harvested_content: List[Dict] = []
        console.print("[bold cyan]Starting Enhanced Harvest with Source Rotation[/bold cyan]")
        source_types = list(sources.keys())
        content_per_type = max(1, max_content // max(1, len(source_types)))
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), BarColumn(), console=console) as progress:
            for source_type in source_types:
                task = progress.add_task(f"[cyan]Harvesting {source_type}...", total=content_per_type)
                if source_type == "documentation":
                    for subcategory, urls in sources[source_type].items():
                        for url in urls:
                            if url not in self.used_sources:
                                content = self.harvest_documentation_enhanced(url, subcategory)
                                if content:
                                    harvested_content.extend(content)
                                    self.used_sources.add(url)
                                    progress.advance(task)
                                    if len(harvested_content) >= content_per_type:
                                        break
                        if len(harvested_content) >= content_per_type:
                            break
                elif source_type == "stackoverflow_tags":
                    for tag in sources[source_type]:
                        if f"so_{tag}" not in self.used_sources:
                            content = self.harvest_stackoverflow_enhanced(tag)
                            if content:
                                harvested_content.extend(content)
                                self.used_sources.add(f"so_{tag}")
                                progress.advance(task)
                                if len(harvested_content) >= content_per_type:
                                    break
                elif source_type == "github_repos":
                    for repo_url in sources[source_type]:
                        if repo_url not in self.used_sources:
                            content = self.harvest_github_enhanced(repo_url)
                            if content:
                                harvested_content.append(content)
                                self.used_sources.add(repo_url)
                                progress.advance(task)
                                if len(harvested_content) >= content_per_type:
                                    break
        return harvested_content

    def harvest_documentation_enhanced(self, url: str, category: str) -> List[Dict]:
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, "html.parser")
            content_sections: List[Dict] = []
            for selector in ["pre", "code", ".warning", ".note", ".important", "h2", "h3"]:
                elements = soup.select(selector)[:5]
                for elem in elements:
                    text = elem.get_text(strip=True)
                    if 50 < len(text) < 500:
                        content_sections.append({
                            "text": text,
                            "type": selector,
                            "url": url,
                            "category": category,
                        })
            return content_sections
        except Exception as e:  # pragma: no cover
            console.print(f"[red]Error harvesting {url}: {e}[/red]")
            return []

    def harvest_stackoverflow_enhanced(self, tag: str) -> List[Dict]:
        try:
            api_url = "https://api.stackexchange.com/2.3/questions"
            params = {
                "order": "desc",
                "sort": "votes",
                "tagged": tag,
                "site": "stackoverflow",
                "filter": "!9Z(-wwYGT",
                "pagesize": 10,
            }
            response = requests.get(api_url, params=params)
            data = response.json()
            content_sections: List[Dict] = []
            for item in data.get("items", []):
                if item.get("score", 0) > 5:
                    content_sections.append({
                        "text": BeautifulSoup(item.get("body", ""), "html.parser").get_text()[:500],
                        "title": item.get("title", ""),
                        "url": item.get("link", ""),
                        "category": "programming",
                        "subcategory": tag,
                        "score": item.get("score", 0),
                    })
            return content_sections
        except Exception as e:  # pragma: no cover
            console.print(f"[red]Error harvesting SO {tag}: {e}[/red]")
            return []

    def harvest_github_enhanced(self, repo_url: str) -> Optional[Dict]:
        try:
            parts = repo_url.replace("https://github.com/", "").split("/")
            if len(parts) >= 2:
                owner, repo = parts[0], parts[1]
                readme_urls = [
                    f"https://raw.githubusercontent.com/{owner}/{repo}/main/README.md",
                    f"https://raw.githubusercontent.com/{owner}/{repo}/master/README.md",
                ]
                for readme_url in readme_urls:
                    response = requests.get(readme_url)
                    if response.status_code == 200:
                        content = response.text
                        code_blocks = re.findall(r"```[\s\S]*?```", content)
                        return {
                            "text": content[:2000],
                            "code_examples": code_blocks[:3],
                            "url": repo_url,
                            "category": "repository",
                            "subcategory": repo,
                        }
        except Exception as e:  # pragma: no cover
            console.print(f"[red]Error harvesting GitHub {repo_url}: {e}[/red]")
        return None

    def generate_enhanced_question(self, content: Dict) -> Optional[EnhancedQuestion]:
        text = content.get("text", "")
        concepts = self.extract_concepts(text)
        if not concepts:
            return None
        concept = random.choice(concepts)
        question_templates = [
            f"What is the primary purpose of {concept}?",
            f"Which statement best describes {concept}?",
            f"In the context of {content.get('category', 'technology')}, what does {concept} do?",
            f"What is a key characteristic of {concept}?",
            f"How does {concept} differ from alternatives?",
            f"What problem does {concept} solve?",
            f"When should you use {concept}?",
            f"What is the main advantage of {concept}?",
        ]
        question_text = random.choice(question_templates)
        if not self.check_semantic_uniqueness(question_text):
            return None
        correct_answer = self.extract_answer_from_context(concept, text)
        if not correct_answer:
            return None
        distractors = self.generate_quality_distractors(correct_answer, concept, content.get("category", ""), text)
        options = [correct_answer] + distractors
        target_position = self.balance_answer_distribution(0)
        random.shuffle(distractors)
        final_options = distractors[:target_position] + [correct_answer] + distractors[target_position:]
        final_options = final_options[:4]
        while len(final_options) < 4:
            final_options.append("None of the above")
        correct_index = final_options.index(correct_answer)
        self.answer_distribution[correct_index] += 1
        explanation = f"{concept} is best understood as: {correct_answer}. "
        explanation += f"This is important in {content.get('category', 'this context')} because it "
        explanation += self.generate_explanation_detail(concept, text)
        distractor_quality = self.assess_distractor_quality(correct_answer, distractors)
        difficulty = self.assess_difficulty(concept, text, distractor_quality)
        confidence = 0.5 + (distractor_quality * 0.3) + (0.2 if len(concepts) > 3 else 0)
        if self.teach:
            console.print(f"[green]Quality[/green] q={distractor_quality:.2f} [green]Conf[/green]={confidence:.2f} [green]Diff[/green]={difficulty}")
        semantic_fingerprint = hashlib.sha256(f"{question_text}{sorted(final_options)}".encode()).hexdigest()
        self.existing_questions.append(question_text)
        return EnhancedQuestion(
            question=question_text,
            options=final_options,
            correct_answer=correct_index,
            explanation=explanation[:500],
            category=content.get("category", "general"),
            subcategory=content.get("subcategory", ""),
            difficulty=difficulty,
            confidence=confidence,
            source_url=content.get("url", ""),
            source_type=content.get("type", "documentation"),
            distractor_quality=distractor_quality,
            answer_distribution=f"ABCD"[correct_index],
            semantic_fingerprint=semantic_fingerprint,
            concepts=concepts[:5],
            created_at=datetime.now().isoformat(),
        )

    def extract_concepts(self, text: str) -> List[str]:
        concepts: List[str] = []
        patterns = [
            r"\b[A-Z][a-z]+(?:[A-Z][a-z]+)*\b",
            r"\b[A-Z]{2,}\b",
            r"`([^`]+)`",
            r"\*\*([^*]+)\*\*",
            r"class\s+(\w+)",
            r"function\s+(\w+)",
            r"def\s+(\w+)",
        ]
        for pattern in patterns:
            concepts.extend(re.findall(pattern, text))
        cleaned: List[str] = []
        stopwords = {"the", "and", "or", "but", "for", "with", "this", "that", "from", "will"}
        for concept in concepts:
            concept = concept.strip()
            if len(concept) > 2 and concept.lower() not in stopwords and not concept.isdigit():
                cleaned.append(concept)
        return list(set(cleaned))[:20]

    def extract_answer_from_context(self, concept: str, context: str) -> Optional[str]:
        sentences = context.split(".")
        relevant: List[str] = []
        for sentence in sentences:
            if concept.lower() in sentence.lower():
                cleaned = sentence.strip()
                if 20 < len(cleaned) < 200:
                    relevant.append(cleaned)
        if relevant:
            return max(relevant, key=lambda x: len(x.split()))
        return f"A {concept} implementation in this context"

    def generate_explanation_detail(self, concept: str, context: str) -> str:
        explanations = [
            "provides a solution for common challenges in this domain.",
            "enables better performance and scalability.",
            "follows industry best practices and standards.",
            "integrates well with other components in the system.",
            "offers a reliable and maintainable approach.",
        ]
        return random.choice(explanations)

    def assess_difficulty(self, concept: str, context: str, distractor_quality: float) -> int:
        if len(concept) < 5:
            base = 1
        elif any(char.isdigit() for char in concept) or concept.count("_") > 1 or concept.count("-") > 1:
            base = 3
        else:
            base = 2
        if len(context) > 1000:
            base += 1
        if distractor_quality > 0.8:
            base += 1
        return min(5, max(1, base))

    def run_interactive_harvest(self) -> None:
        console.print("""
[bold cyan]╔══════════════════════════════════════════════════════════╗
║           ENHANCED QUIZ CONTENT HARVESTER                  ║
║  Diversity • Semantic Uniqueness • Answer Balance         ║
╚══════════════════════════════════════════════════════════╝[/bold cyan]
""")
        total_questions = 0
        continue_harvesting = True
        while continue_harvesting:
            console.print("\n[bold yellow]How many questions to generate in this batch?[/bold yellow]")
            console.print("Suggested: 100-500 for quick test, 1000-2000 for full harvest")
            try:
                batch_size = int(input("Enter number (or 0 to stop): "))
                if batch_size == 0:
                    break
                content_needed = max(1, batch_size // 2)
                content = self.harvest_with_rotation(content_needed)
                questions: List[EnhancedQuestion] = []
                console.print(f"\n[bold cyan]Generating questions from {len(content)} content pieces...[/bold cyan]")
                for content_piece in content:
                    for _ in range(random.randint(2, 3)):
                        question = self.generate_enhanced_question(content_piece)
                        if question:
                            questions.append(question)
                            if len(questions) >= batch_size:
                                break
                    if len(questions) >= batch_size:
                        break
                self.save_questions(questions)
                total_questions += len(questions)
                self.show_statistics(questions, total_questions)
                continue_harvesting = Confirm.ask(f"\n[bold yellow]Generated {len(questions)} questions. Continue harvesting?[/bold yellow]")
            except ValueError:
                console.print("[red]Invalid input. Please enter a number.[/red]")
            except KeyboardInterrupt:
                console.print("\n[yellow]Harvest interrupted by user.[/yellow]")
                break
        if Confirm.ask("\n[bold cyan]Generate HTML report?[/bold cyan]"):
            self.generate_report(total_questions)

    def save_questions(self, questions: List[EnhancedQuestion]) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        for q in questions:
            try:
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO enhanced_questions
                    (question, options, correct_answer, explanation, category,
                     subcategory, difficulty, confidence, source_url, source_type,
                     distractor_quality, answer_distribution, semantic_fingerprint,
                     concepts, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        q.question,
                        json.dumps(q.options),
                        q.correct_answer,
                        q.explanation,
                        q.category,
                        q.subcategory,
                        q.difficulty,
                        q.confidence,
                        q.source_url,
                        q.source_type,
                        q.distractor_quality,
                        q.answer_distribution,
                        q.semantic_fingerprint,
                        json.dumps(q.concepts),
                        q.created_at,
                    ),
                )
            except sqlite3.IntegrityError:
                pass
        conn.commit()
        conn.close()

    def show_statistics(self, questions: List[EnhancedQuestion], total: int) -> None:
        table = Table(title="Harvest Statistics", show_header=True)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        if questions:
            avg_confidence = sum(q.confidence for q in questions) / len(questions)
            avg_distractor_quality = sum(q.distractor_quality for q in questions) / len(questions)
            categories = Counter(q.category for q in questions)
            answer_dist = Counter(q.answer_distribution for q in questions)
            difficulty_dist = Counter(q.difficulty for q in questions)
            table.add_row("Questions Generated", str(len(questions)))
            table.add_row("Total Questions", str(total))
            table.add_row("Average Confidence", f"{avg_confidence:.2%}")
            table.add_row("Average Distractor Quality", f"{avg_distractor_quality:.2%}")
            table.add_row("", "")
            table.add_row("Top Categories", "")
            for cat, count in categories.most_common(5):
                table.add_row(f"  {cat}", str(count))
            table.add_row("", "")
            table.add_row("Answer Distribution", "")
            for answer, count in sorted(answer_dist.items()):
                table.add_row(f"  {answer}", f"{count} ({count/len(questions)*100:.1f}%)")
            table.add_row("", "")
            table.add_row("Difficulty Distribution", "")
            for diff in range(1, 6):
                count = difficulty_dist.get(diff, 0)
                table.add_row(f"  Level {diff}", f"{count} ({'■' * (count//10)})")
        console.print(table)

    def generate_report(self, total_questions: int) -> None:
        console.print("\n[bold cyan]Generating HTML report...[/bold cyan]")
        console.print(f"[bold green]✅ Report generated: enhanced_harvest_report.html[/bold green]")
        console.print(f"[bold green]✅ Total questions harvested: {total_questions}[/bold green]")

