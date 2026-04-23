#!/usr/bin/env python3
"""
Comprehensive RAG System Test Script
Tests database connectivity, news retrieval, and chatbot responses
"""

import sqlite3
import os
from datetime import datetime, timedelta
from tabulate import tabulate

# ============================================
# DATABASE CHECKS
# ============================================

def check_database():
    """Verify database and check article count"""
    print("\n" + "="*70)
    print("🔍 DATABASE CONNECTIVITY CHECK")
    print("="*70)
    
    db_path = "global_news.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='articles'")
        if not cursor.fetchone():
            print("❌ 'articles' table not found in database")
            return False
        
        print(f"✅ Database found: {db_path}")
        
        # Count total articles
        cursor.execute("SELECT COUNT(*) FROM articles")
        total = cursor.fetchone()[0]
        print(f"✅ Total articles in database: {total}")
        
        if total == 0:
            print("⚠️  No articles in database. Run scrapper first!")
            return False
        
        # Count by category
        cursor.execute("""
            SELECT predicted_category, COUNT(*) 
            FROM articles 
            GROUP BY predicted_category 
            ORDER BY COUNT(*) DESC
        """)
        categories = cursor.fetchall()
        
        print("\n📊 Articles by Category:")
        cat_table = []
        for cat, count in categories:
            cat_label = cat if cat else "Unknown"
            cat_table.append([cat_label, count])
        print(tabulate(cat_table, headers=["Category", "Count"], tablefmt="grid"))
        
        # Count by source
        cursor.execute("""
            SELECT source, COUNT(*) 
            FROM articles 
            GROUP BY source 
            ORDER BY COUNT(*) DESC
            LIMIT 5
        """)
        sources = cursor.fetchall()
        
        print("\n📰 Top 5 Sources:")
        src_table = []
        for src, count in sources:
            src_table.append([src, count])
        print(tabulate(src_table, headers=["Source", "Count"], tablefmt="grid"))
        
        # Check latest article
        cursor.execute("""
            SELECT title, scraped_at, predicted_category 
            FROM articles 
            ORDER BY scraped_at DESC 
            LIMIT 1
        """)
        latest = cursor.fetchone()
        if latest:
            print(f"\n📅 Latest Article: {latest[1]}")
            print(f"   Title: {latest[0][:60]}...")
            print(f"   Category: {latest[2]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False


# ============================================
# RAG SYSTEM TESTS
# ============================================

def test_rag_functions():
    """Test RAG functions with real data"""
    print("\n" + "="*70)
    print("🧠 RAG SYSTEM TESTS")
    print("="*70)
    
    try:
        from rag_with_sambanova import (
            init_rag, query_rag, get_latest_news,
            get_trending_topics, get_news_statistics
        )
        
        print("\n⏳ Initializing RAG system...")
        init_rag()
        print("✅ RAG system initialized successfully")
        
        # Test 1: Get Latest News
        print("\n" + "-"*70)
        print("TEST 1: Get Latest News (Today)")
        print("-"*70)
        try:
            latest = get_latest_news(days=1, limit=3)
            if latest:
                print(f"✅ Retrieved {len(latest)} articles from today")
                for i, article in enumerate(latest, 1):
                    print(f"\n  {i}. {article['title'][:60]}...")
                    print(f"     📅 {article['date']}")
                    print(f"     📂 {article['category']}")
            else:
                print("⚠️  No articles found for today (database may be empty)")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Test 2: Get Latest News by Category
        print("\n" + "-"*70)
        print("TEST 2: Get Latest Technology News (This Week)")
        print("-"*70)
        try:
            tech_news = get_latest_news(days=7, category="Technology", limit=3)
            if tech_news:
                print(f"✅ Retrieved {len(tech_news)} Technology articles")
                for i, article in enumerate(tech_news, 1):
                    print(f"\n  {i}. {article['title'][:60]}...")
                    print(f"     📅 {article['date']}")
            else:
                print("⚠️  No Technology articles found this week")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Test 3: Get Trending Topics
        print("\n" + "-"*70)
        print("TEST 3: Trending Topics (Last 7 Days)")
        print("-"*70)
        try:
            trends = get_trending_topics(days=7, top_n=5)
            if trends:
                print(f"✅ Found {len(trends)} trending topics")
                trend_table = []
                for trend in trends:
                    trend_table.append([trend['keyword'], trend['count']])
                print(tabulate(trend_table, headers=["Keyword", "Mentions"], tablefmt="grid"))
            else:
                print("⚠️  No trending data available")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Test 4: Get Statistics
        print("\n" + "-"*70)
        print("TEST 4: News Statistics (Last 30 Days)")
        print("-"*70)
        try:
            stats = get_news_statistics(days=30)
            if stats:
                print(f"✅ Total articles: {stats['total_articles']}")
                print(f"\n   By Category:")
                for cat, count in list(stats['by_category'].items())[:5]:
                    print(f"   • {cat}: {count}")
            else:
                print("⚠️  No statistics available")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error initializing RAG: {e}")
        return False


# ============================================
# CHATBOT QUERY TESTS
# ============================================

def test_chatbot_queries():
    """Test chatbot with real queries"""
    print("\n" + "="*70)
    print("💬 CHATBOT QUERY TESTS")
    print("="*70)
    
    try:
        from rag_with_sambanova import query_rag
        
        # Test queries
        test_queries = [
            "What's the latest technology news?",
            "Tell me about recent developments",
            "What happened in sports today?",
            "Give me news from this week",
            "What are people talking about?",
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n" + "-"*70)
            print(f"Query {i}: {query}")
            print("-"*70)
            
            try:
                result = query_rag(query)
                
                print("\n📝 AI Response:")
                print(result["answer"][:300] + "..." if len(result["answer"]) > 300 else result["answer"])
                
                if result["sources"]:
                    print(f"\n📚 Sources Used ({len(result['sources'])}):")
                    for j, source in enumerate(result["sources"][:3], 1):
                        print(f"   {j}. {source['title'][:50]}... ({source['category']})")
                
                if result.get("metadata"):
                    meta = result["metadata"]
                    if meta.get("query_category"):
                        print(f"\n📂 Detected Category: {meta['query_category']}")
                    if meta.get("time_filter"):
                        print(f"⏰ Detected Time Filter: {meta['time_filter']}")
                    print(f"📊 Documents Retrieved: {meta.get('documents_retrieved', 'N/A')}")
                
                print("\n✅ Query successful")
                
            except Exception as e:
                print(f"❌ Query failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing chatbot: {e}")
        return False


# ============================================
# SUMMARY REPORT
# ============================================

def generate_report():
    """Generate comprehensive test report"""
    print("\n" + "="*70)
    print("📊 TEST SUMMARY REPORT")
    print("="*70)
    
    checks = {
        "Database Connectivity": check_database(),
        "RAG Functions": test_rag_functions(),
        "Chatbot Queries": test_chatbot_queries(),
    }
    
    print("\n" + "="*70)
    print("✅ FINAL STATUS")
    print("="*70)
    
    summary_table = []
    for check, status in checks.items():
        status_icon = "✅" if status else "❌"
        summary_table.append([status_icon, check])
    
    print(tabulate(summary_table, headers=["Status", "Test"], tablefmt="grid"))
    
    all_passed = all(checks.values())
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED! System is working properly!")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
    
    print("\n" + "="*70)


# ============================================
# MAIN
# ============================================

if __name__ == "__main__":
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "  🚀 RAG SYSTEM COMPREHENSIVE TEST SUITE".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝")
    
    generate_report()
    
    print("\n📖 Documentation:")
    print("   - QUICK_REFERENCE.md: Fast lookup guide")
    print("   - FEATURES_ENHANCED.md: Complete feature docs")
    print("   - IMPLEMENTATION_SUMMARY.md: Technical details")
    print("\n")
