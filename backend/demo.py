#!/usr/bin/env python3
import sys
from database.db_connection import get_connection
from backend.hybrid_search import choose_strategy

_model = None

def get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model


def run_filter_first(cur, embedding, category, top_k):
    cur.execute("""
        SELECT id, text, category,
               1 - (embedding <=> %s::vector) AS similarity
        FROM passages
        WHERE category = %s
        ORDER BY embedding <=> %s::vector
        LIMIT %s
    """, (embedding, category, embedding, top_k))
    return cur.fetchall()

def run_vector_first(cur, embedding, category, top_k):
    cur.execute("""
        SELECT id, text, category,
               1 - (embedding <=> %s::vector) AS similarity
        FROM passages
        ORDER BY embedding <=> %s::vector
        LIMIT %s
    """, (embedding, embedding, top_k * 5))
    rows = cur.fetchall()
    if category:
        rows = [r for r in rows if r[2] == category][:top_k]
    else:
        rows = rows[:top_k]
    return rows

def run_query(query_text, category=None, top_k=5):
    embedding = get_model().encode(query_text).tolist()
    conn = get_connection()
    cur = conn.cursor()

    if category:
        strategy, selectivity = choose_strategy("passages", "category", category)
    else:
        strategy, selectivity = "vector-first", 1.0

    if strategy == "filter-first":
        rows = run_filter_first(cur, embedding, category, top_k)
    else:
        rows = run_vector_first(cur, embedding, category, top_k)

    cur.close()
    conn.close()

    print(f"\nQuery: {query_text}")
    print(f"Category filter: {category}")
    print(f"Strategy used: {strategy.upper()}  (selectivity: {selectivity:.4f})")
    print("-" * 60)
    for r in rows:
        print(f"[{r[3]:.4f}] ({r[2]}) {r[1][:100]}...")

def preset_demo():
    run_query("database indexing and sql optimization", category="database")
    run_query("medical treatment and hospital care", category="health")
    run_query("how do computers search through large amounts of data")

def interactive_demo():
    print("Type a query (or 'exit' to quit). Optional: type category after a comma, e.g. 'sql tuning, database'")
    while True:
        raw = input("\nQuery: ").strip()
        if raw.lower() == "exit":
            break
        if "," in raw:
            query_text, category = [x.strip() for x in raw.split(",", 1)]
        else:
            query_text, category = raw, None
        run_query(query_text, category)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_demo()
    else:
        preset_demo()