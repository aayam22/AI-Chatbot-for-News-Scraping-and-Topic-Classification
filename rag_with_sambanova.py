# rag_with_sambanova_enhanced.py
# Enhanced RAG system with latest news retrieval and advanced features

import os
import re
import sqlite3
from datetime import datetime, timedelta

import torch
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from nltk.tokenize import sent_tokenize
from sambanova import SambaNova

# -----------------------------
# GLOBALS
# -----------------------------
vectorstore = None
client = None
chat_history = []
llm_model = "Meta-Llama-3.3-70B-Instruct"
db_path = "global_news.db"
retrieval_mode = "uninitialized"
generation_mode = "uninitialized"

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

STOP_WORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "is", "are",
    "what", "whats", "latest", "recent", "news", "about", "tell", "from", "this", "that",
    "with", "into", "over", "under", "have", "has", "had", "been", "were", "will", "would",
    "could", "should", "today", "week", "month", "days", "happened", "developments", "people"
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
    global vectorstore, client, llm_model, retrieval_mode, generation_mode

    llm_model = llm_model_param
    vectorstore = None
    client = None
    retrieval_mode = "database"
    generation_mode = "local-summary"
    offline_only = os.getenv("RAG_OFFLINE_ONLY", "false").lower() in {"1", "true", "yes", "on"}

    print("Initializing RAG system...")

    if offline_only:
        print("RAG_OFFLINE_ONLY enabled. Skipping remote embedding and LLM setup.")
        print(
            f"RAG ready! Retrieval: {retrieval_mode} | "
            f"Answering: {generation_mode} | LLM model: {llm_model}"
        )
        return {
            "retrieval_mode": retrieval_mode,
            "generation_mode": generation_mode,
            "llm_model": llm_model,
        }

    try:
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
            retrieval_mode = "faiss"
            print("Loaded existing FAISS index")
        else:
            print("FAISS index not found. Falling back to database retrieval")
    except Exception as exc:
        print(f"FAISS initialization unavailable, using database retrieval instead: {exc}")

    if sambanova_api_key:
        try:
            client = SambaNova(
                api_key=sambanova_api_key,
                base_url="https://api.sambanova.ai/v1"
            )
            generation_mode = "sambanova"
        except Exception as exc:
            print(f"SambaNova client unavailable, using local summaries instead: {exc}")
    else:
        print("SAMBANOVA_API_KEY not set. Using local summaries instead of LLM responses")

    print(
        f"RAG ready! Retrieval: {retrieval_mode} | "
        f"Answering: {generation_mode} | LLM model: {llm_model}"
    )

    return {
        "retrieval_mode": retrieval_mode,
        "generation_mode": generation_mode,
        "llm_model": llm_model,
    }


def format_timestamp(iso_string):
    """Convert ISO timestamp to readable format."""
    try:
        dt = datetime.fromisoformat(iso_string)
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return iso_string


# ========================================
# IMPROVED: Category Detection
# ========================================
def detect_category(query: str):
    """Detect category from query."""
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

    if re.search(r"last\s+(\d+)\s+days?", query_lower):
        match = re.search(r"last\s+(\d+)\s+days?", query_lower)
        return int(match.group(1)), f"last {match.group(1)} days"

    return None, None


# ========================================
# IMPROVED: Context Building
# ========================================
def clean_context(text, max_chars=700):
    """Clean and truncate context."""
    if not text:
        return ""

    try:
        sentences = sent_tokenize(text)
    except LookupError:
        sentences = re.split(r"(?<=[.!?])\s+", text)

    context = ""
    for sentence in sentences:
        if len(context) + len(sentence) > max_chars:
            break
        context += sentence + " "
    return context.strip()


def build_enhanced_context(docs, max_chars=700):
    """
    Build context with better timestamp formatting and structure
    """
    context_parts = []
    for index, doc in enumerate(docs, 1):
        date_str = format_timestamp(doc.metadata.get("date", "unknown"))
        title = doc.metadata.get("title", "N/A")
        category = doc.metadata.get("category", "General")

        context_parts.append(
            f"[{index}] [{category}] {title}\n"
            f"Date: {date_str}\n"
            f"Content: {clean_context(doc.page_content, max_chars)}\n"
        )

    return "\n---\n".join(context_parts)


def extract_query_terms(query: str):
    return [
        token for token in re.findall(r"\b[a-zA-Z]{3,}\b", query.lower())
        if token not in STOP_WORDS
    ]


def search_local_documents(category=None, days_filter=None, top_k=10, query=""):
    """
    Offline-safe fallback retrieval from the local SQLite article store.
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        sql = """
            SELECT id, title, teaser, full_text, scraped_at, predicted_category, image_url
            FROM articles
            WHERE full_text IS NOT NULL
        """
        params = []

        if category:
            sql += " AND predicted_category = ?"
            params.append(category)

        if days_filter:
            cutoff_date = (datetime.now() - timedelta(days=days_filter)).isoformat()
            sql += " AND scraped_at > ?"
            params.append(cutoff_date)

        sql += " ORDER BY scraped_at DESC LIMIT 500"
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()

        query_terms = extract_query_terms(query)
        scored_documents = []

        for row in rows:
            article_id, title, teaser, full_text, scraped_at, predicted_category, image_url = row
            title = title or ""
            teaser = teaser or ""
            full_text = full_text or ""
            haystack = f"{title} {teaser} {full_text}".lower()

            if query_terms:
                score = 0
                for term in query_terms:
                    term_hits = haystack.count(term)
                    if term_hits:
                        score += term_hits
                        if term in title.lower():
                            score += 4
                        if term in teaser.lower():
                            score += 2
                if score <= 0:
                    continue
            else:
                score = 1

            doc = Document(
                page_content=full_text or teaser or title,
                metadata={
                    "id": article_id,
                    "title": title,
                    "teaser": teaser[:180] if teaser else "",
                    "category": predicted_category or "General",
                    "date": scraped_at or "unknown",
                    "image_url": image_url or "",
                }
            )
            scored_documents.append((score, doc))

        scored_documents.sort(
            key=lambda item: (
                item[0],
                item[1].metadata.get("date", "")
            ),
            reverse=True
        )
        return [doc for _, doc in scored_documents[:top_k]]
    except Exception as e:
        print(f"Error during local document search: {e}")
        return []


def build_local_answer(query, docs, category=None, time_phrase=None):
    """
    Deterministic summary used when the remote LLM is unavailable.
    """
    if not docs:
        return (
            f"I couldn't find matching articles"
            f"{f' for {category}' if category else ''}"
            f"{f' from {time_phrase}' if time_phrase else ''}."
        )

    intro = "Here are the most relevant articles I found locally"
    if time_phrase:
        intro += f" for {time_phrase}"
    if category:
        intro += f" in {category}"
    intro += ":"

    lines = [intro]
    for doc in docs[:3]:
        title = doc.metadata.get("title", "Untitled article")
        category_label = doc.metadata.get("category", "General")
        date_label = format_timestamp(doc.metadata.get("date", "unknown"))
        preview = doc.metadata.get("teaser") or clean_context(doc.page_content, max_chars=160)
        preview = preview.strip()
        lines.append(f"- {date_label}: {title} ({category_label})")
        if preview:
            lines.append(f"  {preview}")

    if len(docs) > 3:
        lines.append(f"I found {len(docs)} relevant articles in total for: {query}")

    return "\n".join(lines)


# ========================================
# IMPROVED: Message Building
# ========================================
def build_system_prompt():
    """Build the grounding and response policy for the remote LLM."""
    today = datetime.now().strftime("%Y-%m-%d")
    return (
        "You are an advanced news assistant powered by SambaNova AI.\n"
        f"Today's date is {today}.\n\n"
        "Follow these rules strictly:\n"
        "1. Use only the provided article context for factual claims.\n"
        "2. Treat prior conversation as preference/reference context, not as evidence for new facts.\n"
        "3. If the context is incomplete, uncertain, or does not answer the question, say so clearly.\n"
        "4. Do not invent statistics, dates, quotes, motives, or outcomes.\n"
        "5. When you mention a concrete fact from the context, cite it with source ids like [1] or [2].\n"
        "6. Mention dates when they matter, especially for 'latest', 'today', 'this week', or timeline questions.\n"
        "7. Prefer a direct answer first, then a brief synthesis of the most relevant developments.\n"
        "8. For multi-article questions, group related developments instead of repeating similar points.\n"
        "9. Keep the tone natural and concise, but never omit important uncertainty.\n"
        "10. If the user asks a follow-up like 'what about sports?' or 'summarize that', resolve it using the recent chat history.\n\n"
        "Default output style:\n"
        "- Start with a 1-2 sentence answer.\n"
        "- Then provide 2-5 bullet points when multiple developments are relevant.\n"
        "- End with a short 'Sources:' line citing the most relevant source ids."
    )


def build_user_prompt(query, context, category=None, time_phrase=None):
    """Build the final grounded user prompt sent to the LLM."""
    inferred_category = category or "none detected"
    inferred_time_filter = time_phrase or "none detected"
    return (
        "Use the context below to answer the user's question.\n\n"
        "Question metadata:\n"
        f"- User question: {query}\n"
        f"- Inferred category: {inferred_category}\n"
        f"- Inferred time filter: {inferred_time_filter}\n\n"
        "Article context:\n"
        f"{context}\n\n"
        "Answer requirements:\n"
        "- Ground factual claims in the article context only.\n"
        "- Prioritize the most recent and most directly relevant sources.\n"
        "- Cite factual statements with source ids such as [1] or [2].\n"
        "- If multiple sources conflict or the answer is incomplete, say that explicitly.\n"
        "- If no article fully answers the question, give the best supported partial answer."
    )


def build_messages(query, context, conversation_history=None, include_summary=False, category=None, time_phrase=None):
    """Build chat messages with enhanced system prompt."""
    del include_summary

    messages = [
        {
            "role": "system",
            "content": build_system_prompt()
        }
    ]

    history = conversation_history if conversation_history is not None else chat_history

    for chat in history[-15:]:
        messages.append({"role": "user", "content": chat["user"]})
        messages.append({"role": "assistant", "content": chat["assistant"]})

    messages.append({
        "role": "user",
        "content": build_user_prompt(
            query,
            context,
            category=category,
            time_phrase=time_phrase,
        )
    })

    return messages


def retrieve_documents(query, category=None, days_filter=None, top_k=10):
    docs = []

    if vectorstore:
        try:
            docs = vectorstore.similarity_search(query, k=top_k)
        except Exception as exc:
            print(f"Vector retrieval failed, using database fallback instead: {exc}")

    if category:
        docs = [doc for doc in docs if doc.metadata.get("category", "").lower() == category.lower()]

    if days_filter:
        cutoff_date = datetime.now() - timedelta(days=days_filter)
        filtered_docs = []
        for doc in docs:
            try:
                doc_date = datetime.fromisoformat(doc.metadata.get("date", ""))
                if doc_date > cutoff_date:
                    filtered_docs.append(doc)
            except Exception:
                continue
        docs = filtered_docs

    if not docs:
        docs = search_local_documents(
            category=category,
            days_filter=days_filter,
            top_k=top_k,
            query=query
        )

    return docs


# ========================================
# ENHANCED: Main Query Function
# ========================================
def query_rag(query: str, conversation_history=None, max_chars=700, top_k=10, use_date_filter=True):
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
    global chat_history

    try:
        category = detect_category(query)
        days_filter, time_phrase = detect_time_filter(query) if use_date_filter else (None, None)

        docs = retrieve_documents(
            query=query,
            category=category,
            days_filter=days_filter,
            top_k=top_k
        )

        if not docs:
            no_results_msg = (
                f"No relevant articles found"
                f"{f' for {category}' if category else ''}"
                f"{f' from {time_phrase}' if time_phrase else ''}. "
                "Try adjusting your search or time period."
            )
            return {"answer": no_results_msg, "sources": [], "metadata": {}}

        context = build_enhanced_context(docs, max_chars)
        answer_mode_used = generation_mode

        if client:
            try:
                messages = build_messages(
                    query,
                    context,
                    conversation_history=conversation_history,
                    category=category,
                    time_phrase=time_phrase,
                )
                response = client.chat.completions.create(
                    model=llm_model,
                    messages=messages,
                    temperature=0.2
                )
                answer = response.choices[0].message.content.strip() or "Could not generate an answer."
            except Exception as exc:
                answer = build_local_answer(query, docs, category=category, time_phrase=time_phrase)
                answer_mode_used = f"local-summary-fallback ({exc})"
        else:
            answer = build_local_answer(query, docs, category=category, time_phrase=time_phrase)

        if conversation_history is None:
            chat_history.append({"user": query, "assistant": answer})
            if len(chat_history) > 15:
                chat_history.pop(0)

        sources = []
        for doc in docs:
            sources.append({
                "title": doc.metadata.get("title", ""),
                "category": doc.metadata.get("category", ""),
                "date": format_timestamp(doc.metadata.get("date", "")),
                "image_url": doc.metadata.get("image_url", ""),
                "teaser": doc.metadata.get("teaser", "")
            })

        metadata = {
            "query_category": category,
            "time_filter": time_phrase,
            "documents_retrieved": len(docs),
            "timestamp": datetime.now().isoformat(),
            "retrieval_mode": retrieval_mode,
            "generation_mode": answer_mode_used,
        }

        return {
            "answer": answer,
            "sources": sources,
            "metadata": metadata
        }

    except Exception as e:
        return {
            "answer": f"Error: {str(e)}",
            "sources": [],
            "metadata": {"error": str(e)}
        }


# ========================================
# ENHANCED: Interactive CLI
# ========================================
def print_menu():
    """Display interactive menu."""
    print("\n" + "=" * 60)
    print("Advanced News RAG System with SambaNova")
    print("=" * 60)
    print("Commands:")
    print("  1  Ask a question")
    print("  2  Show chat history")
    print("  3  Clear chat history")
    print("  0  Exit")
    print("=" * 60)

def display_search_result(result):
    """Display query result with formatting."""
    print("\n" + "=" * 60)
    print("AI Answer:")
    print("=" * 60)
    print(result["answer"])

    if result["sources"]:
        print("\n" + "=" * 60)
        print("Sources:")
        print("=" * 60)
        for index, source in enumerate(result["sources"], 1):
            print(f"\n{index}. {source['title']}")
            print(f"   Category: {source['category']} | Date: {source['date']}")
            if source["image_url"]:
                print(f"   Image: {source['image_url']}")

    if result.get("metadata"):
        metadata = result["metadata"]
        if metadata.get("query_category"):
            print(f"\nQuery Category: {metadata['query_category']}")
        if metadata.get("time_filter"):
            print(f"Time Filter: {metadata['time_filter']}")
        if metadata.get("retrieval_mode"):
            print(f"Retrieval Mode: {metadata['retrieval_mode']}")
        if metadata.get("generation_mode"):
            print(f"Generation Mode: {metadata['generation_mode']}")


# ========================================
# MAIN ENTRY POINT
# ========================================
if __name__ == "__main__":
    init_rag()

    while True:
        print_menu()
        choice = input("Enter your choice (0-3): ").strip()

        if choice == "0":
            print("Goodbye!")
            break

        if choice == "1":
            question = input("\nAsk a question: ").strip()
            if question:
                result = query_rag(question)
                display_search_result(result)
            continue

        if choice == "2":
            if chat_history:
                print("\nChat History:\n")
                for index, chat in enumerate(chat_history, 1):
                    print(f"{index}. User: {chat['user'][:50]}...")
                    print(f"   AI: {chat['assistant'][:50]}...\n")
            else:
                print("No chat history yet")
            continue

        if choice == "3":
            chat_history.clear()
            print("Chat history cleared")
            continue

        print("Invalid choice. Please try again.")
