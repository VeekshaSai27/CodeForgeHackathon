-- ============================================================
-- Skill Intelligence Platform — PostgreSQL Schema
-- ============================================================

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================
-- 1. USER DOMAIN
-- ============================================================

CREATE TABLE users (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        TEXT NOT NULL,
    email       TEXT NOT NULL UNIQUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE user_profiles (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id      UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    resume_text  TEXT,
    github_url   TEXT,
    linkedin_url TEXT,
    preferences  JSONB NOT NULL DEFAULT '{}',
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- 2. SKILL INTELLIGENCE DOMAIN
-- ============================================================

CREATE TABLE skills (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name       TEXT NOT NULL UNIQUE,
    category   TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE user_skills (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id          UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    skill_id         UUID NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    confidence_score FLOAT CHECK (confidence_score BETWEEN 0 AND 1),
    source           TEXT NOT NULL CHECK (source IN ('resume', 'inferred')),
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, skill_id)
);

CREATE TABLE job_roles (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title       TEXT NOT NULL,
    description TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE job_role_skills (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_role_id      UUID NOT NULL REFERENCES job_roles(id) ON DELETE CASCADE,
    skill_id         UUID NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    importance_score FLOAT CHECK (importance_score BETWEEN 0 AND 1),
    UNIQUE (job_role_id, skill_id)
);

-- ============================================================
-- 3. SKILL VALIDATION DOMAIN
-- ============================================================

CREATE TABLE assessments (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id          UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    skill_id         UUID NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    score            FLOAT CHECK (score BETWEEN 0 AND 1),
    difficulty_level TEXT CHECK (difficulty_level IN ('beginner', 'intermediate', 'advanced')),
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE assessment_questions (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assessment_id  UUID NOT NULL REFERENCES assessments(id) ON DELETE CASCADE,
    question_text  TEXT NOT NULL,
    options        JSONB NOT NULL DEFAULT '[]',
    correct_answer TEXT NOT NULL,
    user_answer    TEXT,
    is_correct     BOOLEAN
);

-- ============================================================
-- 4. SKILL GRAPH DOMAIN
-- ============================================================

CREATE TABLE skill_graph_nodes (
    id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    skill_id UUID NOT NULL REFERENCES skills(id) ON DELETE CASCADE UNIQUE,
    metadata JSONB NOT NULL DEFAULT '{}'
);

CREATE TABLE skill_graph_edges (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    from_skill_id UUID NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    to_skill_id   UUID NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    weight        FLOAT CHECK (weight BETWEEN 0 AND 1) DEFAULT 1.0,
    created_by    TEXT NOT NULL CHECK (created_by IN ('system', 'llm')),
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (from_skill_id, to_skill_id)
);

-- ============================================================
-- 5. DECISION ENGINE DATA
-- ============================================================

CREATE TABLE skill_scores (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id           UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    skill_id          UUID NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    importance        FLOAT CHECK (importance BETWEEN 0 AND 1),
    proficiency       FLOAT CHECK (proficiency BETWEEN 0 AND 1),
    dependency_score  FLOAT CHECK (dependency_score BETWEEN 0 AND 1),
    confidence        FLOAT CHECK (confidence BETWEEN 0 AND 1),
    final_score       FLOAT CHECK (final_score BETWEEN 0 AND 1),
    computed_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE learning_paths (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id    UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    is_active  BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE learning_path_nodes (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    path_id     UUID NOT NULL REFERENCES learning_paths(id) ON DELETE CASCADE,
    skill_id    UUID NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    order_index INT NOT NULL,
    score       FLOAT CHECK (score BETWEEN 0 AND 1),
    reasoning   TEXT,
    status      TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'completed', 'abandoned')),
    UNIQUE (path_id, skill_id)
);

-- ============================================================
-- 6. LEARNING EXPERIENCE DOMAIN
-- ============================================================

CREATE TABLE resources (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    skill_id         UUID NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    type             TEXT NOT NULL CHECK (type IN ('video', 'doc', 'practice')),
    title            TEXT NOT NULL,
    url              TEXT NOT NULL,
    difficulty_level TEXT CHECK (difficulty_level IN ('beginner', 'intermediate', 'advanced'))
);

CREATE TABLE user_progress (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id      UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    skill_id     UUID NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    progress     FLOAT NOT NULL DEFAULT 0.0 CHECK (progress BETWEEN 0 AND 1),
    last_updated TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, skill_id)
);

-- ============================================================
-- 7. LEARNING JOURNEY TRACKING
-- ============================================================

CREATE TABLE user_journeys (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id      UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    path_id      UUID NOT NULL REFERENCES learning_paths(id) ON DELETE CASCADE,
    started_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE TABLE journey_events (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    journey_id UUID NOT NULL REFERENCES user_journeys(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL CHECK (event_type IN ('started', 'completed', 'abandoned', 'test_taken')),
    metadata   JSONB NOT NULL DEFAULT '{}',
    timestamp  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- 8. LOGGING & OBSERVABILITY
-- ============================================================

CREATE TABLE system_logs (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service_name TEXT NOT NULL,
    event_type   TEXT NOT NULL,
    payload      JSONB NOT NULL DEFAULT '{}',
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE decision_logs (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID REFERENCES users(id) ON DELETE SET NULL,
    input_data  JSONB NOT NULL DEFAULT '{}',
    output_data JSONB NOT NULL DEFAULT '{}',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- INDEXES
-- ============================================================

-- user_id indexes (cross-service lookups)
CREATE INDEX idx_user_profiles_user_id       ON user_profiles(user_id);
CREATE INDEX idx_user_skills_user_id         ON user_skills(user_id);
CREATE INDEX idx_assessments_user_id         ON assessments(user_id);
CREATE INDEX idx_skill_scores_user_id        ON skill_scores(user_id);
CREATE INDEX idx_learning_paths_user_id      ON learning_paths(user_id);
CREATE INDEX idx_user_progress_user_id       ON user_progress(user_id);
CREATE INDEX idx_user_journeys_user_id       ON user_journeys(user_id);
CREATE INDEX idx_decision_logs_user_id       ON decision_logs(user_id);

-- skill_id indexes (graph + scoring lookups)
CREATE INDEX idx_user_skills_skill_id        ON user_skills(skill_id);
CREATE INDEX idx_assessments_skill_id        ON assessments(skill_id);
CREATE INDEX idx_skill_scores_skill_id       ON skill_scores(skill_id);
CREATE INDEX idx_learning_path_nodes_skill   ON learning_path_nodes(skill_id);
CREATE INDEX idx_resources_skill_id          ON resources(skill_id);
CREATE INDEX idx_user_progress_skill_id      ON user_progress(skill_id);
CREATE INDEX idx_graph_edges_from            ON skill_graph_edges(from_skill_id);
CREATE INDEX idx_graph_edges_to              ON skill_graph_edges(to_skill_id);

-- job_role_id indexes
CREATE INDEX idx_job_role_skills_job_role_id ON job_role_skills(job_role_id);

-- temporal indexes (log/event queries)
CREATE INDEX idx_system_logs_created_at      ON system_logs(created_at DESC);
CREATE INDEX idx_journey_events_timestamp    ON journey_events(timestamp DESC);
CREATE INDEX idx_skill_scores_computed_at    ON skill_scores(computed_at DESC);

-- JSONB GIN indexes (flexible metadata queries)
CREATE INDEX idx_user_profiles_preferences   ON user_profiles USING GIN (preferences);
CREATE INDEX idx_system_logs_payload         ON system_logs USING GIN (payload);
CREATE INDEX idx_journey_events_metadata     ON journey_events USING GIN (metadata);
