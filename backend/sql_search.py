"""
sql_search.py

Implements the "filter-first" retrieval strategy: filter by category using
SQL's WHERE clause first, then rank only the matching subset by vector
cosine similarity. Used when the category filter is highly selective.
"""

from database.db_connection import get_connection


def run_filter_first(embedding, category, top_k=5):
    conn = get_connection()
    cur = conn.cursor()
    if category is None:
        cur.execute(
            """
            SELECT id, text, category, 1 - (embedding <=> %s::vector) AS similarity
            FROM passages ORDER BY embedding <=> %s::vector LIMIT %s
            """,
            (embedding, embedding, top_k),
        )
    else:
        cur.execute(
            """
            SELECT id, text, category, 1 - (embedding <=> %s::vector) AS similarity
            FROM passages WHERE category = %s
            ORDER BY embedding <=> %s::vector LIMIT %s
            """,
            (embedding, category, embedding, top_k),
        )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

if __name__ == "__main__":
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")
    embedding = model.encode("database indexing and sql optimization").tolist()
    rows = run_filter_first(embedding, "database", top_k=5)
    for r in rows:
        print(r)
