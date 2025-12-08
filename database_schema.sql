-- Database Schema Export
-- Generated: 2025-12-07T23:01:57.986194
-- Supabase Project: https://smxhdiixzjdwomecvcpw.supabase.co

-- ============================================================
-- TABLE: client_learning_pages
-- ============================================================
CREATE TABLE client_learning_pages (
    id integer,
    client_id text,
    page_index integer,
    content jsonb,
    created_at text,
    updated_at text
);  
-- Row count: 6

-- ============================================================
-- TABLE: junior_leads
-- ============================================================
CREATE TABLE junior_leads (
    id text,
    name text,
    email text,
    description text,
    status text,
    created_at text,
    input_transform jsonb,
    plan text
);
-- Row count: 5
