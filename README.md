# Hybrid Query Optimizer — Adaptive Query Optimization for Hybrid Relational–Vector Workloads

COMP 8157 · Advanced Database Topics · University of Windsor · Summer 2026
Prepared by: Dipesh Adhikari, Haya Shah, Pratyush Sundaram, Uday Kumar Reddy

## Overview

This project is a hybrid search prototype built on PostgreSQL and pgvector. It combines
structured relational filtering (e.g. category) with semantic vector similarity search over
a subset of the MS MARCO passage corpus, and adaptively chooses between two execution
strategies — **Filter-First** and **Vector-First** — based on estimated query selectivity.

A lightweight Flask UI lets a user submit a natural-language query, optionally filter by
category, and see which strategy was selected along with the retrieved passages.

## Project Structure

```
Hybrid-Query-Optimizer/
├── database/
│   ├── db_connection.py       # DB connection using environment variables
│   ├── create_tables.py       # Creates schema from schema.sql
│   ├── check_connection.py    # Verifies DB connectivity
│   └── schema.sql             # passages table + pgvector extension + indexes
├── preprocessing/
│   ├── msmarco_subset.py      # Builds a representative MS MARCO subset
│   └── load_dataset.py        # Embeds passages and loads them into PostgreSQL
├── backend/
│   ├── hybrid_search.py       # Adaptive strategy selection logic
│   ├── sql_search.py          # Filter-First strategy
│   ├── vector_search.py       # Vector-First strategy
│   ├── query_strategies.py    # Shared strategy utilities
│   ├── benchmark.py           # Runs benchmark workload across queries
│   ├── demo.py                # CLI demo of hybrid search
│   └── test_backend.py        # Unit tests for backend modules
├── frontend/
│   ├── app.py                 # Flask application entry point
│   ├── templates/index.html
│   └── static/ (style.css, script.js)
├── requirements.txt
├── .env.example
└── README.md
```

## Prerequisites

- Python 3.10+
- PostgreSQL 14+ with the `pgvector` extension available
- pip / virtualenv

## Setup

### 1. Clone the repository

```bash
git clone <repo-url>
cd Hybrid-Query-Optimizer
```

### 2. Create a virtual environment and install dependencies

```bash
python -m venv venv
source venv/bin/activate   # on Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure environment variables

Copy the example file and fill in your local PostgreSQL credentials:

```bash
cp .env.example .env
```

Edit `.env`:

```
DB_HOST=127.0.0.1
DB_PORT=5432
DB_NAME=hybrid_db
DB_USER=postgres
DB_PASSWORD=your_password_here
```

### 4. Create the database and schema

```bash
createdb hybrid_db
python database/create_tables.py
```

Verify the connection at any time with:

```bash
python database/check_connection.py
```

### 5. Build the dataset and load it

```bash
python preprocessing/msmarco_subset.py
python preprocessing/load_dataset.py
```

This generates 384-dimensional embeddings using `all-MiniLM-L6-v2` and inserts each
passage, category, relevance flag, and embedding into the `passages` table.

## Running the Application

### CLI demo

```bash
python backend/demo.py
```

### Benchmark

```bash
python backend/benchmark.py
```

Reports query text, filter category, estimated selectivity, selected strategy, execution
time, and rows returned for each query in the workload.

### Web UI

```bash
python frontend/app.py
```

Then open `http://127.0.0.1:5000` in a browser. Enter a natural-language query, optionally
select a category filter, and view the retrieved passages along with the strategy chosen.

## How It Works

1. **Filter-First** — applies the category filter in SQL first, then ranks the reduced
   candidate set by vector similarity.
2. **Vector-First** — retrieves the top semantically similar passages first, then applies
   the category filter to that result set.
3. **Adaptive Selection** — estimates the selectivity of the filter (using `pg_stats` and
   category cardinality) and picks whichever strategy is expected to be more efficient for
   that query, logging the decision for later benchmarking.

## Testing

```bash
python -m pytest backend/test_backend.py
```

## Notes

This is an academic prototype scoped to a single-machine, laptop-scale corpus
(~20k rows) and is not intended for production deployment, concurrent multi-user
serving, or the full 8.8-million-row MS MARCO corpus.