import os
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

import rag_with_sambanova as rag


def create_articles_db(path):
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE articles (
            id INTEGER PRIMARY KEY,
            title TEXT,
            teaser TEXT,
            full_text TEXT,
            scraped_at TEXT,
            predicted_category TEXT,
            image_url TEXT,
            source TEXT
        )
        """
    )
    cursor.executemany(
        """
        INSERT INTO articles (id, title, teaser, full_text, scraped_at, predicted_category, image_url, source)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                1,
                "Technology companies launch new AI tools",
                "Several firms announced new products.",
                "Technology companies launched new AI tools for enterprise customers.",
                "2026-05-01 08:00:00",
                "Technology",
                "",
                "Example News",
            ),
            (
                2,
                "Sports team wins championship",
                "A championship result shocked fans.",
                "The sports team won the championship after a dramatic final.",
                "2026-05-01 07:00:00",
                "Sports",
                "",
                "Example News",
            ),
        ],
    )
    conn.commit()
    conn.close()


class RagOfflineTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tempdir.name, "test_news.db")
        create_articles_db(self.db_path)

        self.original_db_path = rag.db_path
        self.original_vectorstore = rag.vectorstore
        self.original_client = rag.client
        self.original_retrieval_mode = rag.retrieval_mode
        self.original_generation_mode = rag.generation_mode
        self.original_chat_history = list(rag.chat_history)

        rag.db_path = self.db_path
        rag.vectorstore = None
        rag.client = None
        rag.retrieval_mode = "database"
        rag.generation_mode = "local-summary"
        rag.chat_history = []

    def tearDown(self):
        rag.db_path = self.original_db_path
        rag.vectorstore = self.original_vectorstore
        rag.client = self.original_client
        rag.retrieval_mode = self.original_retrieval_mode
        rag.generation_mode = self.original_generation_mode
        rag.chat_history = self.original_chat_history
        self.tempdir.cleanup()

    def test_query_rag_returns_local_summary_without_remote_services(self):
        result = rag.query_rag("What's the latest technology news?", top_k=5)

        self.assertIn("Technology companies launch new AI tools", result["answer"])
        self.assertEqual(result["sources"][0]["category"], "Technology")
        self.assertEqual(result["metadata"]["retrieval_mode"], "database")
        self.assertEqual(result["metadata"]["generation_mode"], "local-summary")

    def test_init_rag_falls_back_cleanly_when_embeddings_are_unavailable(self):
        with patch.object(rag, "HuggingFaceEmbeddings", side_effect=RuntimeError("offline")):
            status = rag.init_rag(
                faiss_path=os.path.join(self.tempdir.name, "missing-index"),
                sambanova_api_key=None,
            )

        self.assertEqual(status["retrieval_mode"], "database")
        self.assertEqual(status["generation_mode"], "local-summary")

    def test_build_messages_includes_grounding_rules_and_query_metadata(self):
        messages = rag.build_messages(
            "What's the latest technology news?",
            "[1] [Technology] Technology companies launch new AI tools\nDate: 2026-05-01 08:00\nContent: Several firms announced new products.",
            conversation_history=[],
            category="Technology",
            time_phrase="today",
        )

        self.assertEqual(messages[0]["role"], "system")
        self.assertIn("Use only the provided article context for factual claims", messages[0]["content"])
        self.assertIn("cite it with source ids like [1] or [2]", messages[0]["content"])
        self.assertEqual(messages[-1]["role"], "user")
        self.assertIn("User question: What's the latest technology news?", messages[-1]["content"])
        self.assertIn("Inferred category: Technology", messages[-1]["content"])
        self.assertIn("Inferred time filter: today", messages[-1]["content"])

    def test_build_messages_preserves_recent_conversation_turns_before_latest_prompt(self):
        history = [
            {"user": "What happened earlier?", "assistant": "Earlier summary."},
            {"user": "What about sports?", "assistant": "Sports summary."},
        ]

        messages = rag.build_messages(
            "And today?",
            "[1] [Sports] Sports team wins championship\nDate: 2026-05-01 07:00\nContent: A dramatic final.",
            conversation_history=history,
            category="Sports",
            time_phrase="today",
        )

        self.assertEqual(messages[1]["content"], "What happened earlier?")
        self.assertEqual(messages[2]["content"], "Earlier summary.")
        self.assertEqual(messages[3]["content"], "What about sports?")
        self.assertEqual(messages[4]["content"], "Sports summary.")
        self.assertIn("Answer requirements:", messages[-1]["content"])


if __name__ == "__main__":
    unittest.main()
