# rag_with_sambanova_enhanced.py
# Enhanced RAG system with latest news retrieval and advanced features

import os
import re
import torch
import nltk
import sqlite3
from datetime import datetime, timedelta
from langchain_community.vectorstores import FAISS
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from sambanova import SambaNova
from nltk.tokenize import sent_tokenize
from collections import Counter

# -----------------------------
# GLOBALS
# -----------------------------
vectorstore = None
client = None
chat_history = []
llm_model = "Meta-Llama-3.3-70B-Instruct"
db_path = "global_news.db"

CATEGORIES = [
    "Politics", "Technology", "Sports",
    "Business", "Health", "Entertainment",
    "World", "Science", "Wildlife"
]

TIME_RANGES = {
    "today": 1,
    "this week": 7,
    "this month": 30,
    "last 3 months": 90
}

# ========================================
# RAG INITIALIZATION
# ========================================
def init_rag(
    faiss_path="./faiss_npr_test",
    embedding_model="BAAI/bge-small-en-v1.5",
    llm_model_param="Meta-Llama-3.3-70B-Instruct",
    sambanova_api_key=os.getenv("SAMBANOVA_API_KEY")
):
    global vectorstore, client, llm_model
    llm_model = llm_model_param

    print("🔄 Initializing RAG system...")

    embeddings = HuggingFaceEmbeddings(
        model_name=embedding_model,
        model_kwargs={"device": "cuda" if torch.cuda.is_available() else "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )

    if os.path.exists(faiss_path):
        vectorstore = FAISS.load_local(
            faiss_path,
            embeddings,
            allow_dangerous_deserialization=True
        )
        print("✅ Loaded existing FAISS index")
    else:
        vectorstore = FAISS.from_documents([], embeddings)
        print("⚠️ FAISS index not found. Created empty FAISS index")

    client = SambaNova(
        api_key=sambanova_api_key,
        base_url="https://api.sambanova.ai/v1"
    )

    print(f"✅ RAG ready! Using LLM model: {llm_model}")

# ========================================
# NEW FEATURE: Latest News Retrieval
# ========================================

def get_latest_news(days=1, category=None, limit=5):
    """
    Retrieve latest news within specified time frame
    Args:
        days: Number of days to look back
        category: Optional category filter
        limit: Maximum number of articles
    Returns:
        List of latest articles with timestamps
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        if category:
            cursor.execute("""
                SELECT id, title, teaser, predicted_category, scraped_at, image_url, full_text
                FROM articles
                WHERE predicted_category = ? AND scraped_at > ?
                ORDER BY scraped_at DESC
                LIMIT ?
            """, (category, cutoff_date.isoformat(), limit))
        else:
            cursor.execute("""
                SELECT id, title, teaser, predicted_category, scraped_at, image_url, full_text
                FROM articles
                WHERE scraped_at > ?
                ORDER BY scraped_at DESC
                LIMIT ?
            """, (cutoff_date.isoformat(), limit))
        
        articles = cursor.fetchall()
        conn.close()
        
        result = []
        for article in articles:
            result.append({
                "id": article[0],
                "title": article[1],
                "teaser": article[2],
                "category": article[3],
                "date": article[4],
                "image_url": article[5],
                "preview": article[6][:200] if article[6] else ""
            })
        
        return result
    except Exception as e:
        print(f"❌ Error fetching latest news: {e}")
        return []

def format_timestamp(iso_string):
    """Convert ISO timestamp to readable format"""
    try:
        dt = datetime.fromisoformat(iso_string)
        return dt.strftime("%Y-%m-%d %H:%M")
    except:
        return iso_string

def get_news_by_date_range(start_date, end_date, category=None):
    """
    Get articles within a specific date range
    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        category: Optional category filter
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        if category:
            cursor.execute("""
                SELECT id, title, teaser, predicted_category, scraped_at, image_url
                FROM articles
                WHERE predicted_category = ? 
                AND DATE(scraped_at) BETWEEN ? AND ?
                ORDER BY scraped_at DESC
            """, (category, start_date, end_date))
        else:
            cursor.execute("""
                SELECT id, title, teaser, predicted_category, scraped_at, image_url
                FROM articles
                WHERE DATE(scraped_at) BETWEEN ? AND ?
                ORDER BY scraped_at DESC
            """, (start_date, end_date))
        
        articles = cursor.fetchall()
        conn.close()
        
        return [{
            "title": a[1],
            "category": a[3],
            "date": format_timestamp(a[4]),
            "image_url": a[5]
        } for a in articles]
    except Exception as e:
        print(f"❌ Error fetching date range: {e}")
        return []

# ========================================
# NEW FEATURE: Trending Topics
# ========================================

def get_trending_topics(days=7, top_n=10):
    """
    Get trending topics based on article frequency
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        cursor.execute("""
            SELECT title FROM articles
            WHERE scraped_at > ?
        """, (cutoff_date,))
        
        titles = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        # Extract keywords from titles
        keywords = []
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'is', 'are'}
        
        for title in titles:
            words = [w.lower() for w in title.split() if len(w) > 3 and w.lower() not in stop_words]
            keywords.extend(words)
        
        # Get most common keywords
        trending = Counter(keywords).most_common(top_n)
        return [{"keyword": k, "count": c} for k, c in trending]
    except Exception as e:
        print(f"❌ Error fetching trends: {e}")
        return []

# ========================================
# NEW FEATURE: News Statistics
# ========================================

def get_news_statistics(days=30):
    """
    Get statistics about news in the database
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        # Total articles
        cursor.execute("SELECT COUNT(*) FROM articles WHERE scraped_at > ?", (cutoff_date,))
        total = cursor.fetchone()[0]
        
        # By category
        cursor.execute("""
            SELECT predicted_category, COUNT(*) 
            FROM articles 
            WHERE scraped_at > ?
            GROUP BY predicted_category
            ORDER BY COUNT(*) DESC
        """, (cutoff_date,))
        by_category = {row[0]: row[1] for row in cursor.fetchall()}
        
        # By source
        cursor.execute("""
            SELECT source, COUNT(*) 
            FROM articles 
            WHERE scraped_at > ?
            GROUP BY source
            ORDER BY COUNT(*) DESC
        """, (cutoff_date,))
        by_source = {row[0]: row[1] for row in cursor.fetchall()}
        
        conn.close()
        
        return {
            "total_articles": total,
            "by_category": by_category,
            "by_source": by_source,
            "time_period_days": days
        }
    except Exception as e:
        print(f"❌ Error fetching statistics: {e}")
        return {}

# ========================================
# IMPROVED: Category Detection
# ========================================
def detect_category(query: str):
    """Detect category from query"""
    query_lower = query.lower()
    for cat in CATEGORIES:
        if re.search(rf"\b{cat.lower()}\b", query_lower):
            return cat
    return None

def detect_time_filter(query: str):
    """
    Detect time-based filters from query
    Returns: (days, filter_type)
    """
    query_lower = query.lower()
    
    for time_phrase, days in TIME_RANGES.items():
        if time_phrase in query_lower:
            return days, time_phrase
    
    # Check for specific date patterns
    if re.search(r"last\s+(\d+)\s+days?", query_lower):
        match = re.search(r"last\s+(\d+)\s+days?", query_lower)
        return int(match.group(1)), f"last {match.group(1)} days"
    
    return None, None

# ========================================
# IMPROVED: Context Building
# ========================================
def clean_context(text, max_chars=700):
    """Clean and truncate context"""
    sentences = sent_tokenize(text)
    context = ""
    for s in sentences:
        if len(context) + len(s) > max_chars:
            break
        context += s + " "
    return context.strip()

def build_enhanced_context(docs, max_chars=700):
    """
    Build context with better timestamp formatting and structure
    """
    context_parts = []
    for i, d in enumerate(docs, 1):
        date_str = format_timestamp(d.metadata.get("date", "unknown"))
        title = d.metadata.get("title", "N/A")
        category = d.metadata.get("category", "General")
        
        context_parts.append(
            f"[{i}] [{category}] {title}\n"
            f"📅 Date: {date_str}\n"
            f"Content: {clean_context(d.page_content, max_chars)}\n"
        )
    
    return "\n---\n".join(context_parts)

# -----------------------------
# ========================================
# IMPROVED: Message Building
# ========================================
def build_messages(query, context, include_summary=False):
    """Build chat messages with enhanced system prompt"""
    messages = [
        {
            "role": "system",
            "content": (
                "You are an advanced news assistant powered by SambaNova AI. "
                "Your capabilities:\n"
                "- Read and summarize provided articles concisely in 3-5 sentences\n"
                "- Include publication dates when discussing news\n"
                "- Use natural, conversational language\n"
                "- Cite article titles and categories appropriately\n"
                "- Highlight key facts and recent developments\n"
                "- Note if information is recent or older\n"
                "- Be accurate and avoid speculation\n\n"
                "Always format your response clearly with key points highlighted."
            )
        }
    ]
    
    # Add last 3 chat history for context
    for chat in chat_history[-3:]:
        messages.append({"role": "user", "content": chat["user"]})
        messages.append({"role": "assistant", "content": chat["assistant"]})
    
    messages.append({
        "role": "user",
        "content": f"Latest Articles:\n{context}\n\nUser Question: {query}"
    })
    
    return messages

# -----------------------------
# ========================================
# ENHANCED: Main Query Function
# ========================================
def query_rag(query: str, max_chars=700, top_k=10, use_date_filter=True):
    """
    Enhanced query function with date filtering and better formatting
    
    Args:
        query: User's question
        max_chars: Max chars for context
        top_k: Top results to retrieve
        use_date_filter: Apply time-based filtering
    
    Returns:
        dict with answer, sources, and metadata
    """
    global vectorstore, client, chat_history, llm_model

    if not vectorstore or not client:
        return {"answer": "⚠️ RAG system not initialized", "sources": [], "metadata": {}}

    try:
        category = detect_category(query)
        days_filter, time_phrase = detect_time_filter(query) if use_date_filter else (None, None)

        # Retrieve documents from vectorstore
        docs = vectorstore.similarity_search(query, k=top_k)

        # Apply category filter
        if category:
            docs = [d for d in docs if d.metadata.get("category", "").lower() == category.lower()]

        # Apply date filter
        if days_filter:
            cutoff_date = datetime.now() - timedelta(days=days_filter)
            filtered_docs = []
            for d in docs:
                try:
                    doc_date = datetime.fromisoformat(d.metadata.get("date", ""))
                    if doc_date > cutoff_date:
                        filtered_docs.append(d)
                except:
                    pass
            docs = filtered_docs

        if not docs:
            no_results_msg = (
                f"⚠️ No relevant articles found"
                f"{f' for {category}' if category else ''}"
                f"{f' from {time_phrase}' if time_phrase else ''}. "
                "Try adjusting your search or time period."
            )
            return {"answer": no_results_msg, "sources": [], "metadata": {}}

        # Build enhanced context
        context = build_enhanced_context(docs, max_chars)

        # Build messages and call LLM
        messages = build_messages(query, context)

        response = client.chat.completions.create(
            model=llm_model,
            messages=messages,
            temperature=0.2
        )

        answer = response.choices[0].message.content.strip() or "⚠️ Could not generate an answer."

        # Update chat history
        chat_history.append({"user": query, "assistant": answer})
        if len(chat_history) > 10:
            chat_history.pop(0)

        # Prepare sources with formatted dates
        sources = []
        for d in docs:
            sources.append({
                "title": d.metadata.get("title", ""),
                "category": d.metadata.get("category", ""),
                "date": format_timestamp(d.metadata.get("date", "")),
                "image_url": d.metadata.get("image_url", ""),
                "teaser": d.metadata.get("teaser", "")
            })

        metadata = {
            "query_category": category,
            "time_filter": time_phrase,
            "documents_retrieved": len(docs),
            "timestamp": datetime.now().isoformat()
        }

        return {
            "answer": answer,
            "sources": sources,
            "metadata": metadata
        }

    except Exception as e:
        return {
            "answer": f"❌ Error: {str(e)}",
            "sources": [],
            "metadata": {"error": str(e)}
        }


# -----------------------------
# ========================================
# ENHANCED: Interactive CLI
# ========================================

def print_menu():
    """Display interactive menu"""
    print("\n" + "="*60)
    print("🤖 Advanced News RAG System with SambaNova")
    print("="*60)
    print("Commands:")
    print("  1️⃣  Ask a question")
    print("  2️⃣  Get latest news (today)")
    print("  3️⃣  Get latest news from this week")
    print("  4️⃣  Get latest news from this month")
    print("  5️⃣  Get trending topics")
    print("  6️⃣  Get news statistics")
    print("  7️⃣  News by date range")
    print("  8️⃣  Show chat history")
    print("  9️⃣  Clear chat history")
    print("  0️⃣  Exit")
    print("="*60)

def display_latest_news(articles):
    """Display latest news articles"""
    print("\n📰 Latest News Articles:\n")
    for i, article in enumerate(articles, 1):
        print(f"{i}. {article['title']}")
        print(f"   📅 {article['date']}")
        print(f"   📂 Category: {article['category']}")
        if article['teaser']:
            print(f"   Preview: {article['teaser'][:150]}...")
        print()

def display_trending(trending):
    """Display trending topics"""
    print("\n🔥 Trending Topics:\n")
    for i, item in enumerate(trending, 1):
        print(f"{i}. {item['keyword'].capitalize()} (mentioned {item['count']} times)")
    print()

def display_statistics(stats):
    """Display news statistics"""
    print("\n📊 News Statistics:\n")
    print(f"Total Articles (last {stats['time_period_days']} days): {stats['total_articles']}")
    print("\nBy Category:")
    for cat, count in stats['by_category'].items():
        print(f"  • {cat}: {count}")
    print("\nBy Source:")
    for source, count in stats['by_source'].items():
        print(f"  • {source}: {count}")
    print()

def display_search_result(result):
    """Display query result with formatting"""
    print("\n" + "="*60)
    print("🧠 AI Answer:")
    print("="*60)
    print(result["answer"])
    
    if result["sources"]:
        print("\n" + "="*60)
        print("📚 Sources:")
        print("="*60)
        for i, s in enumerate(result["sources"], 1):
            print(f"\n{i}. {s['title']}")
            print(f"   Category: {s['category']} | Date: {s['date']}")
            if s['image_url']:
                print(f"   Image: {s['image_url']}")
    
    if result.get("metadata"):
        metadata = result["metadata"]
        if "query_category" in metadata and metadata["query_category"]:
            print(f"\n📂 Query Category: {metadata['query_category']}")
        if "time_filter" in metadata and metadata["time_filter"]:
            print(f"⏰ Time Filter: {metadata['time_filter']}")

# ========================================
# MAIN ENTRY POINT
# ========================================

if __name__ == "__main__":
    init_rag()

    while True:
        print_menu()
        choice = input("Enter your choice (0-9): ").strip()

        if choice == "0":
            print("👋 Goodbye!")
            break

        elif choice == "1":
            q = input("\n❓ Ask a question: ").strip()
            if q:
                result = query_rag(q)
                display_search_result(result)

        elif choice == "2":
            print("\n⏳ Fetching today's news...")
            articles = get_latest_news(days=1, limit=5)
            if articles:
                display_latest_news(articles)
            else:
                print("No articles found for today")

        elif choice == "3":
            print("\n⏳ Fetching this week's news...")
            articles = get_latest_news(days=7, limit=10)
            if articles:
                display_latest_news(articles)
            else:
                print("No articles found for this week")

        elif choice == "4":
            print("\n⏳ Fetching this month's news...")
            articles = get_latest_news(days=30, limit=15)
            if articles:
                display_latest_news(articles)
            else:
                print("No articles found for this month")

        elif choice == "5":
            print("\n🔄 Analyzing trends...")
            trending = get_trending_topics(days=7, top_n=10)
            if trending:
                display_trending(trending)
            else:
                print("No trending topics found")

        elif choice == "6":
            print("\n📊 Gathering statistics...")
            stats = get_news_statistics(days=30)
            if stats:
                display_statistics(stats)

        elif choice == "7":
            start = input("Enter start date (YYYY-MM-DD): ").strip()
            end = input("Enter end date (YYYY-MM-DD): ").strip()
            try:
                articles = get_news_by_date_range(start, end)
                if articles:
                    print(f"\n📰 Articles from {start} to {end}:\n")
                    for i, a in enumerate(articles, 1):
                        print(f"{i}. {a['title']}")
                        print(f"   Category: {a['category']} | Date: {a['date']}\n")
                else:
                    print(f"No articles found between {start} and {end}")
            except Exception as e:
                print(f"Error: {e}")

        elif choice == "8":
            if chat_history:
                print("\n📝 Chat History:\n")
                for i, chat in enumerate(chat_history, 1):
                    print(f"{i}. User: {chat['user'][:50]}...")
                    print(f"   AI: {chat['assistant'][:50]}...\n")
            else:
                print("No chat history yet")

        elif choice == "9":
            chat_history.clear()
            print("✅ Chat history cleared")

        else:
            print("❌ Invalid choice. Please try again.")