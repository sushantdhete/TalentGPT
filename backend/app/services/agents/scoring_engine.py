"""
TalentGPT - Multi-Agent Scoring Engine
6 Independent AI Agents + Committee Ranking

Each agent scores candidates 0-100 independently.
The Committee Engine aggregates with configurable weights.
"""

import asyncio
import json
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from anthropic import AsyncAnthropic

from app.core.config import settings


client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)


# ─── DATA STRUCTURES ─────────────────────────────────────────────────────────


@dataclass
class AgentScore:
    score: float          # 0-100
    confidence: float     # 0-1
    reasoning: str
    details: Dict[str, Any]


@dataclass
class CommitteeDecision:
    final_fit_score: float
    rank_explanation: str
    
    # Individual agent scores
    skill_match_score: float
    experience_score: float
    behavior_score: float
    learning_score: float
    leadership_score: float
    culture_fit_score: float
    
    # Explainability
    strengths: List[str]
    weaknesses: List[str]
    risks: List[str]
    missing_skills: List[str]
    growth_potential: str   # "High" / "Medium" / "Low"
    recruiter_summary: str
    
    # Success predictions
    interview_success_probability: float
    offer_acceptance_probability: float
    retention_probability: float
    high_performer_probability: float
    leadership_potential_score: float


# ─── BASE AGENT ──────────────────────────────────────────────────────────────


class BaseAgent:
    """Base class for all scoring agents."""
    
    name: str = "BaseAgent"
    
    async def score(
        self,
        job_profile: Dict,
        candidate_profile: Dict
    ) -> AgentScore:
        raise NotImplementedError

    async def _call_llm(self, prompt: str, system: str = None) -> str:
        """Call Claude API for agent reasoning."""
        messages = [{"role": "user", "content": prompt}]
        
        response = await client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            system=system or "You are an expert AI recruiter agent. Respond only with valid JSON.",
            messages=messages,
        )
        return response.content[0].text

    def _extract_json(self, text: str) -> Dict:
        """Safely extract JSON from LLM response."""
        try:
            # Try direct parse
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to find JSON block
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except:
                    pass
        return {}


# ─── AGENT 1: SKILL MATCH ────────────────────────────────────────────────────


class SkillMatchAgent(BaseAgent):
    name = "SkillMatchAgent"

    async def score(self, job_profile: Dict, candidate_profile: Dict) -> AgentScore:
        prompt = f"""
Analyze the skill match between this job and candidate.

JOB REQUIRED SKILLS: {json.dumps(job_profile.get('required_skills', []))}
JOB PREFERRED SKILLS: {json.dumps(job_profile.get('preferred_skills', []))}
JOB HIDDEN SKILLS: {json.dumps(job_profile.get('hidden_skills', []))}

CANDIDATE TECHNICAL SKILLS: {json.dumps(candidate_profile.get('technical_skills', []))}
CANDIDATE DOMAIN EXPERTISE: {json.dumps(candidate_profile.get('domain_expertise', []))}

Evaluate:
1. Mandatory skill coverage (how many required skills does candidate have?)
2. Preferred skill coverage
3. Semantic skill similarity (e.g., "PyTorch" covers some "ML" requirements)
4. Depth of skills (expert vs beginner level)

Return JSON:
{{
  "score": <0-100>,
  "confidence": <0.0-1.0>,
  "mandatory_coverage_pct": <0-100>,
  "preferred_coverage_pct": <0-100>,
  "semantic_bonus": <0-15>,
  "matched_skills": ["skill1", "skill2"],
  "missing_required": ["skill3"],
  "reasoning": "2-3 sentence explanation"
}}
"""
        raw = await self._call_llm(prompt)
        data = self._extract_json(raw)
        
        score = min(100, max(0, float(data.get("score", 50))))
        return AgentScore(
            score=score,
            confidence=float(data.get("confidence", 0.7)),
            reasoning=data.get("reasoning", ""),
            details={
                "matched_skills": data.get("matched_skills", []),
                "missing_required": data.get("missing_required", []),
                "mandatory_coverage_pct": data.get("mandatory_coverage_pct", 0),
                "preferred_coverage_pct": data.get("preferred_coverage_pct", 0),
            }
        )


# ─── AGENT 2: EXPERIENCE ─────────────────────────────────────────────────────


class ExperienceAgent(BaseAgent):
    name = "ExperienceAgent"

    async def score(self, job_profile: Dict, candidate_profile: Dict) -> AgentScore:
        prompt = f"""
Evaluate the candidate's experience relevance for this role.

JOB SENIORITY: {job_profile.get('seniority_level', 'unknown')}
JOB INDUSTRY: {job_profile.get('industry', 'unknown')}
JOB MIN EXPERIENCE YEARS: {job_profile.get('experience_min_years', 0)}
JOB REQUIRED EXPERIENCE: {json.dumps(job_profile.get('technical_requirements', []))}

CANDIDATE TOTAL EXPERIENCE: {candidate_profile.get('total_experience_years', 0)} years
CANDIDATE EMPLOYMENT HISTORY: {json.dumps(candidate_profile.get('employment_history', [])[:5])}
CANDIDATE CAREER PROGRESSION SCORE: {candidate_profile.get('career_progression_score', 0)}

Evaluate:
1. Years of experience vs requirement
2. Domain/industry relevance
3. Career growth trajectory (are they progressing upward?)
4. Role complexity at previous companies

Return JSON:
{{
  "score": <0-100>,
  "confidence": <0.0-1.0>,
  "years_match": <"under" | "match" | "over">,
  "domain_relevance": <0-100>,
  "trajectory": <"ascending" | "lateral" | "declining">,
  "reasoning": "2-3 sentence explanation"
}}
"""
        raw = await self._call_llm(prompt)
        data = self._extract_json(raw)
        
        score = min(100, max(0, float(data.get("score", 50))))
        return AgentScore(
            score=score,
            confidence=float(data.get("confidence", 0.7)),
            reasoning=data.get("reasoning", ""),
            details={
                "years_match": data.get("years_match", "match"),
                "domain_relevance": data.get("domain_relevance", 50),
                "trajectory": data.get("trajectory", "lateral"),
            }
        )


# ─── AGENT 3: BEHAVIOR ───────────────────────────────────────────────────────


class BehaviorAgent(BaseAgent):
    name = "BehaviorAgent"

    async def score(self, job_profile: Dict, candidate_profile: Dict) -> AgentScore:
        prompt = f"""
Evaluate behavioral signals for this candidate.

CANDIDATE PLATFORM ACTIVITY SCORE: {candidate_profile.get('platform_activity_score', 50)}
CANDIDATE CONSISTENCY SCORE: {candidate_profile.get('consistency_score', 50)}
CANDIDATE RELIABILITY SCORE: {candidate_profile.get('reliability_score', 50)}
CANDIDATE EMPLOYMENT HISTORY (job hopping check): {json.dumps(candidate_profile.get('employment_history', [])[:5])}

Evaluate:
1. Job stability (avg tenure at companies)
2. Activity consistency on professional platforms
3. Reliability indicators from work patterns
4. Red flags (frequent short stints, gaps)

Return JSON:
{{
  "score": <0-100>,
  "confidence": <0.0-1.0>,
  "avg_tenure_years": <float>,
  "stability_flag": <"stable" | "moderate" | "high_churn">,
  "activity_level": <"high" | "medium" | "low">,
  "red_flags": ["flag1"],
  "reasoning": "2-3 sentence explanation"
}}
"""
        raw = await self._call_llm(prompt)
        data = self._extract_json(raw)
        
        score = min(100, max(0, float(data.get("score", 50))))
        return AgentScore(
            score=score,
            confidence=float(data.get("confidence", 0.7)),
            reasoning=data.get("reasoning", ""),
            details={
                "stability_flag": data.get("stability_flag", "moderate"),
                "red_flags": data.get("red_flags", []),
                "avg_tenure_years": data.get("avg_tenure_years", 1.5),
            }
        )


# ─── AGENT 4: LEARNING ───────────────────────────────────────────────────────


class LearningAgent(BaseAgent):
    name = "LearningAgent"

    async def score(self, job_profile: Dict, candidate_profile: Dict) -> AgentScore:
        prompt = f"""
Evaluate the learning velocity and growth potential of this candidate.

CANDIDATE CERTIFICATIONS: {json.dumps(candidate_profile.get('certifications', []))}
CANDIDATE LEARNING VELOCITY: {candidate_profile.get('learning_velocity', 50)}
CANDIDATE EDUCATION: {json.dumps(candidate_profile.get('education', []))}
CANDIDATE EMPLOYMENT HISTORY (technology adoption): {json.dumps(candidate_profile.get('employment_history', [])[:3])}

JOB TECHNOLOGY REQUIREMENTS: {json.dumps(job_profile.get('required_skills', [])[:10])}

Evaluate:
1. Recent certifications (relevance and recency)
2. How fast has candidate adopted new technologies?
3. Education quality and relevance
4. Self-learning indicators

Return JSON:
{{
  "score": <0-100>,
  "confidence": <0.0-1.0>,
  "relevant_certs": ["cert1"],
  "learning_rate": <"fast" | "average" | "slow">,
  "education_quality": <0-100>,
  "reasoning": "2-3 sentence explanation"
}}
"""
        raw = await self._call_llm(prompt)
        data = self._extract_json(raw)
        
        score = min(100, max(0, float(data.get("score", 50))))
        return AgentScore(
            score=score,
            confidence=float(data.get("confidence", 0.7)),
            reasoning=data.get("reasoning", ""),
            details={
                "relevant_certs": data.get("relevant_certs", []),
                "learning_rate": data.get("learning_rate", "average"),
                "education_quality": data.get("education_quality", 50),
            }
        )


# ─── AGENT 5: LEADERSHIP ─────────────────────────────────────────────────────


class LeadershipAgent(BaseAgent):
    name = "LeadershipAgent"

    async def score(self, job_profile: Dict, candidate_profile: Dict) -> AgentScore:
        prompt = f"""
Evaluate leadership potential and demonstrated leadership for this candidate.

JOB LEADERSHIP INDICATORS: {json.dumps(job_profile.get('leadership_indicators', []))}
JOB SENIORITY: {job_profile.get('seniority_level', 'unknown')}

CANDIDATE LEADERSHIP SCORE: {candidate_profile.get('leadership_score', 50)}
CANDIDATE EMPLOYMENT HISTORY (look for team lead, manager, mentor roles): {json.dumps(candidate_profile.get('employment_history', [])[:5])}
CANDIDATE COLLABORATION SCORE: {candidate_profile.get('collaboration_score', 50)}

Evaluate:
1. Team management experience
2. Mentorship and coaching indicators
3. Ownership and initiative signals
4. Seniority appropriate leadership

Return JSON:
{{
  "score": <0-100>,
  "confidence": <0.0-1.0>,
  "managed_teams": <boolean>,
  "max_team_size": <integer>,
  "mentorship_signals": <boolean>,
  "ownership_level": <"high" | "medium" | "low">,
  "reasoning": "2-3 sentence explanation"
}}
"""
        raw = await self._call_llm(prompt)
        data = self._extract_json(raw)
        
        score = min(100, max(0, float(data.get("score", 50))))
        return AgentScore(
            score=score,
            confidence=float(data.get("confidence", 0.7)),
            reasoning=data.get("reasoning", ""),
            details={
                "managed_teams": data.get("managed_teams", False),
                "ownership_level": data.get("ownership_level", "medium"),
            }
        )


# ─── AGENT 6: CULTURE FIT ────────────────────────────────────────────────────


class CultureFitAgent(BaseAgent):
    name = "CultureFitAgent"

    async def score(self, job_profile: Dict, candidate_profile: Dict) -> AgentScore:
        prompt = f"""
Evaluate culture fit and collaboration style for this candidate.

JOB SOFT SKILLS REQUIRED: {json.dumps(job_profile.get('soft_skills', []))}
JOB COMPANY/ROLE CONTEXT: {job_profile.get('title', '')} at {job_profile.get('company', '')}

CANDIDATE COMMUNICATION SCORE: {candidate_profile.get('communication_score', 50)}
CANDIDATE COLLABORATION SCORE: {candidate_profile.get('collaboration_score', 50)}
CANDIDATE HEADLINE: {candidate_profile.get('headline', '')}
CANDIDATE DOMAIN EXPERTISE: {json.dumps(candidate_profile.get('domain_expertise', [])[:3])}

Evaluate:
1. Communication style alignment
2. Collaboration vs independent work preference signals
3. Industry/domain cultural fit
4. Organizational size fit (startup vs enterprise)

Return JSON:
{{
  "score": <0-100>,
  "confidence": <0.0-1.0>,
  "communication_style": <"collaborative" | "independent" | "mixed">,
  "org_size_fit": <"startup" | "enterprise" | "any">,
  "culture_signals": ["signal1"],
  "reasoning": "2-3 sentence explanation"
}}
"""
        raw = await self._call_llm(prompt)
        data = self._extract_json(raw)
        
        score = min(100, max(0, float(data.get("score", 50))))
        return AgentScore(
            score=score,
            confidence=float(data.get("confidence", 0.7)),
            reasoning=data.get("reasoning", ""),
            details={
                "communication_style": data.get("communication_style", "mixed"),
                "org_size_fit": data.get("org_size_fit", "any"),
            }
        )


# ─── COMMITTEE RANKING ENGINE ─────────────────────────────────────────────────


class CommitteeRankingEngine:
    """
    Aggregates all agent scores with configurable weights.
    Generates explainable rankings and success predictions.
    """

    def __init__(self):
        self.agents = {
            "skill": SkillMatchAgent(),
            "experience": ExperienceAgent(),
            "behavior": BehaviorAgent(),
            "learning": LearningAgent(),
            "leadership": LeadershipAgent(),
            "culture": CultureFitAgent(),
        }
        
        # Configurable weights
        self.weights = {
            "skill": settings.WEIGHT_SKILLS,
            "experience": settings.WEIGHT_EXPERIENCE,
            "learning": settings.WEIGHT_LEARNING,
            "leadership": settings.WEIGHT_LEADERSHIP,
            "behavior": settings.WEIGHT_BEHAVIOR,
            "culture": settings.WEIGHT_CULTURE,
        }

    async def evaluate_candidate(
        self,
        job_profile: Dict,
        candidate_profile: Dict
    ) -> CommitteeDecision:
        """Run all agents in parallel and compute committee decision."""
        
        # Run all 6 agents concurrently
        results = await asyncio.gather(
            self.agents["skill"].score(job_profile, candidate_profile),
            self.agents["experience"].score(job_profile, candidate_profile),
            self.agents["behavior"].score(job_profile, candidate_profile),
            self.agents["learning"].score(job_profile, candidate_profile),
            self.agents["leadership"].score(job_profile, candidate_profile),
            self.agents["culture"].score(job_profile, candidate_profile),
            return_exceptions=True
        )
        
        # Unpack safely
        skill_r, exp_r, beh_r, learn_r, lead_r, cult_r = [
            r if isinstance(r, AgentScore) else AgentScore(50, 0.5, "Agent error", {})
            for r in results
        ]
        
        # Weighted final score
        final_score = (
            skill_r.score * self.weights["skill"] +
            exp_r.score * self.weights["experience"] +
            beh_r.score * self.weights["behavior"] +
            learn_r.score * self.weights["learning"] +
            lead_r.score * self.weights["leadership"] +
            cult_r.score * self.weights["culture"]
        )
        
        # Generate explanations
        explanation = await self._generate_explanation(
            job_profile, candidate_profile,
            skill_r, exp_r, beh_r, learn_r, lead_r, cult_r,
            final_score
        )
        
        # Predict success
        predictions = await self._predict_success(
            job_profile, candidate_profile, final_score,
            skill_r.score, exp_r.score, learn_r.score, lead_r.score
        )
        
        return CommitteeDecision(
            final_fit_score=round(final_score, 1),
            rank_explanation=explanation.get("rank_explanation", ""),
            skill_match_score=round(skill_r.score, 1),
            experience_score=round(exp_r.score, 1),
            behavior_score=round(beh_r.score, 1),
            learning_score=round(learn_r.score, 1),
            leadership_score=round(lead_r.score, 1),
            culture_fit_score=round(cult_r.score, 1),
            strengths=explanation.get("strengths", []),
            weaknesses=explanation.get("weaknesses", []),
            risks=explanation.get("risks", []),
            missing_skills=skill_r.details.get("missing_required", []),
            growth_potential=explanation.get("growth_potential", "Medium"),
            recruiter_summary=explanation.get("recruiter_summary", ""),
            interview_success_probability=predictions.get("interview_success", 0.6),
            offer_acceptance_probability=predictions.get("offer_acceptance", 0.7),
            retention_probability=predictions.get("retention", 0.65),
            high_performer_probability=predictions.get("high_performer", 0.5),
            leadership_potential_score=predictions.get("leadership_potential", 0.5),
        )

    async def _generate_explanation(
        self,
        job_profile: Dict,
        candidate_profile: Dict,
        skill_r: AgentScore,
        exp_r: AgentScore,
        beh_r: AgentScore,
        learn_r: AgentScore,
        lead_r: AgentScore,
        cult_r: AgentScore,
        final_score: float
    ) -> Dict:
        
        prompt = f"""
You are an expert AI recruiter providing hiring recommendations.

JOB: {job_profile.get('title', 'Unknown Role')}
CANDIDATE: {candidate_profile.get('name', 'Candidate')}

AGENT SCORES:
- Skill Match: {skill_r.score}/100 — {skill_r.reasoning}
- Experience: {exp_r.score}/100 — {exp_r.reasoning}
- Behavior: {beh_r.score}/100 — {beh_r.reasoning}
- Learning: {learn_r.score}/100 — {learn_r.reasoning}
- Leadership: {lead_r.score}/100 — {lead_r.reasoning}
- Culture Fit: {cult_r.score}/100 — {cult_r.reasoning}

FINAL FIT SCORE: {final_score:.1f}/100

Generate a recruiter-friendly explanation. Return JSON:
{{
  "rank_explanation": "One sentence explaining why this score",
  "strengths": ["strength1", "strength2", "strength3"],
  "weaknesses": ["weakness1", "weakness2"],
  "risks": ["risk1"],
  "growth_potential": "High|Medium|Low",
  "recruiter_summary": "2-3 sentence paragraph a recruiter would tell their hiring manager about this candidate"
}}
"""
        raw = await self._call_llm(prompt)
        return self._extract_json(raw)

    async def _predict_success(
        self,
        job_profile: Dict,
        candidate_profile: Dict,
        final_score: float,
        skill_score: float,
        exp_score: float,
        learn_score: float,
        lead_score: float
    ) -> Dict:
        """Predict hiring success probabilities."""
        # Heuristic-based predictions (can be replaced with trained ML model)
        base = final_score / 100
        
        interview_success = min(0.95, base * 0.9 + skill_score * 0.001 * 0.1)
        offer_acceptance = min(0.95, 0.5 + (exp_score / 100) * 0.3)  # experienced = more selective
        retention = min(0.95, base * 0.7 + learn_score * 0.001 * 0.3)
        high_performer = min(0.95, (skill_score * 0.4 + learn_score * 0.3 + exp_score * 0.3) / 100)
        leadership_potential = min(0.95, lead_score / 100)
        
        return {
            "interview_success": round(interview_success, 2),
            "offer_acceptance": round(offer_acceptance, 2),
            "retention": round(retention, 2),
            "high_performer": round(high_performer, 2),
            "leadership_potential": round(leadership_potential, 2),
        }

    async def _call_llm(self, prompt: str) -> str:
        response = await client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            system="You are an expert AI recruiter. Respond only with valid JSON.",
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text

    def _extract_json(self, text: str) -> Dict:
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


# ─── BATCH RANKING ───────────────────────────────────────────────────────────


async def rank_candidates_for_job(
    job_profile: Dict,
    candidates: List[Dict],
    max_concurrent: int = 5
) -> List[Dict]:
    """
    Rank all candidates for a job using the committee engine.
    Returns sorted list with scores and explanations.
    """
    engine = CommitteeRankingEngine()
    
    # Process in batches to avoid rate limits
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def evaluate_with_semaphore(candidate):
        async with semaphore:
            try:
                decision = await engine.evaluate_candidate(job_profile, candidate)
                return {
                    "candidate_id": candidate.get("id"),
                    "candidate_name": candidate.get("name"),
                    "decision": decision,
                }
            except Exception as e:
                return {
                    "candidate_id": candidate.get("id"),
                    "candidate_name": candidate.get("name"),
                    "error": str(e),
                    "decision": None,
                }
    
    results = await asyncio.gather(
        *[evaluate_with_semaphore(c) for c in candidates]
    )
    
    # Filter successful and sort by score
    scored = [
        r for r in results 
        if r.get("decision") is not None
    ]
    scored.sort(key=lambda x: x["decision"].final_fit_score, reverse=True)
    
    # Assign ranks
    for i, r in enumerate(scored):
        r["rank"] = i + 1
    
    return scored
