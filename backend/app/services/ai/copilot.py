"""
TalentGPT - Recruiter CoPilot Chatbot
Conversational AI assistant for recruiters.
Understands natural language queries about candidates, jobs, and hiring intelligence.
"""

import json
from typing import Dict, List, Optional
from anthropic import AsyncAnthropic

from app.core.config import settings

client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """You are TalentGPT CoPilot — an elite AI Recruiter Assistant.

You help recruiters find, understand, and make decisions about candidates.

You have access to:
- A ranked list of candidates for the current job
- Detailed candidate profiles with scores
- Job description intelligence
- Hiring predictions

PERSONALITY:
- Expert, confident, and concise
- Data-driven but human-centered
- Always explain WHY, not just WHAT
- Use specific numbers and scores when available

CAPABILITIES:
1. Answer questions about specific candidates
2. Filter candidates by skills, scores, experience
3. Compare candidates side-by-side
4. Explain ranking decisions
5. Identify candidates with specific traits
6. Predict hiring outcomes
7. Suggest interview questions for top candidates
8. Flag risks and concerns

RESPONSE FORMAT:
- Be conversational but structured
- Use bullet points for lists
- Bold key names and scores
- Always end with a helpful follow-up suggestion

CONTEXT DATA will be provided in the user message. Use it accurately.
Never hallucinate candidate names or scores not in the data."""


class RecruiterCoPilot:
    
    async def chat(
        self,
        user_message: str,
        conversation_history: List[Dict],
        context: Dict,
    ) -> Dict:
        """
        Process a recruiter message and return intelligent response.
        
        context: {
            "job": {job profile},
            "ranked_candidates": [{candidate + scores}],
            "total_candidates": int,
        }
        """
        
        # Build context string
        context_str = self._build_context_string(context)
        
        # Prepare messages
        messages = []
        
        # Add context as first message
        if conversation_history:
            messages = conversation_history[-10:]  # Last 10 turns
        else:
            # First message: inject context
            messages = [{
                "role": "user",
                "content": f"[CONTEXT]\n{context_str}\n\n[RECRUITER QUESTION]\n{user_message}"
            }]
        
        if conversation_history:
            messages.append({
                "role": "user", 
                "content": f"[CONTEXT UPDATE]\n{context_str}\n\n{user_message}"
            })
        
        response = await client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1500,
            system=SYSTEM_PROMPT,
            messages=messages,
        )
        
        assistant_reply = response.content[0].text
        
        # Update conversation history
        new_history = list(conversation_history)
        new_history.append({"role": "user", "content": user_message})
        new_history.append({"role": "assistant", "content": assistant_reply})
        
        # Extract any candidate IDs mentioned (for UI highlighting)
        mentioned_candidates = self._extract_mentioned_candidates(
            assistant_reply, context.get("ranked_candidates", [])
        )
        
        return {
            "reply": assistant_reply,
            "conversation_history": new_history[-20:],  # Keep last 20
            "mentioned_candidates": mentioned_candidates,
            "suggested_actions": self._suggest_actions(user_message, assistant_reply),
        }

    def _build_context_string(self, context: Dict) -> str:
        """Build a concise context string from platform data."""
        
        job = context.get("job", {})
        candidates = context.get("ranked_candidates", [])
        
        job_str = f"""
JOB: {job.get('title', 'Unknown')} at {job.get('company', 'Unknown')}
REQUIRED SKILLS: {', '.join(job.get('required_skills', [])[:8])}
EXPERIENCE: {job.get('experience_min_years', 0)}-{job.get('experience_max_years', 10)} years
SENIORITY: {job.get('seniority_level', 'mid')}
"""
        
        candidates_str = "TOP CANDIDATES:\n"
        for c in candidates[:15]:  # Top 15 in context
            cand = c.get("candidate", {})
            scores = c.get("scores", {})
            candidates_str += f"""
#{c.get('rank', '?')} {cand.get('name', 'Unknown')} (ID: {cand.get('id', '')[:8]})
  Fit Score: {scores.get('final_fit_score', 0):.0f}/100
  Skills: {scores.get('skill_match_score', 0):.0f} | Exp: {scores.get('experience_score', 0):.0f} | Learning: {scores.get('learning_score', 0):.0f} | Leadership: {scores.get('leadership_score', 0):.0f}
  Summary: {scores.get('recruiter_summary', '')[:150]}
  Top Skills: {', '.join(cand.get('technical_skills', [])[:5]) if isinstance(cand.get('technical_skills'), list) else ''}
"""
        
        return job_str + "\n" + candidates_str

    def _extract_mentioned_candidates(self, reply: str, candidates: List[Dict]) -> List[str]:
        """Find which candidates were mentioned in the reply."""
        mentioned = []
        for c in candidates:
            name = c.get("candidate", {}).get("name", "")
            if name and name.lower() in reply.lower():
                mentioned.append(c.get("candidate", {}).get("id", ""))
        return mentioned

    def _suggest_actions(self, user_message: str, reply: str) -> List[str]:
        """Suggest next actions based on conversation context."""
        suggestions = []
        
        msg_lower = user_message.lower()
        
        if "shortlist" in msg_lower or "top" in msg_lower:
            suggestions.append("Compare top candidates side-by-side")
            suggestions.append("Generate interview questions for shortlisted candidates")
        
        if "skill" in msg_lower or "python" in msg_lower or "experience" in msg_lower:
            suggestions.append("Show all candidates with this skill")
            suggestions.append("Find similar skills in other candidates")
        
        if "leader" in msg_lower or "manage" in msg_lower:
            suggestions.append("Filter by leadership score > 70")
        
        if "risk" in msg_lower or "concern" in msg_lower:
            suggestions.append("Show full risk analysis for this candidate")
        
        if not suggestions:
            suggestions = [
                "Who are your top 3 candidates?",
                "Show me candidates with Python + ML skills",
                "Which candidate is most likely to stay long-term?",
            ]
        
        return suggestions[:3]


async def generate_interview_questions(
    job_profile: Dict,
    candidate_profile: Dict,
    num_questions: int = 5
) -> List[Dict]:
    """Generate targeted interview questions based on job + candidate profile."""
    
    prompt = f"""
Generate {num_questions} highly targeted interview questions for this candidate and role.

JOB: {job_profile.get('title', '')}
REQUIRED SKILLS: {', '.join(job_profile.get('required_skills', [])[:6])}
CANDIDATE: {candidate_profile.get('name', '')}
CANDIDATE SKILLS: {json.dumps(candidate_profile.get('technical_skills', [])[:8])}
CANDIDATE EXPERIENCE: {candidate_profile.get('total_experience_years', 0)} years
GAPS/RISKS: {json.dumps(candidate_profile.get('missing_skills', []))}

Generate a mix of:
- Technical deep-dive questions (to verify skill depth)
- Behavioral questions (STAR format triggers)
- Gap-probing questions (address risks)
- Culture/values questions

Return ONLY valid JSON:
{{
  "questions": [
    {{
      "type": "technical",
      "question": "Walk me through how you'd design a real-time ML serving pipeline handling 10K req/sec.",
      "what_to_look_for": "Mentions caching, model versioning, A/B testing, monitoring",
      "follow_up": "How would you handle model drift?"
    }}
  ]
}}
"""
    
    response = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        system="You are an expert technical interviewer. Generate targeted interview questions. Return only valid JSON.",
        messages=[{"role": "user", "content": prompt}]
    )
    
    try:
        data = json.loads(response.content[0].text)
        return data.get("questions", [])
    except:
        return []
