-- ============================================================
-- TalentGPT - Complete Database Schema
-- PostgreSQL 15
-- ============================================================

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgvector";  -- For vector similarity search

-- ─── JOB DESCRIPTIONS ────────────────────────────────────────────────────────

CREATE TABLE job_descriptions (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title           VARCHAR(255) NOT NULL,
    company         VARCHAR(255),
    raw_text        TEXT NOT NULL,
    
    -- AI-extracted structured data
    required_skills         JSONB DEFAULT '[]',
    preferred_skills        JSONB DEFAULT '[]',
    hidden_skills           JSONB DEFAULT '[]',
    technical_requirements  JSONB DEFAULT '[]',
    soft_skills             JSONB DEFAULT '[]',
    leadership_indicators   JSONB DEFAULT '[]',
    
    -- Requirements
    experience_min_years    INTEGER DEFAULT 0,
    experience_max_years    INTEGER DEFAULT 20,
    seniority_level         VARCHAR(50),
    industry                VARCHAR(100),
    department              VARCHAR(100),
    location                VARCHAR(255),
    remote_option           BOOLEAN DEFAULT FALSE,
    
    -- AI artifacts
    role_embedding          vector(384),    -- Sentence transformer embedding
    role_profile            JSONB,          -- Full structured profile
    capability_graph        JSONB,          -- Skill dependency graph
    
    -- Meta
    is_active               BOOLEAN DEFAULT TRUE,
    created_by              VARCHAR(255),
    created_at              TIMESTAMPTZ DEFAULT NOW(),
    updated_at              TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_jd_active ON job_descriptions(is_active);
CREATE INDEX idx_jd_seniority ON job_descriptions(seniority_level);
CREATE INDEX idx_jd_embedding ON job_descriptions USING ivfflat (role_embedding vector_cosine_ops);

-- ─── CANDIDATES ──────────────────────────────────────────────────────────────

CREATE TABLE candidates (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Identity
    name            VARCHAR(255) NOT NULL,
    email           VARCHAR(255) UNIQUE,
    phone           VARCHAR(50),
    location        VARCHAR(255),
    headline        VARCHAR(500),
    
    -- Raw data sources
    raw_resume              TEXT,
    raw_profile             JSONB,
    
    -- AI-extracted profile
    technical_skills        JSONB DEFAULT '[]',
    domain_expertise        JSONB DEFAULT '[]',
    certifications          JSONB DEFAULT '[]',
    education               JSONB DEFAULT '[]',
    employment_history      JSONB DEFAULT '[]',
    key_achievements        JSONB DEFAULT '[]',
    
    -- Computed metrics
    total_experience_years  DECIMAL(4,1) DEFAULT 0,
    career_progression_score DECIMAL(5,2),
    learning_velocity       DECIMAL(5,2),
    leadership_score        DECIMAL(5,2),
    collaboration_score     DECIMAL(5,2),
    communication_score     DECIMAL(5,2),
    project_complexity_score DECIMAL(5,2),
    achievement_score       DECIMAL(5,2),
    
    -- Behavioral signals
    platform_activity_score DECIMAL(5,2),
    consistency_score       DECIMAL(5,2),
    reliability_score       DECIMAL(5,2),
    
    -- AI artifacts
    capability_vector       JSONB,          -- {"AI": 92, "Backend": 89, ...}
    candidate_embedding     vector(384),    -- Sentence transformer embedding
    
    -- Profile quality
    profile_completeness    DECIMAL(5,2) DEFAULT 0,
    
    -- Meta
    is_active               BOOLEAN DEFAULT TRUE,
    source                  VARCHAR(100),   -- "resume_upload", "platform", "api"
    created_at              TIMESTAMPTZ DEFAULT NOW(),
    updated_at              TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_candidates_email ON candidates(email);
CREATE INDEX idx_candidates_active ON candidates(is_active);
CREATE INDEX idx_candidates_experience ON candidates(total_experience_years);
CREATE INDEX idx_candidates_embedding ON candidates USING ivfflat (candidate_embedding vector_cosine_ops);
CREATE INDEX idx_candidates_profile_gin ON candidates USING gin(technical_skills);

-- ─── CANDIDATE RANKINGS ──────────────────────────────────────────────────────

CREATE TABLE candidate_rankings (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id          UUID NOT NULL REFERENCES job_descriptions(id) ON DELETE CASCADE,
    candidate_id    UUID NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    
    -- Ranking
    rank                    INTEGER,
    final_fit_score         DECIMAL(5,2),
    
    -- Agent scores (0-100 each)
    skill_match_score       DECIMAL(5,2),
    experience_score        DECIMAL(5,2),
    behavior_score          DECIMAL(5,2),
    learning_score          DECIMAL(5,2),
    leadership_score        DECIMAL(5,2),
    culture_fit_score       DECIMAL(5,2),
    
    -- Agent details (full agent output)
    agent_details           JSONB DEFAULT '{}',
    
    -- Explainability
    strengths               JSONB DEFAULT '[]',
    weaknesses              JSONB DEFAULT '[]',
    risks                   JSONB DEFAULT '[]',
    missing_skills          JSONB DEFAULT '[]',
    growth_potential        VARCHAR(20),        -- "High", "Medium", "Low"
    recruiter_summary       TEXT,
    
    -- Success predictions
    interview_success_prob  DECIMAL(4,3),
    offer_acceptance_prob   DECIMAL(4,3),
    retention_probability   DECIMAL(4,3),
    high_performer_prob     DECIMAL(4,3),
    leadership_potential    DECIMAL(4,3),
    
    -- Status
    status                  VARCHAR(50) DEFAULT 'active',  -- active, shortlisted, rejected, hired
    
    -- Meta
    computed_at             TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(job_id, candidate_id)
);

CREATE INDEX idx_rankings_job ON candidate_rankings(job_id);
CREATE INDEX idx_rankings_score ON candidate_rankings(job_id, final_fit_score DESC);
CREATE INDEX idx_rankings_status ON candidate_rankings(job_id, status);

-- ─── RECRUITER FEEDBACK ──────────────────────────────────────────────────────

CREATE TABLE recruiter_feedbacks (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    candidate_id    UUID NOT NULL REFERENCES candidates(id),
    job_id          UUID REFERENCES job_descriptions(id),
    recruiter_id    VARCHAR(255),
    
    feedback_type   VARCHAR(50) NOT NULL,   -- liked, shortlisted, rejected, hired, interviewed
    reason          TEXT,
    notes           TEXT,
    
    -- RL signal
    signal_weight   DECIMAL(3,2) DEFAULT 1.0,   -- Weighted importance
    is_processed    BOOLEAN DEFAULT FALSE,       -- Has been used for retraining
    
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_feedback_candidate ON recruiter_feedbacks(candidate_id);
CREATE INDEX idx_feedback_job ON recruiter_feedbacks(job_id);
CREATE INDEX idx_feedback_unprocessed ON recruiter_feedbacks(is_processed) WHERE NOT is_processed;

-- ─── CHAT SESSIONS ───────────────────────────────────────────────────────────

CREATE TABLE chat_sessions (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    recruiter_id    VARCHAR(255),
    job_id          UUID REFERENCES job_descriptions(id),
    
    messages        JSONB DEFAULT '[]',     -- Full conversation history
    context         JSONB DEFAULT '{}',     -- Active job, filters, etc.
    
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ─── RANKING TASKS ───────────────────────────────────────────────────────────

CREATE TABLE ranking_tasks (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id          UUID NOT NULL REFERENCES job_descriptions(id),
    
    status          VARCHAR(50) DEFAULT 'pending',  -- pending, running, completed, failed
    progress_pct    INTEGER DEFAULT 0,
    total_candidates INTEGER,
    processed_candidates INTEGER DEFAULT 0,
    
    error_message   TEXT,
    started_at      TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ─── ANALYTICS SNAPSHOTS ─────────────────────────────────────────────────────

CREATE TABLE analytics_snapshots (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id          UUID REFERENCES job_descriptions(id),
    snapshot_date   DATE DEFAULT CURRENT_DATE,
    
    metrics         JSONB,  -- Flexible analytics data
    
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ─── VIEWS ───────────────────────────────────────────────────────────────────

-- Top candidates per job
CREATE OR REPLACE VIEW v_top_candidates AS
SELECT 
    cr.job_id,
    cr.rank,
    cr.final_fit_score,
    cr.skill_match_score,
    cr.experience_score,
    cr.learning_score,
    cr.leadership_score,
    cr.strengths,
    cr.weaknesses,
    cr.growth_potential,
    cr.recruiter_summary,
    cr.interview_success_prob,
    cr.retention_probability,
    c.id as candidate_id,
    c.name,
    c.email,
    c.headline,
    c.location,
    c.total_experience_years,
    c.technical_skills,
    c.capability_vector
FROM candidate_rankings cr
JOIN candidates c ON c.id = cr.candidate_id
WHERE cr.status = 'active'
ORDER BY cr.job_id, cr.rank;

-- Job analytics
CREATE OR REPLACE VIEW v_job_analytics AS
SELECT
    jd.id as job_id,
    jd.title,
    jd.company,
    COUNT(cr.id) as total_ranked,
    AVG(cr.final_fit_score) as avg_fit_score,
    MAX(cr.final_fit_score) as top_score,
    COUNT(CASE WHEN cr.final_fit_score >= 85 THEN 1 END) as strong_matches,
    COUNT(CASE WHEN cr.final_fit_score >= 70 THEN 1 END) as good_matches,
    COUNT(CASE WHEN cr.status = 'shortlisted' THEN 1 END) as shortlisted,
    COUNT(CASE WHEN cr.status = 'hired' THEN 1 END) as hired
FROM job_descriptions jd
LEFT JOIN candidate_rankings cr ON cr.job_id = jd.id
GROUP BY jd.id, jd.title, jd.company;
