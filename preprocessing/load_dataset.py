import csv
from sentence_transformers import SentenceTransformer
from psycopg2.extras import execute_values
from database.db_connection import get_connection

model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")

def derive_category(text: str) -> str:
    t = text.lower()

    if any(w in t for w in [
        "database", "postgres", "sql", "server", "query", "index", "transaction",
        "schema", "table", "vector", "pgvector"
    ]):
        return "database"

    if any(w in t for w in [
        "health", "medical", "doctor", "hospital", "patient", "disease",
        "clinic", "nurse", "surgery", "treatment"
    ]):
        return "health"

    if any(w in t for w in [
        "sport", "sports", "game", "player", "team", "coach",
        "match", "tournament", "football", "basketball", "soccer", "cricket"
    ]):
        return "sports"

    if any(w in t for w in [
        "government", "election", "president", "prime minister", "parliament",
        "policy", "democracy", "campaign", "senate", "congress"
    ]):
        return "politics"

    if any(w in t for w in [
        "school", "university", "college", "student", "teacher",
        "education", "classroom", "course", "exam"
    ]):
        return "education"

    if any(w in t for w in [
        "money", "finance", "bank", "market", "stock", "investment",
        "economy", "economic", "loan", "interest rate", "business", "company"
    ]):
        return "finance"

    if any(w in t for w in [
        "science", "experiment", "research", "physics", "chemistry",
        "biology", "laboratory", "atom", "nuclear", "climate", "environment"
    ]):
        return "science"

    return "general"

def load_local_sample(csv_path="data/processed/msmarco_30k.csv", chunk_size=200, batch_size=8):
    conn = get_connection()
    cur = conn.cursor()

    rows = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for record in reader:
            text = record["text"].strip()
            if text:
                rows.append(text)

    total = len(rows)
    inserted = 0

    for i in range(0, total, chunk_size):
        chunk_texts = rows[i:i + chunk_size]
        categories = [derive_category(t) for t in chunk_texts]

        embeddings = model.encode(
            chunk_texts,
            batch_size=batch_size,
            show_progress_bar=True,
            convert_to_numpy=True
        )

        data = [
            (text, category, False, emb.tolist())
            for text, category, emb in zip(chunk_texts, categories, embeddings)
        ]

        execute_values(
            cur,
            """
            INSERT INTO passages (text, category, is_relevant, embedding)
            VALUES %s
            """,
            data
        )

        conn.commit()
        inserted += len(data)
        print(f"Inserted {inserted}/{total}")

    cur.close()
    conn.close()
    print(f"Done. Total inserted: {inserted}")

if __name__ == "__main__":
    load_local_sample()