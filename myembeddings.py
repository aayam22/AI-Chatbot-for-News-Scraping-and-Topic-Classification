# part_3_test_embeddings.py

# Correct import for recent LangChain Hugging Face integration
from langchain_huggingface.embeddings import HuggingFaceEmbeddings

# This model is fast on CPU and good quality
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-en-v1.5",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True}
)

# Test embedding
text = "NPR reports on climate change impacts in Nepal."
vector = embeddings.embed_query(text)

print("Embedding vector length:", len(vector))
print("First 8 values:", vector[:8])
