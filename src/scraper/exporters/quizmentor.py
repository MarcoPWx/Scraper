#!/usr/bin/env python3
from __future__ import annotations

"""
QuizMentor exporter: converts harvested questions stored in SQLite into
QuizMentor quiz JSON files and an index.
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, List

import pandas as pd

from .base import BaseExporter


class QuizMentorExporter(BaseExporter):
    def __init__(self, harvest_db: str):
        self.db_path = Path(harvest_db)

    def load_questions(self) -> pd.DataFrame:
        conn = sqlite3.connect(self.db_path)
        query = """
            SELECT
                id,
                question,
                options,
                correct_answer,
                explanation,
                category,
                subcategory,
                difficulty,
                confidence
            FROM generated_questions
            WHERE confidence >= 0.75
            ORDER BY category, difficulty
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        df["options"] = df["options"].apply(json.loads)
        return df

    def create_quiz_format(self, questions_df: pd.DataFrame, category: str) -> Dict:
        cat_questions = questions_df[questions_df["category"] == category]
        questions_list = []
        for _, row in cat_questions.iterrows():
            question_obj = {
                "id": f"harvest_{row['id']}",
                "question": row["question"],
                "options": row["options"],
                "correct_answer": int(row["correct_answer"]),
                "explanation": row["explanation"],
                "difficulty": int(row["difficulty"]),
                "tags": [category, row["subcategory"]] if row["subcategory"] else [category],
            }
            questions_list.append(question_obj)
        quiz = {
            "quiz_id": f"harvest_{category}",
            "title": f"{category.title()} Quiz (Harvested)",
            "description": f"Auto-generated quiz from harvested {category} content",
            "category": category,
            "difficulty": "mixed",
            "time_limit": 30,
            "passing_score": 70,
            "questions": questions_list,
            "metadata": {
                "source": "automated_harvest",
                "question_count": len(questions_list),
                "difficulty_distribution": cat_questions["difficulty"].value_counts().to_dict(),
            },
        }
        return quiz

    def export(self, out: str) -> List[Dict]:
        out_dir = Path(out)
        out_dir.mkdir(parents=True, exist_ok=True)
        df = self.load_questions()
        categories = df["category"].unique()
        quiz_summary: List[Dict] = []
        for category in categories:
            quiz = self.create_quiz_format(df, category)
            filename = f"quiz_{category}_harvested.json"
            filepath = out_dir / filename
            with open(filepath, "w") as f:
                json.dump(quiz, f, indent=2)
            quiz_info = {
                "category": category,
                "questions": len(quiz["questions"]),
                "file": str(filepath),
                "difficulties": quiz["metadata"]["difficulty_distribution"],
            }
            quiz_summary.append(quiz_info)
        index = {
            "total_quizzes": len(quiz_summary),
            "total_questions": sum(q["questions"] for q in quiz_summary),
            "categories": [q["category"] for q in quiz_summary],
            "quizzes": quiz_summary,
            "integration_ready": True,
        }
        index_path = out_dir / "harvest_index.json"
        with open(index_path, "w") as f:
            json.dump(index, f, indent=2)
        return quiz_summary

