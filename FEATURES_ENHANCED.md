# 🚀 Enhanced RAG System with SambaNova - New Features

## Overview
The RAG system has been significantly enhanced with **latest news retrieval, time-based filtering, trending topic analysis, and advanced statistics**. This document describes all new features and how to use them.

---

## 📋 Table of Contents
1. [New Core Features](#new-core-features)
2. [API Endpoints](#api-endpoints)
3. [CLI Usage](#cli-usage)
4. [Code Examples](#code-examples)
5. [Time-Based Filtering](#time-based-filtering)
6. [Advanced Usage](#advanced-usage)

---

## 🎯 New Core Features

### 1. **Latest News Retrieval with Timestamps**
- Retrieve the latest news articles within a specific time frame
- Supports flexible time ranges (today, this week, this month, custom days)
- Each article includes formatted timestamp
- Returns article metadata with dates and times

```python
from rag_with_sambanova import get_latest_news

# Get today's latest news
articles = get_latest_news(days=1, limit=5)

# Get this week's news from Technology category
articles = get_latest_news(days=7, category="Technology", limit=10)
```

### 2. **Time-Based Query Filtering**
- Automatically detects time-based keywords in user questions
- Filters results to match the time period in the query
- Supports natural language queries like "latest", "today", "this week"

```python
# User asks: "What's the latest technology news from today?"
# System automatically filters to today's articles
result = query_rag("What's the latest technology news from today?")

# User asks: "Give me news from last 3 days about sports"
# System filters to last 3 days and sports category
result = query_rag("Give me news from last 3 days about sports")
```

### 3. **Trending Topics Analysis**
- Analyze trending keywords across articles
- Extract most frequently mentioned topics
- Time-period based trending (e.g., trending this week, this month)
- Useful for understanding news narratives

```python
from rag_with_sambanova import get_trending_topics

# Get top 10 trending topics from last week
trending = get_trending_topics(days=7, top_n=10)
# Returns: [{"keyword": "climate", "count": 45}, ...]
```

### 4. **News Statistics & Analytics**
- Get comprehensive statistics about articles in database
- Breakdown by category, source, and date
- Time-period based analysis
- Useful for dashboard and insights

```python
from rag_with_sambanova import get_news_statistics

# Get statistics from last 30 days
stats = get_news_statistics(days=30)
# Returns:
# {
#     "total_articles": 5234,
#     "by_category": {"Technology": 1200, "Sports": 980, ...},
#     "by_source": {"BBC": 1500, "NPR": 1200, ...}
# }
```

### 5. **Date Range Queries**
- Query articles from a specific date range
- Optional category filtering
- Perfect for historical analysis and research

```python
from rag_with_sambanova import get_news_by_date_range

# Get Business articles from March 1-15, 2025
articles = get_news_by_date_range(
    start_date="2025-03-01",
    end_date="2025-03-15",
    category="Business"
)
```

### 6. **Enhanced Context Building**
- Better formatting of article metadata in responses
- Timestamps displayed in human-readable format
- Structured article citations
- Improved context relevance

### 7. **Improved Error Messages**
- More descriptive error messages
- Better guidance for users
- Error tracking and logging

### 8. **Metadata Enrichment**
- All responses include query metadata
- Track which filters were applied
- Count of documents retrieved
- Query timestamp information

---

## 🔌 API Endpoints

### Authentication Endpoints
```
POST   /register           - Register new user
POST   /login              - Login and get JWT token
```

### Legacy Endpoints
```
POST   /ask                - Ask a question (with JWT auth)
POST   /clear-memory       - Clear chat history (with JWT auth)
GET    /analyze            - Get article statistics
GET    /                   - Health check
```

### ✨ NEW Enhanced Endpoints

#### 1. **Get Latest News**
```
POST /latest-news
```
**Request:**
```json
{
    "days": 1,
    "category": "Technology",
    "limit": 5
}
```

**Response:**
```json
{
    "status": "success",
    "count": 5,
    "articles": [
        {
            "id": 123,
            "title": "New AI Breakthrough",
            "category": "Technology",
            "date": "2025-04-23 10:30",
            "image_url": "https://...",
            "preview": "Researchers announce breakthrough in..."
        }
    ]
}
```

#### 2. **Get Trending Topics**
```
GET /trending-topics?days=7&top_n=10
```

**Response:**
```json
{
    "status": "success",
    "time_period_days": 7,
    "trending_topics": [
        {"keyword": "climate", "count": 45},
        {"keyword": "election", "count": 42},
        {"keyword": "technology", "count": 38}
    ]
}
```

#### 3. **Get Statistics**
```
GET /statistics?days=30
```

**Response:**
```json
{
    "status": "success",
    "time_period_days": 30,
    "total_articles": 5234,
    "by_category": {
        "Technology": 1200,
        "Sports": 980,
        "Business": 850
    },
    "by_source": {
        "BBC": 1500,
        "NPR": 1200,
        "TheHindu": 1534
    }
}
```

#### 4. **Get News by Date Range**
```
POST /news-by-date-range
```

**Request:**
```json
{
    "start_date": "2025-03-01",
    "end_date": "2025-03-31",
    "category": "Business"
}
```

**Response:**
```json
{
    "status": "success",
    "date_range": "2025-03-01 to 2025-03-31",
    "category_filter": "Business",
    "count": 145,
    "articles": [
        {
            "title": "Stock Market Rally",
            "category": "Business",
            "date": "2025-03-15 14:20",
            "image_url": "https://..."
        }
    ]
}
```

---

## 📱 CLI Usage

The enhanced system includes an interactive CLI with menu-driven interface:

### Start Interactive Session
```bash
python rag_with_sambanova.py
```

### Menu Options
```
1️⃣  Ask a question
2️⃣  Get latest news (today)
3️⃣  Get latest news from this week
4️⃣  Get latest news from this month
5️⃣  Get trending topics
6️⃣  Get news statistics
7️⃣  News by date range
8️⃣  Show chat history
9️⃣  Clear chat history
0️⃣  Exit
```

### CLI Examples

**Ask a Question:**
```
Enter your choice: 1
❓ Ask a question: What are the latest technology news?
```

**Get Today's News:**
```
Enter your choice: 2
📰 Latest News Articles:
1. AI Model Breaks New Ground
   📅 2025-04-23 10:30
   📂 Category: Technology
   Preview: Researchers announce breakthrough...
```

**Get Trending Topics:**
```
Enter your choice: 5
🔥 Trending Topics:
1. Climate (mentioned 45 times)
2. Election (mentioned 42 times)
3. Technology (mentioned 38 times)
```

**Get Statistics:**
```
Enter your choice: 6
📊 News Statistics:
Total Articles (last 30 days): 5234
By Category:
  • Technology: 1200
  • Sports: 980
  • Business: 850
By Source:
  • BBC: 1500
  • NPR: 1200
```

---

## 💻 Code Examples

### Python API Usage

**Example 1: Ask about latest technology news**
```python
from rag_with_sambanova import init_rag, query_rag

# Initialize system
init_rag()

# Query with automatic time and category detection
result = query_rag("What are today's latest technology headlines?")

print("Answer:", result["answer"])
print("\nSources:")
for source in result["sources"]:
    print(f"- {source['title']} ({source['date']})")

print("\nMetadata:")
print(f"- Query Category: {result['metadata']['query_category']}")
print(f"- Time Filter: {result['metadata']['time_filter']}")
```

**Example 2: Get latest news with timestamp**
```python
from rag_with_sambanova import get_latest_news, format_timestamp

# Get this week's business news
articles = get_latest_news(days=7, category="Business", limit=5)

for article in articles:
    print(f"Title: {article['title']}")
    print(f"Date: {article['date']}")
    print(f"Category: {article['category']}")
    print(f"Preview: {article['preview'][:100]}...")
    print()
```

**Example 3: Analyze trends and statistics**
```python
from rag_with_sambanova import get_trending_topics, get_news_statistics

# Get trends
trends = get_trending_topics(days=7, top_n=5)
print("Top 5 Trending Topics:")
for trend in trends:
    print(f"- {trend['keyword']}: {trend['count']} mentions")

# Get stats
stats = get_news_statistics(days=30)
print(f"\nTotal articles in last 30 days: {stats['total_articles']}")
print("Top categories:")
for cat, count in list(stats['by_category'].items())[:3]:
    print(f"- {cat}: {count}")
```

**Example 4: Query by date range**
```python
from rag_with_sambanova import get_news_by_date_range

# Get March 2025 sports articles
articles = get_news_by_date_range(
    start_date="2025-03-01",
    end_date="2025-03-31",
    category="Sports"
)

print(f"Found {len(articles)} articles")
for article in articles:
    print(f"{article['title']} - {article['date']}")
```

### FastAPI Integration

**Example 1: Get latest news via API**
```python
import requests

headers = {"Authorization": f"Bearer {your_token}"}

response = requests.post(
    "http://localhost:8000/latest-news",
    json={"days": 7, "category": "Technology", "limit": 10},
    headers=headers
)

data = response.json()
print(f"Found {data['count']} articles")
```

**Example 2: Get trending topics**
```python
response = requests.get("http://localhost:8000/trending-topics?days=7&top_n=10")
trending = response.json()["trending_topics"]

for item in trending:
    print(f"{item['keyword']}: {item['count']}")
```

**Example 3: Query by date range**
```python
response = requests.post(
    "http://localhost:8000/news-by-date-range",
    json={
        "start_date": "2025-03-01",
        "end_date": "2025-03-31",
        "category": "Business"
    }
)

articles = response.json()["articles"]
```

---

## ⏰ Time-Based Filtering

### Supported Time Phrases
The system automatically recognizes these time expressions:

| Phrase | Days | Example |
|--------|------|---------|
| today | 1 | "latest news today" |
| this week | 7 | "news from this week" |
| this month | 30 | "news this month" |
| last 3 months | 90 | "last 3 months news" |
| last N days | N | "last 5 days articles" |

### How It Works
1. User asks: *"What's the latest technology news from today?"*
2. System detects:
   - Time filter: "today" (1 day)
   - Category: "Technology"
3. System queries database for articles:
   - Created in last 24 hours
   - Category = Technology
4. Results are ranked by relevance and date

### Date Format
- **ISO Format**: YYYY-MM-DD (used in database)
- **Display Format**: YYYY-MM-DD HH:MM (human-readable)
- **Input Format**: YYYY-MM-DD (for date range queries)

---

## 🔧 Advanced Usage

### Custom Database Queries
```python
import sqlite3
from datetime import datetime, timedelta

conn = sqlite3.connect("global_news.db")
cursor = conn.cursor()

# Get articles from last 7 days with specific category
cutoff = (datetime.now() - timedelta(days=7)).isoformat()

cursor.execute("""
    SELECT title, predicted_category, scraped_at, image_url
    FROM articles
    WHERE predicted_category = 'Technology' AND scraped_at > ?
    ORDER BY scraped_at DESC
    LIMIT 10
""", (cutoff,))

articles = cursor.fetchall()
conn.close()
```

### Performance Optimization
For large datasets, use date filtering:

```python
# Bad: Retrieves all articles then filters
docs = vectorstore.similarity_search(query, k=100)
recent = [d for d in docs if is_recent(d)]

# Good: Filter before querying
articles = get_latest_news(days=7, limit=20)
```

### Batch Processing
```python
from rag_with_sambanova import get_latest_news

categories = ["Technology", "Business", "Sports"]
all_articles = []

for category in categories:
    articles = get_latest_news(days=7, category=category, limit=5)
    all_articles.extend(articles)
```

### Error Handling
```python
from rag_with_sambanova import get_latest_news

try:
    articles = get_latest_news(days=1)
except Exception as e:
    print(f"Error: {e}")
    # Fallback to older articles
    articles = get_latest_news(days=7)
```

---

## 📊 Database Schema

The system uses SQLite with these key tables:

### Articles Table
```sql
CREATE TABLE articles (
    id INTEGER PRIMARY KEY,
    source TEXT,
    category TEXT,
    title TEXT,
    link TEXT UNIQUE,
    teaser TEXT,
    image_url TEXT,
    full_text TEXT,
    scraped_at TIMESTAMP,
    predicted_category TEXT,
    loaded INTEGER DEFAULT 0
)
```

### Key Timestamps
- `scraped_at`: When article was scraped (ISO format)
- Used for date filtering and time-based queries

---

## 🎓 Best Practices

1. **Use Time Filters**: Include time expressions in queries for better results
2. **Specify Categories**: Narrow down results by mentioning specific categories
3. **Check Metadata**: Review query metadata to understand what filters were applied
4. **Monitor Trends**: Use trending topics to understand news patterns
5. **Archive Statistics**: Log statistics regularly for trend analysis
6. **Error Recovery**: Handle network and database errors gracefully

---

## 🚀 Performance Tips

- **Latest News**: Typically <100ms
- **Trending Analysis**: Typically <500ms (processes all articles)
- **Statistics**: Typically <300ms
- **Vector Search**: ~1-2 seconds for top-k retrieval
- **LLM Response**: 2-5 seconds average

**Optimization**:
- Use smaller `limit` values for faster results
- Apply category filters to reduce search space
- Use date filters to narrow time windows
- Cache trending topics (change infrequently)

---

## 📝 Example Integration

### Frontend Component (React)
```javascript
// Fetch latest news
const response = await fetch('http://localhost:8000/latest-news', {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        days: 7,
        category: 'Technology',
        limit: 10
    })
});

const data = await response.json();
// Display data.articles
```

---

## 🐛 Troubleshooting

**Q: No articles found?**
- Check database has articles with scraped_at timestamps
- Verify date range is correct
- Try without category filter

**Q: Trends don't make sense?**
- Increase `days` parameter to get more data
- Increase `top_n` to see more keywords
- Keywords are extracted from titles (usually more representative)

**Q: API endpoints return 500 error?**
- Verify database path is correct
- Check SAMBANOVA_API_KEY environment variable
- Look at server logs for detailed error message

---

## 📦 Dependencies

- `langchain` - Vector store and embeddings
- `faiss-cpu` or `faiss-gpu` - Similarity search
- `sambanova` - LLM integration
- `sqlite3` - Database
- `fastapi` - API framework
- `pydantic` - Data validation

---

## 📞 Support

For issues or questions:
1. Check troubleshooting section above
2. Review example code
3. Check server logs
4. Verify database connectivity

---

Last Updated: 2025-04-23
