"""
TalentGPT - JD Intelligence Engine
Deeply understands job descriptions, extracts hidden requirements,
generates role embeddings and capability graphs.
"""

import json
import re
from typing import Dict, List, Optional
from anthropic import AsyncAnthropic

from app.core.config import settings

client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)


class JDIntelligenceEngine:
    """
    Transforms raw job descriptions into structured intelligence profiles.
    Goes beyond keywords — infers hidden requirements, seniority signals,
    and builds a capability graph.
    """

    async def analyze(self, jd_text: str, company_name: str = "", title: str = "") -> Dict:
        """Full analysis pipeline for a job description."""
        
        # Run extractions in parallel
        import asyncio
        role_profile, capability_graph = await asyncio.gather(
            self._extract_role_profile(jd_text, company_name, title),
            self._build_capability_graph(jd_text),
        )
        
        return {
            "role_profile": role_profile,
            "capability_graph": capability_graph,
            "seniority_level": role_profile.get("seniority_level", "mid"),
            "required_skills": role_profile.get("required_skills", []),
            "preferred_skills": role_profile.get("preferred_skills", []),
            "hidden_skills": role_profile.get("hidden_skills", []),
            "technical_requirements": role_profile.get("technical_requirements", []),
            "soft_skills": role_profile.get("soft_skills", []),
            "leadership_indicators": role_profile.get("leadership_indicators", []),
            "experience_min_years": role_profile.get("experience_min_years", 0),
            "experience_max_years": role_profile.get("experience_max_years", 20),
            "industry": role_profile.get("industry", "Technology"),
        }

    async def _extract_role_profile(self, jd_text: str, company: str, title: str) -> Dict:
        """Use LLM to extract structured role profile from JD text."""
        
        prompt = f"""
You are an expert technical recruiter and AI architect. Analyze this job description deeply.

JOB TITLE: {title}
COMPANY: {company}
JOB DESCRIPTION:
{jd_text}

Extract a comprehensive structured role profile. Think like an elite recruiter who reads between the lines.

Return ONLY valid JSON with this exact structure:
{{
  "required_skills": ["skill1", "skill2"],
  "preferred_skills": ["skill3"],
  "hidden_skills": ["inferred skill not explicitly stated but clearly needed"],
  "technical_requirements": ["specific tech requirement"],
  "soft_skills": ["communication", "leadership"],
  "leadership_indicators": ["manages team", "leads projects"],
  "experience_min_years": 3,
  "experience_max_years": 8,
  "seniority_level": "senior",
  "industry": "FinTech",
  "department": "Engineering",
  "key_responsibilities": ["responsibility 1"],
  "success_indicators": ["what makes someone great in this role"],
  "red_flags_for_rejection": ["what would disqualify a candidate"],
  "growth_opportunities": ["what candidate can learn/grow into"],
  "team_size_context": "small startup / large enterprise / etc",
  "work_style": "collaborative / independent / hybrid"
}}

For hidden_skills: Look for implied requirements. E.g. "building scalable APIs" implies "system design". "Working with PMs" implies "cross-functional communication". Be insightful.
For seniority_level: Must be one of: intern, junior, mid, senior, lead, principal, director, vp, c_level
"""
        
        response = await client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2000,
            system="You are an expert AI recruiter. Extract structured data from job descriptions. Return only valid JSON.",
            messages=[{"role": "user", "content": prompt}]
        )
        
        text = response.content[0].text
        return self._safe_json(text)

    async def _build_capability_graph(self, jd_text: str) -> Dict:
        """Build a capability graph showing skill relationships for this role."""
        
        prompt = f"""
Analyze this job description and build a capability graph.

JOB DESCRIPTION:
{jd_text}

A capability graph shows:
1. Core competency clusters (e.g. "ML/AI", "Backend Engineering", "Leadership")
2. Skills within each cluster
3. Importance weights (1-10)
4. Dependencies between skills

Return ONLY valid JSON:
{{
  "clusters": [
    {{
      "name": "Machine Learning",
      "importance": 10,
      "skills": [
        {{"name": "Python", "importance": 10, "type": "required"}},
        {{"name": "PyTorch", "importance": 9, "type": "required"}},
        {{"name": "MLflow", "importance": 6, "type": "preferred"}}
      ]
    }},
    {{
      "name": "MLOps",
      "importance": 8,
      "skills": [
        {{"name": "Docker", "importance": 8, "type": "required"}},
        {{"name": "Kubernetes", "importance": 7, "type": "preferred"}}
      ]
    }}
  ],
  "critical_path": ["most important skill 1", "most important skill 2"],
  "nice_to_have_cluster": ["bonus skill 1"]
}}
"""
        
        response = await client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1500,
            system="You are an expert technical architect. Build capability graphs from job descriptions. Return only valid JSON.",
            messages=[{"role": "user", "content": prompt}]
        )
        
        return self._safe_json(response.content[0].text)

    def _safe_json(self, text: str) -> Dict:
        """Safely parse JSON from LLM output."""
        try:
            return json.loads(text)
        except:
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except:
                    pass
        return {}


# ─── CANDIDATE INTELLIGENCE ENGINE ───────────────────────────────────────────


class CandidateIntelligenceEngine:
    """
    Transforms raw candidate data (resume + profile) into a structured 
    360-degree intelligence profile with capability vectors.
    """

    async def analyze(self, resume_text: str = "", profile_data: Dict = None) -> Dict:
        """Full candidate analysis pipeline."""
        
        profile_data = profile_data or {}
        import asyncio
        
        extracted, capability_vector = await asyncio.gather(
            self._extract_candidate_profile(resume_text, profile_data),
            self._compute_capability_vector(resume_text, profile_data),
        )
        
        return {
            **extracted,
            "capability_vector": capability_vector,
        }

    async def _extract_candidate_profile(self, resume: str, profile: Dict) -> Dict:
        """Extract structured intelligence from candidate data."""
        
        prompt = f"""
You are an expert AI recruiter analyzing a candidate. Extract deep insights.

RESUME:
{resume[:3000] if resume else "Not provided"}

PROFILE DATA:
{json.dumps(profile, indent=2)[:2000] if profile else "Not provided"}

Extract comprehensive candidate intelligence. Return ONLY valid JSON:
{{
  "technical_skills": [
    {{"skill": "Python", "proficiency": 90, "years": 5}},
    {{"skill": "FastAPI", "proficiency": 85, "years": 3}}
  ],
  "domain_expertise": ["Machine Learning", "Backend Engineering"],
  "certifications": [
    {{"name": "AWS Solutions Architect", "issuer": "Amazon", "year": 2023, "relevance": "high"}}
  ],
  "education": [
    {{"degree": "B.Tech Computer Science", "institution": "IIT Bombay", "year": 2019, "gpa": "8.5/10"}}
  ],
  "employment_history": [
    {{
      "company": "TechCorp",
      "role": "Senior Engineer",
      "duration_years": 2.5,
      "impact": "Led migration of monolith to microservices, reducing latency 40%",
      "technologies": ["Python", "AWS", "Docker"],
      "team_size": 8
    }}
  ],
  "total_experience_years": 6,
  "career_progression_score": 82,
  "learning_velocity": 88,
  "leadership_score": 72,
  "collaboration_score": 85,
  "communication_score": 78,
  "project_complexity_score": 80,
  "achievement_score": 75,
  "platform_activity_score": 70,
  "consistency_score": 80,
  "reliability_score": 85,
  "key_achievements": ["achievement 1", "achievement 2"],
  "unique_value_proposition": "What makes this candidate special in 1 sentence"
}}

Be analytical. Look for:
- Quantified achievements (numbers, percentages, scale)
- Career growth patterns  
- Hidden leadership (mentoring, owning projects solo)
- Technology breadth and depth
- Learning from newer tech stack
"""
        
        response = await client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2000,
            system="You are an expert AI recruiter. Extract structured candidate intelligence. Return only valid JSON.",
            messages=[{"role": "user", "content": prompt}]
        )
        
        return self._safe_json(response.content[0].text)

    async def _compute_capability_vector(self, resume: str, profile: Dict) -> Dict:
        """Generate the candidate capability vector — a numeric fingerprint."""
        
        prompt = f"""
Analyze this candidate and generate their capability vector — numeric scores across key dimensions.

RESUME: {resume[:2000] if resume else "N/A"}
PROFILE: {json.dumps(profile)[:1000] if profile else "N/A"}

Return ONLY valid JSON with scores 0-100:
{{
  "AI_ML": 85,
  "Backend_Engineering": 90,
  "Frontend_Engineering": 40,
  "Data_Engineering": 70,
  "DevOps_Cloud": 65,
  "System_Design": 78,
  "Leadership": 72,
  "Communication": 80,
  "Problem_Solving": 88,
  "Learning_Velocity": 90,
  "Domain_Finance": 30,
  "Domain_Healthcare": 10,
  "Domain_Ecommerce": 50,
  "OSS_Contribution": 60,
  "Research_Publications": 40
}}

Score honestly based on evidence in the profile. Missing evidence = lower score.
"""
        
        response = await client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=800,
            system="You are a technical assessment expert. Generate capability vectors from candidate profiles. Return only valid JSON.",
            messages=[{"role": "user", "content": prompt}]
        )
        
        return self._safe_json(response.content[0].text)

    def _safe_json(self, text: str) -> Dict:
        try:
            return json.loads(text)
        except:
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except:
                    pass
        return {}
