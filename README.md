# Hybrid Query Optimizer — Adaptive Query Optimization for Hybrid Relational–Vector Workloads

COMP 8157 · Advanced Database Topics · University of Windsor · Summer 2026  
Prepared by: Dipesh Adhikari, Haya Shah, Pratyush Sundaram, Uday Kumar Reddy

## 📌 Project Portal Links (Grading)
- **Project Management Tool:** [Hive Workspace](https://app.hive.com/workspace/rdn2QoFgeTpGdxWEQ?projectId=kpQnLkdBW9XXovH4F)
- **Cloud Platform UI Preview:** [https://hybrid-query-optimizer.onrender.com](https://hybrid-query-optimizer.onrender.com)
  *(Note: Due to Render's free-tier 512MB RAM limit, live search execution causes an OOM error when loading the PyTorch model. Please run locally for full end-to-end functionality as detailed in our D.4.4 Deployment Document).*

## Overview

This project is a hybrid search prototype built on PostgreSQL and pgvector. It combines
structured relational filtering (e.g. category) with semantic vector similarity search over
a subset of the MS MARCO passage corpus, and adaptively chooses between two execution
strategies — **Filter-First** and **Vector-First** — based on estimated query selectivity.

A lightweight Flask UI lets a user submit a natural-language query, optionally filter by
category, and see which strategy was selected along with the retrieved passages.

## Project Structure

```text
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

## Database Schema & Connection
*Note on Existing Database: Due to the high compute costs associated with hosting a live PostgreSQL database with vector extensions, there is no permanently hosted cloud database instance for this project. Graders must provision their own local PostgreSQL database following the connection and setup steps below.*

This project requires **PostgreSQL 15+** with the **pgvector** extension installed.

### Schema
Our core data is stored using the `pgvector` extension. The primary schema configuration is as follows:
```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE passages (
    id SERIAL PRIMARY KEY,
    text TEXT NOT NULL,
    category TEXT,
    is_relevant BOOLEAN,
    embedding vector(384)
);

CREATE INDEX ON passages (category);
```

### Connection Instructions
Database connections are managed via `psycopg2`. See the Setup section below for instructions on how to configure your `.env` file to connect to your local instance.

## Prerequisites

- Python 3.10+
- PostgreSQL 15+ with the `pgvector` extension available
- pip / virtualenv

## Setup

### 1. Clone the repository

```bash
git clone <repo-url>
cd Hybrid-Query-Optimizer
```

### 2. Create a virtual environment and install dependencies

```bash
python3 -m venv venv
source venv/bin/activate   # on Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure environment variables

Copy the example file and fill in your local PostgreSQL credentials:

```bash
cp .env.example .env
```

Edit `.env`:

```env
DB_HOST=127.0.0.1
DB_PORT=5432
DB_NAME=hybrid_db
DB_USER=postgres
DB_PASSWORD=your_password_here
```

### 4. Create the database and schema

```bash
createdb hybrid_db
python3 database/create_tables.py
```

Verify the connection at any time with:

```bash
python3 database/check_connection.py
```

## 📊 Dataset Information
* **Repository Location (Ready to Use):** The pre-processed dataset is included directly in this repository at `data/processed/msmarco_30k.csv`. Graders **do not** need to download any external data to run the application.
* **Original Source:** [BEIR: A Heterogeneous Benchmark for Zero-shot Evaluation of Information Retrieval Models](https://github.com/UKPLab/beir) (Thakur et al., 2021). 
* **Upstream Download Link:** The raw corpus was originally retrieved via the official [BeIR Hugging Face Repository](https://huggingface.co/BeIR).
* **Subset Details:** We sampled a subset of 30,000 passages from the original 8.8-million-row MS MARCO dataset to simulate a realistic search environment while remaining feasible for local database insertion and grading.

To process and load the data into your database, run:
```bash
python3 preprocessing/msmarco_subset.py
python3 preprocessing/load_dataset.py
```

This generates 384-dimensional embeddings using `all-MiniLM-L6-v2` and inserts each
passage, category, relevance flag, and embedding into the `passages` table.

## Running the Application

### CLI demo

```bash
python3 backend/demo.py
```

### Benchmark

```bash
python3 backend/benchmark.py
```

Reports query text, filter category, estimated selectivity, selected strategy, execution
time, and rows returned for each query in the workload.

### Web UI

```bash
python3 frontend/app.py
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

## Notes

This is an academic prototype scoped to a single-machine, laptop-scale corpus
(~30k rows) and is not intended for production deployment, concurrent multi-user
serving, or the full 8.8-million-row MS MARCO corpus.