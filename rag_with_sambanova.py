"""
RAG with SambaNova LLM
Uses SambaNova API for high-performance generative AI.

Install: pip install sambanova
"""

from langchain_community.vectorstores import FAISS
from create_embeddings_and_fiass import embeddings

# For SambaNova
from langchain_core.language_models import LLM
from pydantic import Field
from typing import Optional, List, Any
import requests

# ──────────────────────────────────────────────────────
# SambaNova LLM Wrapper for LangChain
# ──────────────────────────────────────────────────────

class SambanovaLLM(LLM):
    """Custom LangChain wrapper for SambaNova API"""
    
    api_key: str = Field(...)
    model: str = "ALLaM-7B-Instruct-preview"
    temperature: float = 0.1
    top_p: float = 0.1
    
    @property
    def _llm_type(self) -> str:
        return "sambanova"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> str:
        """Call SambaNova API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant answering questions based on news articles."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": self.temperature,
                "top_p": self.top_p
            }
            
            response = requests.post(
                "https://api.sambanova.ai/v1/chat/completions",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                raise Exception(f"SambaNova API error: {response.status_code} - {response.text}")
                
        except Exception as e:
            return f"Error: {str(e)}"

# ──────────────────────────────────────────────────────
# Load FAISS Index
# ──────────────────────────────────────────────────────

print("Loading FAISS index...")
vectorstore = FAISS.load_local(
    "./faiss_npr_minimal",
    embeddings,
    allow_dangerous_deserialization=True
)
print("✓ FAISS index loaded successfully.\n")

# Create retriever
retriever = vectorstore.as_retriever(search_type="mmr", search_kwargs={"k": 5})

# ──────────────────────────────────────────────────────
# Initialize SambaNova LLM
# ──────────────────────────────────────────────────────

print("Initializing SambaNova LLM...\n")

llm = SambanovaLLM(
    api_key="f6724657-3191-4841-8a4b-938e7476b0db",
    model="ALLaM-7B-Instruct-preview",
    temperature=0.1,
    top_p=0.1
)

print("✓ SambaNova LLM ready!\n")

# ──────────────────────────────────────────────────────
# Create RAG Chain (Manual Implementation)
# ──────────────────────────────────────────────────────

def generate_qa_response(query: str) -> dict:
    """Manually create RAG response by combining retrieval + generation"""
    
    # Step 1: Retrieve relevant documents
    relevant_docs = vectorstore.similarity_search(query, k=5)
    
    # Step 2: Combine retrieved docs into context
    context = "\n\n".join([
        f"Article {i+1}:\nTitle: {doc.metadata.get('title', 'N/A')}\n"
        f"Content: {doc.page_content[:500]}"
        for i, doc in enumerate(relevant_docs)
    ])
    
    # Step 3: Create prompt with context
    prompt = f"""Based on the following news articles, answer the question:

ARTICLES:
{context}

QUESTION: {query}

ANSWER:"""
    
    # Step 4: Generate answer using SambaNova
    answer = llm._call(prompt)
    
    return {
        "result": answer,
        "source_documents": relevant_docs
    }

# ──────────────────────────────────────────────────────
# Interactive Q&A Loop
# ──────────────────────────────────────────────────────

print("=" * 80)
print("RAG Q&A System with SambaNova LLM")
print("=" * 80)
print("Type 'exit' or 'quit' to exit.\n")

while True:
    query = input("\n📝 Ask a question: ").strip()
    if query.lower() in ["exit", "quit"]:
        print("Exiting. Goodbye!")
        break

    if not query:
        continue

    print(f"\n🔍 Searching and generating answer...\n")

    try:
        # Get answer from RAG chain
        result = generate_qa_response(query)
        
        # Display answer
        print("=" * 80)
        print("💡 ANSWER:")
        print("=" * 80)
        print(result["result"])
        
        # Display source documents (commented out - user only wants answers)
        # print("\n" + "=" * 80)
        # print("📰 SOURCE ARTICLES:")
        # print("=" * 80)
        # for i, doc in enumerate(result["source_documents"], 1):
        #     print(f"\n[Source {i}]")
        #     print(f"Title : {doc.metadata.get('title', 'N/A')}")
        #     print(f"Date  : {doc.metadata.get('scraped_at', 'N/A')}")
        #     print(f"Source: {doc.metadata.get('source', 'N/A')}")
        #     snippet = doc.page_content[:300].replace("\n", " ")
        #     print(f"Preview: {snippet}...\n")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Check your API key and internet connection.")
        continue
