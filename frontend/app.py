import os

os.environ["PYTORCH_JIT"] = "O"
os.environ["TORCH_COMPILE_DISABLE"]="1"

from flask import Flask, render_template, request, jsonify
import time
from database.db_connection import get_connection
from backend.hybrid_search import choose_strategy
from backend.sql_search import run_filter_first
from backend.vector_search import run_vector_first

app = Flask(__name__)

_model = None

def get_model():
    global _model
    if _model is None:
        print("Loading embedding model...")
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")
        print("Model loaded.")
    return _model

CATEGORIES = ["database", "health", "sports", "politics", "education", "finance", "science", "general"]


@app.route("/")
def index():
    return render_template("index.html", categories=CATEGORIES)


@app.route("/api/search", methods=["POST"])
def search():
    data = request.get_json(force=True)
    query_text = (data.get("query") or "").strip()
    category = (data.get("category") or "").strip() or None
    top_k = int(data.get("top_k") or 5)

    if not query_text:
        return jsonify({"error": "Query text is required."}), 400

    t_embed_start = time.perf_counter()
    embedding = get_model().encode(query_text).tolist()   # <-- changed from model.encode(...)
    t_embed = time.perf_counter() - t_embed_start

    if category:
        strategy, selectivity = choose_strategy("passages", "category", category)
    else:
        strategy, selectivity = "vector-first", 1.0

    t_query_start = time.perf_counter()
    if strategy == "filter-first":
        rows = run_filter_first(embedding, category, top_k)
    else:
        rows = run_vector_first(embedding, category, top_k)
    t_query = time.perf_counter() - t_query_start

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM passages")
    total_rows = cur.fetchone()[0]

    matched_rows = None
    if category:
        cur.execute("SELECT COUNT(*) FROM passages WHERE category = %s", (category,))
        matched_rows = cur.fetchone()[0]

    cur.close()
    conn.close()

    results = [
        {
            "id": r[0],
            "text": r[1],
            "category": r[2],
            "similarity": round(float(r[3]), 4),
        }
        for r in rows
    ]

    return jsonify({
        "query": query_text,
        "category": category,
        "strategy": strategy,
        "selectivity": round(float(selectivity), 4),
        "total_rows": total_rows,
        "matched_rows": matched_rows,
        "embed_time_ms": round(t_embed * 1000, 2),
        "query_time_ms": round(t_query * 1000, 2),
        "total_time_ms": round((t_embed + t_query) * 1000, 2),
        "results": results,
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)
