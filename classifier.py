import sqlite3
from transformers import pipeline
from tqdm import tqdm
from datasets import Dataset
from transformers.pipelines.pt_utils import KeyDataset

DB_PATH = "global_news.db"

# -------------------------------
# Load model (GPU)
# -------------------------------
classifier = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli",
    device=0  # GPU
)

# -------------------------------
# Categories
# -------------------------------
CATEGORIES = [
    "Politics",
    "Technology",
    "Sports",
    "Business",
    "Health",
    "Entertainment",
    "World",
    "Science"
]

# -------------------------------
# Build text (FULL TEXT)
# -------------------------------
def build_text(title, teaser, full_text):
    title = title or ""
    teaser = teaser or ""
    full_text = full_text or ""

    text = f"{title} {teaser} {full_text}".strip()

    return text[:512] if text else "General"


# -------------------------------
# Main
# -------------------------------
def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Add column if not exists
    try:
        cursor.execute("ALTER TABLE articles ADD COLUMN predicted_category TEXT")
        print("Added predicted_category column")
    except Exception:
        print("Column already exists")

    # Fetch data
    cursor.execute("""
        SELECT id, title, teaser, full_text
        FROM articles
        WHERE predicted_category IS NULL
    """)

    rows = cursor.fetchall()
    print(f"Found {len(rows)} articles to classify")

    if not rows:
        return

    # -------------------------------
    # Prepare dataset
    # -------------------------------
    data = []
    for article_id, title, teaser, full_text in rows:
        text = build_text(title, teaser, full_text)
        data.append({"id": article_id, "text": text})

    dataset = Dataset.from_list(data)

    # -------------------------------
    # Run classification (NO WARNING 🚀)
    # -------------------------------
    results = []

    for output in tqdm(
        classifier(
            KeyDataset(dataset, "text"),
            candidate_labels=CATEGORIES,
            batch_size=64,
            truncation=True
        ),
        total=len(dataset),
        desc="Classifying"
    ):
        results.append(output)

    # -------------------------------
    # Save results
    # -------------------------------
    for item, result in zip(data, results):
        category = result["labels"][0]

        cursor.execute("""
            UPDATE articles
            SET predicted_category = ?
            WHERE id = ?
        """, (category, item["id"]))

    conn.commit()
    conn.close()

    print("✅ Classification saved to database")


# -------------------------------
# Run
# -------------------------------
if __name__ == "__main__":
    main()
