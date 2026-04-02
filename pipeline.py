"""
MASTER PIPELINE (FINAL FIXED VERSION)

Automates:
1. Scraping
2. Classification
3. Embedding + FAISS (incremental)

Features:
- Clean module loading
- Error handling
- Execution timing
- Optional pipeline modes
"""

import time
import importlib

# -------------------------------
# CONFIGURATION
# -------------------------------
MODE = "full"
# "full" → run everything
# "fast" → skip scraping (only classify + embed)


# -------------------------------
# UTILITY: RUN MODULE MAIN
# -------------------------------
def run_module(module_name, step_name):
    print(f"\n🚀 Running {step_name}...")
    start = time.time()

    try:
        module = importlib.import_module(module_name)

        if hasattr(module, "main"):
            module.main()
        else:
            raise AttributeError(f"{module_name}.py has no main() function")

    except Exception as e:
        print(f"❌ {step_name} failed: {e}")
        raise

    end = time.time()
    print(f"✅ {step_name} completed in {round(end - start, 2)} seconds")


# -------------------------------
# STEP 1: SCRAPER
# -------------------------------
def run_scraper():
    run_module("scrapper", "Scraping")


# -------------------------------
# STEP 2: CLASSIFIER
# -------------------------------
def run_classifier():
    run_module("classifier", "Classification")


# -------------------------------
# STEP 3: EMBEDDER
# -------------------------------
def run_embedder():
    run_module("embedder", "Embedding + FAISS")


# -------------------------------
# MAIN PIPELINE
# -------------------------------
def main():
    total_start = time.time()

    print("\n==============================")
    print("🚀 STARTING NEWS AI PIPELINE")
    print(f"⚙️ Mode: {MODE.upper()}")
    print("==============================\n")

    try:
        if MODE == "full":
            run_scraper()
            run_classifier()
            run_embedder()

        elif MODE == "fast":
            # Skip scraping → use existing data
            run_classifier()
            run_embedder()

        else:
            raise ValueError("Invalid MODE. Use 'full' or 'fast'.")

    except Exception as e:
        print("\n❌ PIPELINE FAILED")
        print(f"Error: {e}")
        return

    total_end = time.time()

    print("\n==============================")
    print("🎉 PIPELINE COMPLETED SUCCESSFULLY")
    print(f"⏱ Total time: {round(total_end - total_start, 2)} seconds")
    print("==============================\n")


# -------------------------------
# RUN
# -------------------------------
if __name__ == "__main__":
    main()