"""
TalentGPT - Database Models
SQLAlchemy ORM Models for all entities
"""

from sqlalchemy import (
    Column, String, Float, Integer, Boolean, 
    DateTime, Text, JSON, ForeignKey, Enum
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from datetime import datetime
import uuid
import enum

Base = declarative_base()


def generate_uuid():
    return str(uuid.uuid4())


class SeniorityLevel(str, enum.Enum):
    INTERN = "intern"
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    PRINCIPAL = "principal"
    DIRECTOR = "director"
    VP = "vp"
    C_LEVEL = "c_level"


class FeedbackType(str, enum.Enum):
    LIKED = "liked"
    SHORTLISTED = "shortlisted"
    REJECTED = "rejected"
    HIRED = "hired"
    INTERVIEWED = "interviewed"


# ─── JOB DESCRIPTION ────────────────────────────────────────────────────────


class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id = Column(UUID, primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    company = Column(String(255))
    raw_text = Column(Text, nullable=False)
    
    # AI-extracted structured data
    required_skills = Column(JSON, default=list)       # ["Python", "SQL", ...]
    preferred_skills = Column(JSON, default=list)
    hidden_skills = Column(JSON, default=list)         # Inferred by AI
    technical_requirements = Column(JSON, default=list)
    soft_skills = Column(JSON, default=list)
    leadership_indicators = Column(JSON, default=list)
    
    experience_min_years = Column(Integer)
    experience_max_years = Column(Integer)
    seniority_level = Column(String(50))
    industry = Column(String(100))
    department = Column(String(100))
    location = Column(String(255))
    remote_option = Column(Boolean, default=False)
    
    # Role embedding vector (stored as JSON array for portability)
    role_embedding = Column(JSON)  
    
    # Capability graph
    capability_graph = Column(JSON)
    
    # Structured role profile
    role_profile = Column(JSON)
    
    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    rankings = relationship("CandidateRanking", back_populates="job")
    

# ─── CANDIDATE ──────────────────────────────────────────────────────────────


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(UUID, primary_key=True, default=generate_uuid)
    
    # Basic info
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True)
    phone = Column(String(50))
    location = Column(String(255))
    headline = Column(String(500))
    
    # Raw data
    raw_resume = Column(Text)
    raw_profile = Column(JSON)  # Platform profile data
    
    # AI-extracted: Technical profile
    technical_skills = Column(JSON, default=list)      # [{"skill": "Python", "proficiency": 90}]
    domain_expertise = Column(JSON, default=list)
    certifications = Column(JSON, default=list)
    education = Column(JSON, default=list)
    
    # Career data
    employment_history = Column(JSON, default=list)    # [{company, role, duration, impact}]
    total_experience_years = Column(Float, default=0)
    career_progression_score = Column(Float, default=0)  # 0-100
    
    # AI-computed signals
    learning_velocity = Column(Float, default=0)       # 0-100
    leadership_score = Column(Float, default=0)
    collaboration_score = Column(Float, default=0)
    communication_score = Column(Float, default=0)
    project_complexity_score = Column(Float, default=0)
    achievement_score = Column(Float, default=0)
    
    # Behavioral signals
    platform_activity_score = Column(Float, default=0)
    consistency_score = Column(Float, default=0)
    reliability_score = Column(Float, default=0)
    
    # Candidate Capability Vector
    capability_vector = Column(JSON)  # {"AI": 92, "Backend": 89, ...}
    
    # Embedding vector
    candidate_embedding = Column(JSON)
    
    # Metadata
    is_active = Column(Boolean, default=True)
    profile_completeness = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    rankings = relationship("CandidateRanking", back_populates="candidate")
    feedbacks = relationship("RecruiterFeedback", back_populates="candidate")


# ─── CANDIDATE RANKING ───────────────────────────────────────────────────────


class CandidateRanking(Base):
    __tablename__ = "candidate_rankings"

    id = Column(UUID, primary_key=True, default=generate_uuid)
    job_id = Column(UUID, ForeignKey("job_descriptions.id"), nullable=False)
    candidate_id = Column(UUID, ForeignKey("candidates.id"), nullable=False)
    
    # Rank
    rank = Column(Integer)
    final_fit_score = Column(Float)  # 0-100
    
    # Agent scores
    skill_match_score = Column(Float)
    experience_score = Column(Float)
    behavior_score = Column(Float)
    learning_score = Column(Float)
    leadership_score = Column(Float)
    culture_fit_score = Column(Float)
    
    # Explainability
    strengths = Column(JSON, default=list)
    weaknesses = Column(JSON, default=list)
    risks = Column(JSON, default=list)
    missing_skills = Column(JSON, default=list)
    growth_potential = Column(String(50))  # "High" / "Medium" / "Low"
    recruiter_summary = Column(Text)
    
    # Success predictions
    interview_success_probability = Column(Float)
    offer_acceptance_probability = Column(Float)
    retention_probability = Column(Float)
    high_performer_probability = Column(Float)
    leadership_potential_score = Column(Float)
    
    # Metadata
    computed_at = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    job = relationship("JobDescription", back_populates="rankings")
    candidate = relationship("Candidate", back_populates="rankings")


# ─── RECRUITER FEEDBACK ──────────────────────────────────────────────────────


class RecruiterFeedback(Base):
    __tablename__ = "recruiter_feedbacks"

    id = Column(UUID, primary_key=True, default=generate_uuid)
    candidate_id = Column(UUID, ForeignKey("candidates.id"), nullable=False)
    job_id = Column(UUID, ForeignKey("job_descriptions.id"))
    recruiter_id = Column(String(255))  # Auth user ID
    
    feedback_type = Column(String(50), nullable=False)  # FeedbackType enum
    reason = Column(Text)
    notes = Column(Text)
    
    # Learning signal weights
    signal_weight = Column(Float, default=1.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    candidate = relationship("Candidate", back_populates="feedbacks")


# ─── CHAT SESSION ────────────────────────────────────────────────────────────


class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(UUID, primary_key=True, default=generate_uuid)
    recruiter_id = Column(String(255))
    job_id = Column(UUID, ForeignKey("job_descriptions.id"), nullable=True)
    
    messages = Column(JSON, default=list)  # [{role, content, timestamp}]
    context = Column(JSON, default=dict)   # Active filters, candidate list, etc.
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
