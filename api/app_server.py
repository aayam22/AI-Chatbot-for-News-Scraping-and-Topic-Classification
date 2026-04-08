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

# ✅ Import RAG module with chat_history
from rag_with_sambanova import init_rag, query_rag, chat_history

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
# HEALTH CHECK
# ----------------------------
@app.get("/")
def home():
    return {"message": "Unified Auth + RAG API running"}