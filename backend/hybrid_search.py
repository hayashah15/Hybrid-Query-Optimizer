"""
Module: Hybrid Search
Description:
Combines SQL Search and Vector Search.
"""

from sql_search import sql_search
from vector_search import vector_search


def hybrid_search(query):

    print("=" * 50)
    print("HYBRID QUERY EXECUTION")
    print("=" * 50)

    sql_results = sql_search(query)

    vector_results = vector_search(query)

    print("Hybrid Search Finished Successfully.\n")

    return {
        "sql_results": sql_results,
        "vector_results": vector_results
    }