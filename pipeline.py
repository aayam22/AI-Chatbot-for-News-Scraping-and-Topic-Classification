"""
Master Pipeline Runner
Automates:
1. Scraping
2. Classification
3. Load Documents (FULL)
4. Embedding + FAISS
Tracks time for each step and total runtime.
"""

import time
import importlib


# -------------------------------
# STEP 1: SCRAPING
# -------------------------------
def run_scraper():
    print("\n📰 Running scraper...")
    start = time.time()
    
    try:
        scraper = importlib.import_module("scrapper")
        
        if hasattr(scraper, "main"):
            scraper.main()
        else:
            raise AttributeError("scrapper.py has no main() function")
    
    except Exception as e:
        print(f"❌ Scraping failed: {e}")
        raise
    
    end = time.time()
    print(f"✅ Scraping completed in {round(end - start, 2)} seconds")


# -------------------------------
# STEP 2: CLASSIFICATION
# -------------------------------
def run_classifier():
    print("\n🤖 Running classifier...")
    start = time.time()
    
    try:
        classifier = importlib.import_module("classifier")
        
        if hasattr(classifier, "main"):
            classifier.main()
        else:
            raise AttributeError("classifier.py has no main() function")
    
    except Exception as e:
        print(f"❌ Classification failed: {e}")
        raise
    
    end = time.time()
    print(f"✅ Classification completed in {round(end - start, 2)} seconds")


# -------------------------------
# STEP 3: LOAD DOCUMENTS (FULL)
# -------------------------------
def run_loader():
    print("\n📄 Loading ALL documents...")
    start = time.time()
    
    try:
        loader = importlib.import_module("load_documents")
        
        if hasattr(loader, "load_articles"):
            docs = loader.load_articles(limit=None)  # FULL load
            print(f"✅ Loaded {len(docs)} documents")
        else:
            raise AttributeError("load_documents.py has no load_articles()")
    
    except Exception as e:
        print(f"❌ Loading failed: {e}")
        raise
    
    end = time.time()
    print(f"📄 Document loading completed in {round(end - start, 2)} seconds")


# -------------------------------
# STEP 4: EMBEDDING + FAISS
# -------------------------------
def run_embedding():
    print("\n🧠 Running embedding + FAISS...")
    start = time.time()
    
    try:
        embeddings_script = importlib.import_module("create_embeddings_and_fiass")
        
        if hasattr(embeddings_script, "main"):
            embeddings_script.main()
        else:
            raise AttributeError("create_embeddings_and_fiass.py has no main() function")
    
    except Exception as e:
        print(f"❌ Embedding failed: {e}")
        raise
    
    end = time.time()
    print(f"✅ Embedding completed in {round(end - start, 2)} seconds")


# -------------------------------
# MAIN PIPELINE
# -------------------------------
def main():
    total_start = time.time()
    print("\n🚀 STARTING FULL NEWS AI PIPELINE\n")

    try:
        run_scraper()
        run_classifier()
        run_loader()
        run_embedding()
    
    except Exception as e:
        print(f"\n❌ Pipeline failed: {e}")
        return

    total_end = time.time()
    print("\n🎉 PIPELINE COMPLETED SUCCESSFULLY")
    print(f"⏱ Total pipeline time: {round(total_end - total_start, 2)} seconds")


# -------------------------------
# RUN
# -------------------------------
if __name__ == "__main__":
    main()