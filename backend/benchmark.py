from backend.query_strategies import filter_first, vector_first
from backend.hybrid_search import choose_strategy

TEST_QUERIES = [
    ("database indexing and sql optimization", "database"),
    ("medical treatment and hospital care", "health"),
    ("team player wins game", "sports"),
    ("general information retrieval question", "general")
]


def run_benchmark():
    for query_text, category in TEST_QUERIES:
        ff_rows, ff_time = filter_first(query_text, category)
        vf_rows, vf_time = vector_first(query_text, category)
        strategy, sel = choose_strategy("passages", "category", category)

        print("-" * 60)
        print("Query:", query_text)
        print("Category:", category)
        print("Selectivity:", round(sel, 4), "Chosen:", strategy)
        print("Filter-First:", round(ff_time, 4), "sec | rows:", len(ff_rows))
        print("Vector-First:", round(vf_time, 4), "sec | rows:", len(vf_rows))


if __name__ == "__main__":
    run_benchmark()
