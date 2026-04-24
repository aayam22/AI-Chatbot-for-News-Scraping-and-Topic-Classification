import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from api import app_server


def build_test_client(current_user="alice"):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    app_server.Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    def override_get_current_user():
        return current_user

    app_server.app.dependency_overrides[app_server.get_db] = override_get_db
    app_server.app.dependency_overrides[app_server.get_current_user] = override_get_current_user

    client = TestClient(app_server.app)
    return client, TestingSessionLocal


class ChatHistoryApiTests(unittest.TestCase):
    def setUp(self):
        self.init_rag_patcher = patch.object(app_server, "init_rag", return_value=None)
        self.init_rag_patcher.start()

    def tearDown(self):
        app_server.app.dependency_overrides.clear()
        self.init_rag_patcher.stop()

    def test_ask_uses_only_current_user_history(self):
        client, SessionLocal = build_test_client(current_user="alice")

        with SessionLocal() as db:
            db.add_all(
                [
                    app_server.ChatMessage(username="alice", role="user", text="Alice question 1", sources=None),
                    app_server.ChatMessage(username="alice", role="assistant", text="Alice answer 1", sources=[]),
                    app_server.ChatMessage(username="alice", role="user", text="Alice question 2", sources=None),
                    app_server.ChatMessage(username="alice", role="assistant", text="Alice answer 2", sources=[]),
                    app_server.ChatMessage(username="bob", role="user", text="Bob secret question", sources=None),
                    app_server.ChatMessage(username="bob", role="assistant", text="Bob secret answer", sources=[]),
                ]
            )
            db.commit()

        captured = {}

        def fake_query_rag(question, conversation_history=None, **kwargs):
            captured["question"] = question
            captured["conversation_history"] = conversation_history
            return {"answer": "Fresh answer", "sources": [{"title": "Source A", "category": "Tech"}]}

        with patch.object(app_server, "query_rag", side_effect=fake_query_rag):
            response = client.post("/ask", json={"question": "New Alice question"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(captured["question"], "New Alice question")
        self.assertEqual(
            captured["conversation_history"],
            [
                {"user": "Alice question 1", "assistant": "Alice answer 1"},
                {"user": "Alice question 2", "assistant": "Alice answer 2"},
            ],
        )

        with SessionLocal() as db:
            saved_messages = db.query(app_server.ChatMessage).filter(
                app_server.ChatMessage.username == "alice"
            ).order_by(app_server.ChatMessage.id).all()

        self.assertEqual(saved_messages[-2].text, "New Alice question")
        self.assertEqual(saved_messages[-1].text, "Fresh answer")

    def test_ask_uses_latest_fifteen_turns_for_current_user_only(self):
        client, SessionLocal = build_test_client(current_user="alice")

        with SessionLocal() as db:
            for turn in range(1, 17):
                db.add(
                    app_server.ChatMessage(
                        username="alice",
                        role="user",
                        text=f"Alice question {turn}",
                        sources=None,
                    )
                )
                db.add(
                    app_server.ChatMessage(
                        username="alice",
                        role="assistant",
                        text=f"Alice answer {turn}",
                        sources=[],
                    )
                )

            for turn in range(1, 6):
                db.add(
                    app_server.ChatMessage(
                        username="bob",
                        role="user",
                        text=f"Bob question {turn}",
                        sources=None,
                    )
                )
                db.add(
                    app_server.ChatMessage(
                        username="bob",
                        role="assistant",
                        text=f"Bob answer {turn}",
                        sources=[],
                    )
                )

            db.commit()

        captured = {}

        def fake_query_rag(question, conversation_history=None, **kwargs):
            captured["conversation_history"] = conversation_history
            return {"answer": "Latest 15 only", "sources": []}

        with patch.object(app_server, "query_rag", side_effect=fake_query_rag):
            response = client.post("/ask", json={"question": "Limit check"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(captured["conversation_history"]), 15)
        self.assertEqual(
            captured["conversation_history"][0],
            {"user": "Alice question 2", "assistant": "Alice answer 2"},
        )
        self.assertEqual(
            captured["conversation_history"][-1],
            {"user": "Alice question 16", "assistant": "Alice answer 16"},
        )
        self.assertTrue(
            all("Bob" not in turn["user"] and "Bob" not in turn["assistant"] for turn in captured["conversation_history"])
        )

    def test_clear_memory_removes_history_used_by_follow_up_requests(self):
        client, SessionLocal = build_test_client(current_user="alice")

        with SessionLocal() as db:
            db.add_all(
                [
                    app_server.ChatMessage(username="alice", role="user", text="Question before clear", sources=None),
                    app_server.ChatMessage(username="alice", role="assistant", text="Answer before clear", sources=[]),
                ]
            )
            db.commit()

        clear_response = client.post("/clear-memory")
        self.assertEqual(clear_response.status_code, 200)

        captured = {}

        def fake_query_rag(question, conversation_history=None, **kwargs):
            captured["conversation_history"] = conversation_history
            return {"answer": "After clear", "sources": []}

        with patch.object(app_server, "query_rag", side_effect=fake_query_rag):
            ask_response = client.post("/ask", json={"question": "Start over"})

        self.assertEqual(ask_response.status_code, 200)
        self.assertEqual(captured["conversation_history"], [])

        history_response = client.get("/chat-history")
        self.assertEqual(history_response.status_code, 200)
        payload = history_response.json()
        self.assertEqual([message["text"] for message in payload["messages"]], ["Start over", "After clear"])

    def test_chat_history_returns_only_current_user_messages_in_chronological_order(self):
        client, SessionLocal = build_test_client(current_user="alice")

        with SessionLocal() as db:
            db.add_all(
                [
                    app_server.ChatMessage(username="alice", role="user", text="First", sources=None),
                    app_server.ChatMessage(username="alice", role="assistant", text="Second", sources=[]),
                    app_server.ChatMessage(username="bob", role="user", text="Third", sources=None),
                    app_server.ChatMessage(username="alice", role="user", text="Fourth", sources=None),
                ]
            )
            db.commit()

        response = client.get("/chat-history?limit=10&offset=0")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual([message["text"] for message in payload["messages"]], ["First", "Second", "Fourth"])

    def test_delete_chat_message_removes_it_from_future_history_results(self):
        client, SessionLocal = build_test_client(current_user="alice")

        with SessionLocal() as db:
            message = app_server.ChatMessage(username="alice", role="assistant", text="Delete me", sources=[])
            db.add(message)
            db.commit()
            message_id = message.id

        delete_response = client.delete(f"/chat-history/{message_id}")
        self.assertEqual(delete_response.status_code, 200)

        history_response = client.get("/chat-history")
        self.assertEqual(history_response.status_code, 200)
        self.assertEqual(history_response.json()["messages"], [])


if __name__ == "__main__":
    unittest.main()
