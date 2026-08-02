CREATE EXTENSION IF NOT EXISTS vector;

DROP TABLE IF EXISTS passages;

CREATE TABLE passages (
    id SERIAL PRIMARY KEY,
    text TEXT NOT NULL,
    category TEXT,
    is_relevant BOOLEAN,
    embedding vector(384)
);

CREATE INDEX passages_category_idx ON passages (category);


CREATE INDEX passages_embedding_hnsw ON passages USING hnsw (embedding vector_cosine_ops);