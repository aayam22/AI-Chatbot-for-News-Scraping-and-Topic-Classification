# app_server_unified_per_user.py

from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import sqlite3
from collections import Counter
import os

# ✅ Import RAG module with chat_history
from rag_with_sambanova import (
    init_rag, query_rag, chat_history,
    get_latest_news, get_trending_topics, 
    get_news_statistics, get_news_by_date_range
)

# ----------------------------
# CONFIG
# ----------------------------
DATABASE_URL = "sqlite:///./users.db"
SECRET_KEY = "super_secret_key_change_this_in_production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# ----------------------------
# DATABASE SETUP
# ----------------------------
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

Base.metadata.create_all(bind=engine)

# ----------------------------
# PASSWORD UTILS
# ----------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str):
    return pwd_context.verify(password, hashed)

# ----------------------------
# SCHEMAS
# ----------------------------
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class QueryRequest(BaseModel):
    question: str

class DateRangeRequest(BaseModel):
    start_date: str
    end_date: str
    category: str = None

class LatestNewsRequest(BaseModel):
    days: int = 1
    category: str = None
    limit: int = 5

class AnalysisResponse(BaseModel):
    total_articles: int
    top_categories: list
    top_sources: list
    category_distribution: dict
    source_distribution: dict

# ----------------------------
# DEPENDENCY
# ----------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ----------------------------
# JWT TOKEN
# ----------------------------
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ----------------------------
# ANALYSIS UTILS
# ----------------------------
def get_article_statistics(date_from: str = None, date_to: str = None, category: str = None, source: str = None):
    """
    Query global_news.db for advanced analytics with time-series data
    Supports filtering by date range, predicted_category, and source
    """
    try:
        db_path = os.path.join(os.path.dirname(__file__), '..', 'global_news.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Build query with optional filters - using scraped_at timestamp and predicted_category
        query = "SELECT scraped_at, predicted_category, source FROM articles WHERE 1=1"
        params = []
        
        if date_from:
            query += " AND DATE(scraped_at) >= ?"
            params.append(date_from)
        if date_to:
            query += " AND DATE(scraped_at) <= ?"
            params.append(date_to)
        if category:
            query += " AND predicted_category = ?"
            params.append(category)
        if source:
            query += " AND source = ?"
            params.append(source)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        print(f"[DEBUG] Query executed, found {len(rows)} rows")  # Debug log
        if rows:
            print(f"[DEBUG] Sample row: {rows[0]}")  # Debug log
        
        # Process data for time-series
        time_series = {}
        category_counter = Counter()
        source_counter = Counter()
        
        for scraped_at, pred_cat, src in rows:
            # Extract date (YYYY-MM-DD format) from timestamp
            date_key = scraped_at[:10] if scraped_at else "Unknown"
            time_series[date_key] = time_series.get(date_key, 0) + 1
            
            # Handle None/empty predicted_category as "General"
            cat_label = pred_cat if pred_cat and pred_cat.strip() else "General"
            category_counter[cat_label] += 1
            
            if src:
                source_counter[src] += 1
        
        # Sort time series by date
        sorted_dates = sorted(time_series.keys())
        time_series_sorted = {date: time_series[date] for date in sorted_dates}
        
        # Get totals
        total_articles = len(rows)
        
        # Get top predicted categories and sources
        top_categories = [
            {"name": cat, "count": count} 
            for cat, count in category_counter.most_common(5)
        ]
        top_sources = [
            {"name": src, "count": count} 
            for src, count in source_counter.most_common(5)
        ]
        
        # Get all unique predicted categories and sources for filters
        all_categories = list(dict.fromkeys([
            (pred_cat if pred_cat and pred_cat.strip() else "General") 
            for _, pred_cat, _ in rows
        ]))
        all_sources = list(dict.fromkeys([src for _, _, src in rows if src]))
        
        print(f"[DEBUG] Categories found: {all_categories}")  # Debug log
        print(f"[DEBUG] Category distribution: {dict(category_counter)}")  # Debug log
        
        conn.close()
        
        return {
            "total_articles": total_articles,
            "time_series": time_series_sorted,
            "top_categories": top_categories,
            "top_sources": top_sources,
            "category_distribution": dict(category_counter),
            "source_distribution": dict(source_counter),
            "available_categories": all_categories,
            "available_sources": all_sources,
            "date_range": {
                "from": sorted_dates[0] if sorted_dates else None,
                "to": sorted_dates[-1] if sorted_dates else None
            }
        }
    except Exception as e:
        print(f"[ERROR] {str(e)}")  # Debug log
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# ----------------------------
# PER-USER CHAT HISTORY
# ----------------------------
# Map username → list of messages
user_chat_memory = {}

# ----------------------------
# LIFESPAN HANDLER (RAG Init)
# ----------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Initializing RAG system...")
    init_rag()
    yield
    print("🛑 Shutting down app...")

# ----------------------------
# FASTAPI APP
# ----------------------------
app = FastAPI(title="Unified Auth + RAG API with Per-User Chat", lifespan=lifespan)

# ----------------------------
# CORS
# ----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------
# AUTH ROUTES
# ----------------------------
@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username or email already exists")

    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"username": new_user.username, "email": new_user.email}


@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": db_user.username})
    return {"access_token": token, "token_type": "bearer"}

# ----------------------------
# PROTECTED CHAT ROUTES
# ----------------------------
@app.post("/ask")
def ask_question(req: QueryRequest, current_user: str = Depends(get_current_user)):
    # Initialize per-user memory if not exists
    if current_user not in user_chat_memory:
        user_chat_memory[current_user] = []

    try:
        # Query RAG (this also updates chat_history internally)
        rag_result = query_rag(req.question)

        # Update per-user memory
        user_chat_memory[current_user].append({
            "question": req.question, 
            "answer": rag_result["answer"],
            "sources": rag_result["sources"]
        })

        return {
            "answer": rag_result["answer"],
            "sources": rag_result["sources"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/clear-memory")
def clear_memory(current_user: str = Depends(get_current_user)):
    # Clear only this user's memory
    user_chat_memory[current_user] = []
    return {"status": "Memory cleared", "user": current_user}

# ----------------------------
# ANALYSIS ROUTES
# ----------------------------
@app.get("/analyze")
def get_analysis(date_from: str = None, date_to: str = None, category: str = None, source: str = None):
    """
    Get advanced article statistics with time-series data
    Query params:
    - date_from: YYYY-MM-DD format
    - date_to: YYYY-MM-DD format
    - category: Filter by specific predicted_category
    - source: Filter by specific source
    """
    stats = get_article_statistics(date_from, date_to, category, source)
    return stats

# ========================================
# NEW ENDPOINTS FOR ENHANCED RAG FEATURES
# ========================================

@app.post("/latest-news")
def get_latest_news_endpoint(req: LatestNewsRequest, current_user: str = Depends(get_current_user)):
    """
    Get latest news with optional category filter
    - days: Number of days to look back (1=today, 7=this week, 30=this month)
    - category: Optional category filter
    - limit: Max articles to return
    """
    try:
        articles = get_latest_news(days=req.days, category=req.category, limit=req.limit)
        return {
            "status": "success",
            "count": len(articles),
            "articles": articles
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/trending-topics")
def get_trending_topics_endpoint(days: int = 7, top_n: int = 10):
    """
    Get trending topics based on article frequency
    - days: Analyze articles from last N days
    - top_n: Number of top trends to return
    """
    try:
        trending = get_trending_topics(days=days, top_n=top_n)
        return {
            "status": "success",
            "time_period_days": days,
            "trending_topics": trending
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/statistics")
def get_statistics_endpoint(days: int = 30):
    """
    Get news statistics for specified time period
    - days: Number of days to analyze
    """
    try:
        stats = get_news_statistics(days=days)
        return {
            "status": "success",
            "time_period_days": days,
            **stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/news-by-date-range")
def get_news_by_date_range_endpoint(req: DateRangeRequest):
    """
    Get articles within a specific date range
    - start_date: YYYY-MM-DD format
    - end_date: YYYY-MM-DD format
    - category: Optional category filter
    """
    try:
        articles = get_news_by_date_range(req.start_date, req.end_date, req.category)
        return {
            "status": "success",
            "date_range": f"{req.start_date} to {req.end_date}",
            "category_filter": req.category,
            "count": len(articles),
            "articles": articles
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ----------------------------
# HEALTH CHECK
# ----------------------------
@app.get("/")
def home():
    return {"message": "Unified Auth + RAG API running"}