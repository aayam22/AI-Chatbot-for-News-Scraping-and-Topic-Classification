import os
import sqlite3
import sys
import tempfile
import unittest
from datetime import datetime, timedelta
from unittest.mock import patch

from fastapi.testclient import TestClient
from jose import jwt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import rag_with_sambanova as rag
from api import app_server
from api.password_policy import validate_password_strength


def reset_pipeline_state():
    with app_server.pipeline_status_lock:
        app_server.pipeline_run_state.clear()
        app_server.pipeline_run_state.update(
            {
                "status": "idle",
                "mode": app_server.PIPELINE_DEFAULT_MODE,
                "started_at": None,
                "finished_at": None,
                "updated_at": None,
                "last_triggered_by": None,
                "exit_code": None,
                "output": "",
            }
        )

    if app_server.pipeline_run_lock.locked():
        app_server.pipeline_run_lock.release()


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
                "https://img.example.com/tech.png",
                "BBC",
            ),
            (
                2,
                "Sports team wins championship",
                "A championship result shocked fans.",
                "The sports team won the championship after a dramatic final.",
                "2026-05-01 07:00:00",
                "Sports",
                "https://img.example.com/sports.png",
                "ESPN",
            ),
            (
                3,
                "Technology startup raises funding",
                "Investors backed a new startup.",
                "A technology startup raised funding for new AI research.",
                "2025-02-15 11:30:00",
                "Technology",
                "",
                "BBC",
            ),
            (
                4,
                "Health officials publish advisory",
                "Officials issued a public advisory.",
                "Health officials published an advisory for seasonal planning.",
                "2025-03-20 09:15:00",
                "Health",
                "",
                "Reuters",
            ),
        ],
    )
    conn.commit()
    conn.close()


class ApiTestCase(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        self.SessionLocal = sessionmaker(bind=self.engine, autocommit=False, autoflush=False)
        app_server.Base.metadata.create_all(bind=self.engine)

        def override_get_db():
            db = self.SessionLocal()
            try:
                yield db
            finally:
                db.close()

        app_server.app.dependency_overrides[app_server.get_db] = override_get_db
        self.client = TestClient(app_server.app)

        self.init_rag_patcher = patch.object(app_server, "init_rag", return_value=None)
        self.init_rag_patcher.start()

        self.original_otp_debug_mode = app_server.OTP_DEBUG_MODE
        self.original_smtp_host = app_server.SMTP_HOST
        app_server.OTP_DEBUG_MODE = True
        app_server.SMTP_HOST = None
        reset_pipeline_state()

    def tearDown(self):
        app_server.app.dependency_overrides.clear()
        self.init_rag_patcher.stop()
        app_server.OTP_DEBUG_MODE = self.original_otp_debug_mode
        app_server.SMTP_HOST = self.original_smtp_host
        reset_pipeline_state()

    def create_user(self, username="alice", password="StrongerPass!123", email=None):
        email = email or f"{username}@example.com"
        with self.SessionLocal() as db:
            user = app_server.User(
                username=username,
                email=email,
                hashed_password=app_server.hash_password(password),
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            return user

    def auth_headers(self, username="alice", expired=False):
        expires_at = datetime.utcnow() - timedelta(minutes=5) if expired else datetime.utcnow() + timedelta(hours=1)
        token = jwt.encode(
            {"sub": username, "exp": expires_at},
            app_server.SECRET_KEY,
            algorithm=app_server.ALGORITHM,
        )
        return {"Authorization": f"Bearer {token}"}


class AuthenticationDocumentedTests(ApiTestCase):
    def test_tc_01_register_with_valid_credentials(self):
        response = self.client.post(
            "/register/request-otp",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "ValidPass!123",
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["delivery"], "debug")
        self.assertIn("debug_otp", payload)

    def test_tc_02_register_with_weak_password(self):
        response = self.client.post(
            "/register/request-otp",
            json={
                "username": "weakuser",
                "email": "weak@example.com",
                "password": "abc123",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("at least 12 characters", response.json()["detail"])

    def test_tc_03_register_with_duplicate_username(self):
        self.create_user(username="existing", email="existing@example.com")

        response = self.client.post(
            "/register/request-otp",
            json={
                "username": "existing",
                "email": "new-email@example.com",
                "password": "ValidPass!123",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Username or email already exists")

    def test_tc_04_verify_with_correct_otp(self):
        otp_response = self.client.post(
            "/register/request-otp",
            json={
                "username": "pendinguser",
                "email": "pending@example.com",
                "password": "ValidPass!123",
            },
        )
        otp_code = otp_response.json()["debug_otp"]

        response = self.client.post(
            "/register",
            json={
                "username": "pendinguser",
                "email": "pending@example.com",
                "otp": otp_code,
            },
        )

        self.assertEqual(response.status_code, 200)
        with self.SessionLocal() as db:
            user = db.query(app_server.User).filter(app_server.User.username == "pendinguser").first()
        self.assertIsNotNone(user)

    def test_tc_05_verify_with_expired_otp(self):
        otp_response = self.client.post(
            "/register/request-otp",
            json={
                "username": "expiringuser",
                "email": "expiring@example.com",
                "password": "ValidPass!123",
            },
        )
        otp_code = otp_response.json()["debug_otp"]

        with self.SessionLocal() as db:
            pending = db.query(app_server.PendingRegistration).filter(
                app_server.PendingRegistration.username == "expiringuser"
            ).first()
            pending.otp_expires_at = datetime.utcnow() - timedelta(minutes=1)
            db.commit()

        response = self.client.post(
            "/register",
            json={
                "username": "expiringuser",
                "email": "expiring@example.com",
                "otp": otp_code,
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("OTP expired", response.json()["detail"])
        with self.SessionLocal() as db:
            pending = db.query(app_server.PendingRegistration).filter(
                app_server.PendingRegistration.username == "expiringuser"
            ).first()
        self.assertIsNone(pending)

    def test_tc_06_verify_with_wrong_otp(self):
        self.client.post(
            "/register/request-otp",
            json={
                "username": "wrongotp",
                "email": "wrongotp@example.com",
                "password": "ValidPass!123",
            },
        )

        response = self.client.post(
            "/register",
            json={
                "username": "wrongotp",
                "email": "wrongotp@example.com",
                "otp": "999999",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Invalid OTP.")

    def test_tc_07_login_with_valid_credentials(self):
        self.create_user(username="alice", password="ValidPass!123")

        response = self.client.post(
            "/login",
            json={"username": "alice", "password": "ValidPass!123"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.json())

    def test_tc_08_login_with_wrong_password(self):
        self.create_user(username="alice", password="ValidPass!123")

        response = self.client.post(
            "/login",
            json={"username": "alice", "password": "WrongPass!123"},
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"], "Invalid credentials")

    def test_tc_09_access_protected_route_without_token(self):
        response = self.client.get("/chat-history")
        self.assertEqual(response.status_code, 401)

    def test_tc_10_access_protected_route_with_expired_token(self):
        self.create_user(username="alice", password="ValidPass!123")

        response = self.client.get("/chat-history", headers=self.auth_headers("alice", expired=True))

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"], "Invalid token")


class ChatAndRagDocumentedTests(ApiTestCase):
    def test_tc_11_ask_a_valid_news_question(self):
        self.create_user(username="alice")

        with patch.object(
            app_server,
            "query_rag",
            return_value={
                "answer": "Here is the latest update.",
                "sources": [{"title": "Source A", "category": "Technology", "image_url": "x"}],
            },
        ):
            response = self.client.post(
                "/ask",
                json={"question": "What is the latest technology news?"},
                headers=self.auth_headers("alice"),
            )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("answer", payload)
        self.assertIsInstance(payload["sources"], list)

    def test_tc_12_ask_question_without_auth_token(self):
        response = self.client.post("/ask", json={"question": "Hello?"})
        self.assertEqual(response.status_code, 401)

    def test_tc_13_conversation_history_carries_context(self):
        self.create_user(username="alice")

        with self.SessionLocal() as db:
            db.add_all(
                [
                    app_server.ChatMessage(username="alice", role="user", text="First question", sources=None),
                    app_server.ChatMessage(username="alice", role="assistant", text="First answer", sources=[]),
                ]
            )
            db.commit()

        captured = {}

        def fake_query_rag(question, conversation_history=None, **kwargs):
            captured["question"] = question
            captured["conversation_history"] = conversation_history
            return {"answer": "Follow-up answer", "sources": []}

        with patch.object(app_server, "query_rag", side_effect=fake_query_rag):
            response = self.client.post(
                "/ask",
                json={"question": "What about that story?"},
                headers=self.auth_headers("alice"),
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            captured["conversation_history"],
            [{"user": "First question", "assistant": "First answer"}],
        )

    def test_tc_14_clear_chat_memory_then_follow_up_has_no_prior_context(self):
        self.create_user(username="alice")

        with self.SessionLocal() as db:
            db.add_all(
                [
                    app_server.ChatMessage(username="alice", role="user", text="Before clear", sources=None),
                    app_server.ChatMessage(username="alice", role="assistant", text="Old answer", sources=[]),
                ]
            )
            db.commit()

        clear_response = self.client.post("/clear-memory", headers=self.auth_headers("alice"))
        self.assertEqual(clear_response.status_code, 200)

        captured = {}

        def fake_query_rag(question, conversation_history=None, **kwargs):
            captured["conversation_history"] = conversation_history
            return {"answer": "Fresh start", "sources": []}

        with patch.object(app_server, "query_rag", side_effect=fake_query_rag):
            ask_response = self.client.post(
                "/ask",
                json={"question": "Start again"},
                headers=self.auth_headers("alice"),
            )

        self.assertEqual(ask_response.status_code, 200)
        self.assertEqual(captured["conversation_history"], [])

    def test_tc_17_sources_contain_image_url_field(self):
        self.create_user(username="alice")

        with patch.object(
            app_server,
            "query_rag",
            return_value={
                "answer": "Response with image sources.",
                "sources": [
                    {
                        "title": "Source A",
                        "category": "Technology",
                        "image_url": "https://img.example.com/a.png",
                    }
                ],
            },
        ):
            response = self.client.post(
                "/ask",
                json={"question": "Show sources"},
                headers=self.auth_headers("alice"),
            )

        self.assertEqual(response.status_code, 200)
        self.assertIn("image_url", response.json()["sources"][0])


class RagBehaviorDocumentedTests(unittest.TestCase):
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

    def test_tc_15_category_detection_in_query(self):
        result = rag.query_rag("latest sports news", top_k=5)
        self.assertEqual(result["metadata"]["query_category"], "Sports")

    def test_tc_16_time_filter_detection(self):
        result = rag.query_rag("news this week", top_k=5)
        self.assertEqual(result["metadata"]["time_filter"], "this week")

    def test_tc_18_no_results_for_obscure_query(self):
        result = rag.query_rag("obscure mitochondrial parliament hedgehog query", top_k=5)
        self.assertIn("No relevant articles found", result["answer"])
        self.assertEqual(result["sources"], [])


class ArchiveAndHistoryDocumentedTests(ApiTestCase):
    def seed_messages(self, username, texts):
        with self.SessionLocal() as db:
            for text in texts:
                db.add(app_server.ChatMessage(username=username, role="user", text=text, sources=None))
            db.commit()

    def test_tc_19_fetch_chat_history(self):
        self.create_user(username="alice")
        self.seed_messages("alice", ["First", "Second", "Third"])

        response = self.client.get("/chat-history", headers=self.auth_headers("alice"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual([msg["text"] for msg in response.json()["messages"]], ["First", "Second", "Third"])

    def test_tc_20_history_is_user_scoped(self):
        self.create_user(username="alice")
        self.create_user(username="bob")
        self.seed_messages("alice", ["Alice only"])
        self.seed_messages("bob", ["Bob only"])

        alice_response = self.client.get("/chat-history", headers=self.auth_headers("alice"))
        bob_response = self.client.get("/chat-history", headers=self.auth_headers("bob"))

        self.assertEqual([msg["text"] for msg in alice_response.json()["messages"]], ["Alice only"])
        self.assertEqual([msg["text"] for msg in bob_response.json()["messages"]], ["Bob only"])

    def test_tc_21_fetch_chat_statistics(self):
        self.create_user(username="alice")
        with self.SessionLocal() as db:
            db.add_all(
                [
                    app_server.ChatMessage(username="alice", role="user", text="One", sources=None),
                    app_server.ChatMessage(username="alice", role="assistant", text="Two", sources=[]),
                    app_server.ChatMessage(username="alice", role="user", text="Three", sources=None),
                ]
            )
            db.commit()

        response = self.client.get("/chat-history/stats", headers=self.auth_headers("alice"))

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["total_messages"], 3)
        self.assertEqual(payload["user_messages"], 2)
        self.assertEqual(payload["assistant_messages"], 1)
        self.assertIsNotNone(payload["first_message"])
        self.assertIsNotNone(payload["last_message"])

    def test_tc_22_delete_own_message(self):
        self.create_user(username="alice")
        with self.SessionLocal() as db:
            message = app_server.ChatMessage(username="alice", role="user", text="Delete me", sources=None)
            db.add(message)
            db.commit()
            message_id = message.id

        delete_response = self.client.delete(f"/chat-history/{message_id}", headers=self.auth_headers("alice"))
        history_response = self.client.get("/chat-history", headers=self.auth_headers("alice"))

        self.assertEqual(delete_response.status_code, 204)
        self.assertEqual(history_response.json()["messages"], [])

    def test_tc_23_delete_another_users_message(self):
        self.create_user(username="alice")
        self.create_user(username="bob")
        with self.SessionLocal() as db:
            message = app_server.ChatMessage(username="bob", role="user", text="Private", sources=None)
            db.add(message)
            db.commit()
            message_id = message.id

        response = self.client.delete(f"/chat-history/{message_id}", headers=self.auth_headers("alice"))

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "Message not found")

    def test_tc_24_pagination_via_limit_offset(self):
        self.create_user(username="alice")
        self.seed_messages("alice", [f"Message {index}" for index in range(1, 16)])

        response = self.client.get("/chat-history?limit=5&offset=10", headers=self.auth_headers("alice"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual([msg["text"] for msg in response.json()["messages"]], [f"Message {index}" for index in range(1, 6)])


class AnalyticsDocumentedTests(ApiTestCase):
    def setUp(self):
        super().setUp()
        self.tempdir = tempfile.TemporaryDirectory()
        self.articles_db_path = os.path.join(self.tempdir.name, "articles.db")
        create_articles_db(self.articles_db_path)
        self.original_sqlite_connect = sqlite3.connect

        def redirect_connect(_path):
            return self.original_sqlite_connect(self.articles_db_path)

        self.sqlite_connect_patcher = patch.object(app_server.sqlite3, "connect", side_effect=redirect_connect)
        self.sqlite_connect_patcher.start()

    def tearDown(self):
        self.sqlite_connect_patcher.stop()
        self.tempdir.cleanup()
        super().tearDown()

    def test_tc_25_get_analysis_with_no_filters(self):
        response = self.client.get("/analyze")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["total_articles"], 4)
        self.assertIn("time_series", payload)
        self.assertIn("category_distribution", payload)
        self.assertIn("source_distribution", payload)

    def test_tc_26_filter_by_date_range(self):
        response = self.client.get("/analyze?date_from=2025-01-01&date_to=2025-03-31")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["total_articles"], 2)
        self.assertEqual(set(payload["time_series"].keys()), {"2025-02-15", "2025-03-20"})

    def test_tc_27_filter_by_category(self):
        response = self.client.get("/analyze?category=Technology")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["total_articles"], 2)
        self.assertEqual(set(payload["category_distribution"].keys()), {"Technology"})

    def test_tc_28_filter_by_source(self):
        response = self.client.get("/analyze?source=BBC")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["total_articles"], 2)
        self.assertEqual(set(payload["source_distribution"].keys()), {"BBC"})

    def test_tc_29_analysis_endpoint_is_public(self):
        response = self.client.get("/analyze")
        self.assertEqual(response.status_code, 200)


class DummyThread:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def start(self):
        return None


class PipelineManagementDocumentedTests(ApiTestCase):
    def test_tc_30_get_pipeline_status_idle(self):
        response = self.client.get("/system/pipeline-status", headers=self.auth_headers("alice"))

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "idle")
        self.assertTrue(payload["can_start"])

    def test_tc_31_trigger_full_pipeline_run(self):
        with patch.object(app_server.threading, "Thread", DummyThread):
            response = self.client.post(
                "/system/pipeline/run",
                json={"mode": "full"},
                headers=self.auth_headers("alice"),
            )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "running")
        self.assertEqual(payload["mode"], "full")
        self.assertFalse(payload["can_start"])

    def test_tc_32_trigger_fast_pipeline_run(self):
        with patch.object(app_server.threading, "Thread", DummyThread):
            response = self.client.post(
                "/system/pipeline/run",
                json={"mode": "fast"},
                headers=self.auth_headers("alice"),
            )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "running")
        self.assertEqual(payload["mode"], "fast")

    def test_tc_33_prevent_concurrent_runs(self):
        app_server.pipeline_run_lock.acquire()
        try:
            response = self.client.post(
                "/system/pipeline/run",
                json={"mode": "full"},
                headers=self.auth_headers("alice"),
            )
        finally:
            if app_server.pipeline_run_lock.locked():
                app_server.pipeline_run_lock.release()

        self.assertEqual(response.status_code, 409)
        self.assertIn("already in progress", response.json()["detail"])

    def test_tc_34_invalid_pipeline_mode(self):
        response = self.client.post(
            "/system/pipeline/run",
            json={"mode": "invalid"},
            headers=self.auth_headers("alice"),
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid mode", response.json()["detail"])

    def test_tc_35_pipeline_output_streams_in_status(self):
        app_server.update_pipeline_run_state(
            status="running",
            mode="full",
            started_at="2026-05-03T10:00:00Z",
            updated_at="2026-05-03T10:00:00Z",
            output="",
        )

        app_server.append_pipeline_output("line one\n")
        first_response = self.client.get("/system/pipeline-status", headers=self.auth_headers("alice"))
        app_server.append_pipeline_output("line two\n")
        second_response = self.client.get("/system/pipeline-status", headers=self.auth_headers("alice"))

        first_output = first_response.json()["output"]
        second_output = second_response.json()["output"]

        self.assertLess(len(first_output), len(second_output))
        self.assertIn("line one", second_output)
        self.assertIn("line two", second_output)


class PasswordPolicyDocumentedTests(unittest.TestCase):
    def test_tc_36_password_too_short(self):
        errors = validate_password_strength("Ab1!short")
        self.assertTrue(any("at least 12 characters" in error for error in errors))

    def test_tc_37_common_password_rejected(self):
        errors = validate_password_strength("password123")
        self.assertTrue(any("too common" in error for error in errors))

    def test_tc_38_password_contains_username(self):
        errors = validate_password_strength("alice!SecurePass1", username="alice", email="alice@example.com")
        self.assertTrue(any("must not contain your username or email" in error for error in errors))

    def test_tc_39_repeated_character_sequence(self):
        errors = validate_password_strength("aaaaaaaaaaaa")
        self.assertTrue(any("single character repeated" in error for error in errors))

    def test_tc_40_only_two_character_classes_used(self):
        errors = validate_password_strength("alllowercase123")
        self.assertTrue(any("at least three" in error for error in errors))

    def test_tc_41_strong_password_accepted(self):
        errors = validate_password_strength("Tr0ub4dor&3XYZ")
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
