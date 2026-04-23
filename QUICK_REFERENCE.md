# 🚀 Quick Reference Guide - Enhanced RAG System

## 📋 Quick Start

### Run Interactive CLI
```bash
python rag_with_sambanova.py
```

### Start API Server
```bash
uvicorn api.app_server:app --reload
```

---

## 🎯 Common Tasks

### Task 1: Get Latest News
**CLI:**
```
Choose option 2 (today), 3 (this week), or 4 (this month)
```

**Python:**
```python
from rag_with_sambanova import get_latest_news
articles = get_latest_news(days=7, category="Technology", limit=10)
```

**API:**
```bash
curl -X POST http://localhost:8000/latest-news \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"days": 7, "category": "Technology", "limit": 10}'
```

---

### Task 2: Ask About Current Events
**CLI:**
```
Choose option 1, then ask: "What's the latest technology news?"
```

**Python:**
```python
result = query_rag("What's the latest technology news today?")
print(result["answer"])
```

**API:**
```bash
curl -X POST http://localhost:8000/ask \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"question": "What happened in sports this week?"}'
```

---

### Task 3: Get Trending Topics
**CLI:**
```
Choose option 5
```

**Python:**
```python
from rag_with_sambanova import get_trending_topics
trends = get_trending_topics(days=7, top_n=10)
for t in trends:
    print(f"{t['keyword']}: {t['count']} mentions")
```

**API:**
```bash
curl http://localhost:8000/trending-topics?days=7&top_n=10
```

---

### Task 4: Get Statistics
**CLI:**
```
Choose option 6
```

**Python:**
```python
from rag_with_sambanova import get_news_statistics
stats = get_news_statistics(days=30)
print(f"Total articles: {stats['total_articles']}")
```

**API:**
```bash
curl http://localhost:8000/statistics?days=30
```

---

### Task 5: Query Date Range
**CLI:**
```
Choose option 7
Enter start date: 2025-03-01
Enter end date: 2025-03-31
```

**Python:**
```python
from rag_with_sambanova import get_news_by_date_range
articles = get_news_by_date_range(
    start_date="2025-03-01",
    end_date="2025-03-31",
    category="Business"
)
```

**API:**
```bash
curl -X POST http://localhost:8000/news-by-date-range \
  -H "Content-Type: application/json" \
  -d '{
    "start_date": "2025-03-01",
    "end_date": "2025-03-31",
    "category": "Business"
  }'
```

---

## 🔍 Key Features at a Glance

| Feature | CLI | Python | API | Time |
|---------|-----|--------|-----|------|
| Latest News | ✓ | ✓ | ✓ | 100ms |
| Trending | ✓ | ✓ | ✓ | 500ms |
| Statistics | ✓ | ✓ | ✓ | 300ms |
| Date Range | ✓ | ✓ | ✓ | 200ms |
| Query | ✓ | ✓ | ✓ | 3-8s |

---

## 📊 Data Format Examples

### Latest News Response
```json
{
  "id": 123,
  "title": "Breaking News",
  "category": "Technology",
  "date": "2025-04-23 10:30",
  "preview": "Article content...",
  "image_url": "https://..."
}
```

### Trending Topics
```json
{
  "keyword": "climate",
  "count": 45
}
```

### Statistics Response
```json
{
  "total_articles": 5234,
  "by_category": {
    "Technology": 1200,
    "Sports": 980
  },
  "by_source": {
    "BBC": 1500,
    "NPR": 1200
  }
}
```

### Query Response
```json
{
  "answer": "Based on recent articles...",
  "sources": [
    {
      "title": "Article Title",
      "category": "Technology",
      "date": "2025-04-23 10:30",
      "image_url": "https://..."
    }
  ],
  "metadata": {
    "query_category": "Technology",
    "time_filter": "today",
    "documents_retrieved": 5
  }
}
```

---

## ⏰ Time Filter Keywords

```python
TIME_RANGES = {
    "today": 1,
    "this week": 7,
    "this month": 30,
    "last 3 months": 90
}
```

**Examples:**
- "latest news today" → today's articles
- "what happened this week?" → last 7 days
- "news from this month" → last 30 days
- "last 5 days news" → custom 5 days

---

## 🔐 Authentication

### Get Token
```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "pass"}'

# Response: {"access_token": "YOUR_TOKEN", "token_type": "bearer"}
```

### Use Token
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/ask
```

---

## 🛠️ Configuration

### Environment Variables
```bash
# Set SambaNova API key
export SAMBANOVA_API_KEY="your_api_key"

# Optional: Change FAISS path
FAISS_PATH="./faiss_npr_test"

# Optional: Change database
DB_PATH="global_news.db"
```

### Settings in Code
```python
# In rag_with_sambanova.py
DB_PATH = "global_news.db"
FAISS_PATH = "./faiss_npr_test"

# Model
LLM_MODEL = "Meta-Llama-3.3-70B-Instruct"

# Categories
CATEGORIES = ["Politics", "Technology", "Sports", ...]

# Time ranges
TIME_RANGES = {"today": 1, "this week": 7, ...}
```

---

## 📱 Frontend Integration

### React Example
```javascript
// Login
const loginResponse = await fetch('http://localhost:8000/login', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({username: 'user', password: 'pass'})
});
const {access_token} = await loginResponse.json();

// Ask question
const response = await fetch('http://localhost:8000/ask', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${access_token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({question: 'Latest news today?'})
});
const result = await response.json();
```

### Vue Example
```javascript
// Get trending
const response = await fetch('http://localhost:8000/trending-topics?days=7&top_n=10');
const data = await response.json();
// Display data.trending_topics
```

---

## 🐛 Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| No articles found | Verify database has data, check date range |
| API returns 401 | Generate new JWT token |
| Slow response | Reduce `limit` parameter, use smaller date range |
| Database error | Verify `DB_PATH` and database permissions |
| Missing API key | Set `SAMBANOVA_API_KEY` environment variable |

---

## 📊 Performance Tips

1. **Use smaller limits** - `limit=5` faster than `limit=50`
2. **Apply filters early** - Specify category or date range
3. **Cache results** - Store trending/statistics for 1 hour
4. **Use date ranges** - Reduce search space with specific dates
5. **Batch queries** - Process multiple questions together

---

## 🎓 Learning Path

1. **Start**: Run CLI (`python rag_with_sambanova.py`)
2. **Explore**: Try each menu option
3. **Code**: Test Python functions
4. **API**: Use REST endpoints
5. **Integrate**: Build frontend
6. **Advanced**: Custom queries and analysis

---

## 📚 Documentation Map

```
Project Root
├── FEATURES_ENHANCED.md ........... Complete feature docs
├── IMPLEMENTATION_SUMMARY.md ..... What was added
├── README.md ..................... Original project docs
├── rag_with_sambanova.py ......... Main module (Enhanced)
├── api/app_server.py ............ API server (Enhanced)
├── scrapper.py ................... News scraper
├── embedder.py ................... FAISS embedder
└── classifier.py ................. Category classifier
```

---

## 🔗 Useful Links

- [SambaNova API Docs](https://docs.sambanova.ai/)
- [LangChain Docs](https://python.langchain.com/)
- [FAISS Docs](https://github.com/facebookresearch/faiss)
- [FastAPI Docs](https://fastapi.tiangolo.com/)

---

## 💬 Example Queries

```
"What's the latest technology news?"
"Show me today's breaking news"
"What happened in sports this week?"
"Latest business news from this month"
"Tell me about recent health developments"
"What are people talking about?"
"Show trending topics"
"Get news from March 1-15"
"Business articles from last week"
"Statistics for the last 30 days"
```

---

## 📈 Dashboard Ideas

Combine API endpoints to create:
- **Live Dashboard**: Trending topics + stats
- **News Feed**: Latest news by category
- **Analytics**: Statistics over time
- **Search**: Query with date ranges
- **Alerts**: Track specific keywords

---

## 🚀 Pro Tips

1. Use CLI for testing, API for production
2. Cache trending topics (changes hourly)
3. Implement rate limiting on API
4. Monitor vector search quality
5. Archive statistics weekly
6. Track query patterns
7. Set alerts for trending spikes

---

**Quick Links:**
- Full Docs: [FEATURES_ENHANCED.md](FEATURES_ENHANCED.md)
- Implementation: [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
- Code: [rag_with_sambanova.py](rag_with_sambanova.py)

Last Updated: 2025-04-23
