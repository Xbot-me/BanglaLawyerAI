-- PostgreSQL 16 Database Schema for Bangladesh Legal Knowledge Platform
-- Enable pgvector and pg_trgm extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- 1. Acts Table (Law Codifications)
CREATE TABLE IF NOT EXISTS acts (
    act_id INTEGER PRIMARY KEY,
    act_name_en VARCHAR(255) NOT NULL,
    act_name_bn VARCHAR(255) NOT NULL,
    category VARCHAR(100) DEFAULT 'General Law',
    source_url TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Sections Table (Statutory Sections)
CREATE TABLE IF NOT EXISTS sections (
    id SERIAL PRIMARY KEY,
    act_id INTEGER REFERENCES acts(act_id) ON DELETE CASCADE,
    section_number VARCHAR(50) NOT NULL,
    section_title_en TEXT,
    section_title_bn TEXT,
    chapter_number VARCHAR(50),
    chapter_title TEXT,
    content_en TEXT,
    content_bn TEXT NOT NULL,
    easy_explanation_bn TEXT,
    source_url TEXT NOT NULL,
    keywords TEXT[],
    embedding vector(1024), -- 1024-dim dense vector embedding (bge-m3 / multilingual-e5)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_act_section UNIQUE (act_id, section_number)
);

-- 3. HNSW Vector Cosine Distance Index for Sub-millisecond Vector Search
CREATE INDEX IF NOT EXISTS sections_embedding_hnsw_idx 
ON sections USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- 4. Trigram Full-Text Search Index on Bengali & English Text
CREATE INDEX IF NOT EXISTS sections_content_bn_trgm_idx 
ON sections USING gin (content_bn gin_trgm_ops);

CREATE INDEX IF NOT EXISTS sections_title_bn_trgm_idx 
ON sections USING gin (section_title_bn gin_trgm_ops);
