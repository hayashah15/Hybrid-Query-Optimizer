import time
from sentence_transformers import SentenceTransformer
from database.db_connection import get_connection

model = SentenceTransformer("all-MiniLM-L6-v2")


def embed_query(text):
    return model.encode(text).tolist()


def filter_first(query_text, category, top_k=5):
    embedding = embed_query(query_text)
    conn = get_connection()
    cur = conn.cursor()

    start = time.time()
    cur.execute(
        """
        SELECT id, text, category, embedding <-> %s::vector AS distance
        FROM passages
        WHERE category = %s
        ORDER BY distance
        LIMIT %s
        """,
        (embedding, category, top_k)
    )
    rows = cur.fetchall()
    elapsed = time.time() - start

    cur.close()
    conn.close()
    return rows, elapsed


def vector_first(query_text, category, top_k=5, candidate_pool=50):
    embedding = embed_query(query_text)
    conn = get_connection()
    cur = conn.cursor()

    start = time.time()
    cur.execute(
        """
        SELECT id, text, category, embedding <-> %s::vector AS distance
        FROM passages
        ORDER BY distance
        LIMIT %s
        """,
        (embedding, candidate_pool)
    )
    candidates = cur.fetchall()
    filtered = [row for row in candidates if row[2] == category][:top_k]
    elapsed = time.time() - start

    cur.close()
    conn.close()
    return filtered, elapsed


if __name__ == "__main__":
    q = "database indexing and query optimization"
    cat = "database"

    ff_rows, ff_time = filter_first(q, cat)
    print("Filter-First time:", round(ff_time, 4), "seconds")
    print("Filter-First rows:", len(ff_rows))

    vf_rows, vf_time = vector_first(q, cat)
    print("Vector-First time:", round(vf_time, 4), "seconds")
    print("Vector-First rows:", len(vf_rows))
