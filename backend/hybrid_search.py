"""
hybrid_search.py

Core decision logic for the hybrid search system.

Given a category filter, this module estimates how selective that filter is
(what fraction of the table it matches) using PostgreSQL's own planner
statistics (pg_stats), then decides whether to run a "filter-first" or
"vector-first" retrieval strategy:

- filter-first: apply the category filter first (cheap), then rank only the
  matching subset by vector similarity. Chosen when the filter is highly
  selective (matches a small fraction of rows), since it avoids running the
  expensive vector distance computation over the full table.

- vector-first: rank the entire table by vector similarity first, since
  filtering wouldn't meaningfully reduce the search space. Chosen when the
  filter is not selective (matches a large fraction of rows).

See sql_search.py and vector_search.py for the actual query implementations
of each strategy.
"""

from database.db_connection import get_connection


def parse_pg_array(s):
    """
    Parse a PostgreSQL array literal returned as text (e.g. '{a,b,c}')
    into a plain Python list of strings.
    """
    if s is None:
        return []
    s = s.strip("{}")
    if not s:
        return []
    return [x.strip().strip('"') for x in s.split(",")]


def get_column_selectivity(table, column, value):
    """
    Estimate the selectivity of `column = value` for the given table,
    using PostgreSQL's pg_stats catalog (populated by ANALYZE).

    Selectivity is defined as the estimated fraction of rows in `table`
    that match `column = value` (a number between 0 and 1). Lower values
    mean the filter is more selective (fewer matching rows).

    Strategy:
    1. If `value` appears in the column's "most common values" list,
       return its recorded frequency directly (most accurate).
    2. Otherwise, fall back to an estimate based on `n_distinct`:
       - if n_distinct > 0, it's a direct count of distinct values.
       - if n_distinct < 0, it's a negative fraction of the row count
         (per PostgreSQL's documented convention), so we convert it to
         an absolute distinct count.
       - selectivity is then approximated as 1 / distinct_count, assuming
         roughly uniform distribution across distinct values.
    3. If no statistics are available at all, default to 1.0 (assume the
       filter matches everything, i.e. "not selective").
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT most_common_vals::text,
               most_common_freqs::text,
               n_distinct
        FROM pg_stats
        WHERE tablename = %s AND attname = %s
    """, (table, column))

    row = cur.fetchone()

    cur.execute(f"SELECT COUNT(*) FROM {table}")
    total_rows = cur.fetchone()[0]

    cur.close()
    conn.close()

    if not row:
        return 1.0

    most_common_vals, most_common_freqs, n_distinct = row

    vals = parse_pg_array(most_common_vals)
    freqs = [float(x) for x in parse_pg_array(most_common_freqs)]

    if value in vals:
        idx = vals.index(value)
        if idx < len(freqs):
            return freqs[idx]

    if n_distinct is None:
        return 1.0

    if n_distinct > 0:
        distinct_count = n_distinct
    else:
        distinct_count = abs(n_distinct) * total_rows

    if distinct_count <= 0:
        return 1.0

    return 1.0 / distinct_count


def choose_strategy(table, column, value, threshold=0.3):
    """
    Decide between "filter-first" and "vector-first" retrieval strategies
    based on the estimated selectivity of `column = value`.

    Parameters
    ----------
    table, column, value : str
        The table/column/value to check selectivity for (e.g.
        "passages", "category", "database").
    threshold : float
        Selectivity cutoff below which filter-first is chosen. Default is 0.3
    (per Lu et al.'s reference value; see project report for discussion).
    
    Returns
    -------
    (strategy, selectivity) : (str, float)
        strategy is either "filter-first" or "vector-first".
        selectivity is the estimated fraction of matching rows.
    """
    if value is None:
        return "vector-first", 1.0
    selectivity = get_column_selectivity(table, column, value)
    strategy = "filter-first" if selectivity < threshold else "vector-first"
    return strategy, selectivity


if __name__ == "__main__":
    strategy, sel = choose_strategy("passages", "category", "database")
    print("Chosen strategy:", strategy)
    print("Estimated selectivity:", sel)
