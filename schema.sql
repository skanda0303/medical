-- schema.sql
-- This file creates the necessary extensions, the medicines table, 
-- specialized search columns (tsvector), and performance indexes (GIN/B-tree).

-- 1. EXTENSIONS
-- Required for Fuzzy Search (%%) and Substring Search (similarity()).
CREATE EXTENSION IF NOT EXISTS pg_trgm; 
-- Required for better Full-Text Search language handling.
CREATE EXTENSION IF NOT EXISTS unaccent; 

-- 2. MEDICINES TABLE CREATION
CREATE TABLE medicines (
    -- Core Fields (matched from JSON data)
    id TEXT PRIMARY KEY,
    sku_id TEXT,
    name TEXT NOT NULL,
    manufacturer_name TEXT,
    marketer_name TEXT,
    type TEXT,
    price NUMERIC,
    pack_size_label TEXT,
    short_composition TEXT,
    
    -- Added fields to match complete JSON structure
    rx_required TEXT,       -- Altered from BOOLEAN to TEXT to handle inconsistent JSON data
    slug TEXT,
    image_url TEXT,
    
    -- Remaining fields
    is_discontinued BOOLEAN DEFAULT false,
    available BOOLEAN DEFAULT true,

    -- Specialized Search Field (Full-Text)
    search_tsv tsvector
);

-- 3. FULL-TEXT SEARCH (TSVECTOR) SETUP

-- Function to update the search_tsv column on every insert or update.
-- Weights (A, B, C, D) define relevance: A is highest (for name).
CREATE OR REPLACE FUNCTION medicines_search_tsv_trigger() RETURNS trigger AS $$
BEGIN
  NEW.search_tsv :=
     setweight(to_tsvector('english', coalesce(NEW.name,'')), 'A') ||
     setweight(to_tsvector('english', coalesce(NEW.short_composition,'')), 'B') ||
     setweight(to_tsvector('english', coalesce(NEW.manufacturer_name,'')), 'C') ||
     setweight(to_tsvector('english', coalesce(NEW.type,'')), 'D');
  RETURN NEW;
END
$$ LANGUAGE plpgsql;

-- Trigger to execute the function before insert or update
CREATE TRIGGER tsvectorupdate BEFORE INSERT OR UPDATE
  ON medicines FOR EACH ROW EXECUTE PROCEDURE medicines_search_tsv_trigger();

-- 4. PERFORMANCE INDEXES

-- A. Index for Fuzzy/Substring Search
-- GIN index using gin_trgm_ops is crucial for fast '%%' operator and similarity() ordering.
CREATE INDEX idx_medicines_name_trgm ON medicines USING gin (name gin_trgm_ops);

-- B. Index for Full-Text Search
-- GIN index on the search_tsv column for blazing-fast relevance queries.
CREATE INDEX idx_medicines_search_tsv ON medicines USING gin (search_tsv);

-- C. Index for Optimized Prefix Search (like 'query%')
-- B-tree index on the lowercase name is optimal for fast prefix lookups.
CREATE INDEX idx_medicines_name_lower ON medicines (lower(name) text_pattern_ops);
