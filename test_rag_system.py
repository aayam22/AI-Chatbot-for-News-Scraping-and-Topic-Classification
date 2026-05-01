#!/usr/bin/env python3
"""
Core RAG system smoke test.
Tests database connectivity, RAG initialization, and chatbot responses.
"""

import os
import sqlite3
import sys

from tabulate import tabulate

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

os.environ.setdefault("RAG_OFFLINE_ONLY", "1")


def check_database():
    """Verify database exists and has article data."""
    print("\n" + "=" * 70)
    print("DATABASE CONNECTIVITY CHECK")
    print("=" * 70)

    db_path = "global_news.db"

    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return False

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='articles'")
        if not cursor.fetchone():
            print("'articles' table not found in database")
            conn.close()
            return False

        print(f"Database found: {db_path}")

        cursor.execute("SELECT COUNT(*) FROM articles")
        total = cursor.fetchone()[0]
        print(f"Total articles in database: {total}")

        if total == 0:
            print("No articles in database. Run scrapper first.")
            conn.close()
            return False

        cursor.execute(
            """
            SELECT predicted_category, COUNT(*)
            FROM articles
            GROUP BY predicted_category
            ORDER BY COUNT(*) DESC
            """
        )
        categories = cursor.fetchall()

        cat_table = []
        for category, count in categories:
            cat_table.append([category if category else "Unknown", count])
        print("\nArticles by Category:")
        print(tabulate(cat_table, headers=["Category", "Count"], tablefmt="grid"))

        cursor.execute(
            """
            SELECT source, COUNT(*)
            FROM articles
            GROUP BY source
            ORDER BY COUNT(*) DESC
            LIMIT 5
            """
        )
        sources = cursor.fetchall()

        src_table = [[source, count] for source, count in sources]
        print("\nTop 5 Sources:")
        print(tabulate(src_table, headers=["Source", "Count"], tablefmt="grid"))

        cursor.execute(
            """
            SELECT title, scraped_at, predicted_category
            FROM articles
            ORDER BY scraped_at DESC
            LIMIT 1
            """
        )
        latest = cursor.fetchone()
        if latest:
            print(f"\nLatest Article: {latest[1]}")
            print(f"   Title: {latest[0][:60]}...")
            print(f"   Category: {latest[2]}")

        conn.close()
        return True
    except Exception as exc:
        print(f"Database error: {exc}")
        return False


def test_rag_initialization():
    """Verify the RAG module initializes."""
    print("\n" + "=" * 70)
    print("RAG INITIALIZATION TEST")
    print("=" * 70)

    try:
        from rag_with_sambanova import init_rag

        print("\nInitializing RAG system...")
        init_rag()
        print("RAG system initialized successfully")
        return True
    except Exception as exc:
        print(f"Error initializing RAG: {exc}")
        return False


def test_chatbot_queries():
    """Run a few real chatbot queries."""
    print("\n" + "=" * 70)
    print("CHATBOT QUERY TESTS")
    print("=" * 70)

    try:
        from rag_with_sambanova import query_rag

        test_queries = [
            "What's the latest technology news?",
            "Tell me about recent developments",
            "What happened in sports today?",
            "Give me news from this week",
            "What are people talking about?",
        ]

        for index, query in enumerate(test_queries, 1):
            print("\n" + "-" * 70)
            print(f"Query {index}: {query}")
            print("-" * 70)

            try:
                result = query_rag(query)

                print("\nAI Response:")
                answer = result["answer"]
                print(answer[:300] + "..." if len(answer) > 300 else answer)

                if result["sources"]:
                    print(f"\nSources Used ({len(result['sources'])}):")
                    for source_index, source in enumerate(result["sources"][:3], 1):
                        print(f"   {source_index}. {source['title'][:50]}... ({source['category']})")

                if result.get("metadata"):
                    meta = result["metadata"]
                    if meta.get("query_category"):
                        print(f"\nDetected Category: {meta['query_category']}")
                    if meta.get("time_filter"):
                        print(f"Detected Time Filter: {meta['time_filter']}")
                    print(f"Documents Retrieved: {meta.get('documents_retrieved', 'N/A')}")

                print("\nQuery successful")
            except Exception as exc:
                print(f"Query failed: {exc}")
                return False

        return True
    except Exception as exc:
        print(f"Error testing chatbot: {exc}")
        return False


def generate_report():
    """Generate smoke test summary."""
    print("\n" + "=" * 70)
    print("TEST SUMMARY REPORT")
    print("=" * 70)

    checks = {
        "Database Connectivity": check_database(),
        "RAG Initialization": test_rag_initialization(),
        "Chatbot Queries": test_chatbot_queries(),
    }

    print("\n" + "=" * 70)
    print("FINAL STATUS")
    print("=" * 70)

    summary_table = []
    for check, status in checks.items():
        summary_table.append(["PASS" if status else "FAIL", check])

    print(tabulate(summary_table, headers=["Status", "Test"], tablefmt="grid"))

    if all(checks.values()):
        print("\nALL TESTS PASSED! System is working properly.")
    else:
        print("\nSome tests failed. Check the errors above.")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    print("\n")
    print("+" + "=" * 68 + "+")
    print("|" + " " * 68 + "|")
    print("|" + "  RAG SYSTEM COMPREHENSIVE TEST SUITE".center(68) + "|")
    print("|" + " " * 68 + "|")
    print("+" + "=" * 68 + "+")

    generate_report()

    print("\nDocumentation:")
    print("   - QUICK_REFERENCE.md: Fast lookup guide")
    print("   - FEATURES_ENHANCED.md: Complete feature docs")
    print("   - IMPLEMENTATION_SUMMARY.md: Technical details")
    print("\n")
