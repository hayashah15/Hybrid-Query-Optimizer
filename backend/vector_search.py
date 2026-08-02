"""
vector_search.py

Implements the "vector-first" retrieval strategy: rank ALL rows by vector
cosine similarity first, then optionally filter by category afterward.
Used when a category filter is not selective enough to justify filtering
before running the vector distance computation.
"""

from database.db_connection import get_connection


def run_vector_first(embedding, category=None, top_k=5, oversample_factor=5):
    """
    Rank all passages by cosine similarity to the query embedding, then
    optionally keep only rows matching the given category.
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, text, category,
               1 - (embedding <=> %s::vector) AS similarity
        FROM passages
        ORDER BY embedding <=> %s::vector
        LIMIT %s
        """,
        (embedding, embedding, top_k * oversample_factor),
    )
    rows = cur.fetchall()

    cur.close()
    conn.close()

    if category:
        rows = [r for r in rows if r[2] == category][:top_k]
    else:
        rows = rows[:top_k]

    return rows


if __name__ == "__main__":
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")
    embedding = model.encode("database indexing and sql optimization").tolist()
    rows = run_vector_first(embedding, category=None, top_k=5)
    for r in rows:
        print(r)
