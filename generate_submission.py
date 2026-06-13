"""
TalentGPT - Hackathon Submission Generator
Generates the ranked output file in required format.

Usage: python generate_submission.py --job-id <id> --output ranked_output.csv
"""

import asyncio
import json
import csv
import sys
from pathlib import Path
from datetime import datetime

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.services.agents.scoring_engine import rank_candidates_for_job
from app.services.ai.intelligence_engine import JDIntelligenceEngine, CandidateIntelligenceEngine

# ─── SAMPLE JD (replace with actual dataset) ─────────────────────────────────

SAMPLE_JD = """
Senior Machine Learning Engineer

Requirements:
- 5+ years ML experience
- Python, PyTorch, TensorFlow
- NLP and LLM experience  
- Production ML systems
- AWS/GCP cloud

Preferred:
- Fine-tuning LLMs
- LangChain, LlamaIndex
- Vector databases
- Team leadership
"""

# ─── SAMPLE CANDIDATES (replace with actual dataset) ─────────────────────────

SAMPLE_CANDIDATES = [
    {
        "id": "c001",
        "name": "Arjun Sharma",
        "headline": "Senior ML Engineer | NLP & LLMs | Ex-Google Brain",
        "technical_skills": [
            {"skill": "Python", "proficiency": 95},
            {"skill": "PyTorch", "proficiency": 90},
            {"skill": "NLP", "proficiency": 92},
            {"skill": "LLMs", "proficiency": 88},
            {"skill": "AWS", "proficiency": 85},
            {"skill": "LangChain", "proficiency": 80},
        ],
        "total_experience_years": 7,
        "domain_expertise": ["Machine Learning", "NLP", "MLOps"],
        "certifications": [{"name": "AWS ML Specialty"}, {"name": "GCP ML Engineer"}],
        "employment_history": [
            {"company": "MindTree", "role": "Staff ML Engineer", "duration_years": 2.5,
             "impact": "Led 8-person NLP team, reduced latency 60%"},
        ],
        "learning_velocity": 90,
        "leadership_score": 78,
        "collaboration_score": 85,
        "communication_score": 82,
        "platform_activity_score": 88,
        "consistency_score": 82,
        "reliability_score": 88,
        "career_progression_score": 85,
    },
    # Add more candidates from actual dataset
]


async def generate_submission(output_file: str = "ranked_output.csv"):
    """Main submission generation pipeline."""
    
    print("🚀 TalentGPT Submission Generator")
    print("=" * 50)
    
    # Step 1: Analyze JD
    print("\n📋 Step 1: Analyzing Job Description...")
    jd_engine = JDIntelligenceEngine()
    job_profile = await jd_engine.analyze(SAMPLE_JD, title="Senior ML Engineer")
    print(f"✅ Extracted {len(job_profile.get('required_skills', []))} required skills")
    print(f"✅ Identified seniority: {job_profile.get('seniority_level', 'unknown')}")
    
    # Step 2: Analyze Candidates
    print(f"\n👥 Step 2: Analyzing {len(SAMPLE_CANDIDATES)} candidates...")
    cand_engine = CandidateIntelligenceEngine()
    enriched_candidates = []
    
    for i, cand in enumerate(SAMPLE_CANDIDATES):
        print(f"   [{i+1}/{len(SAMPLE_CANDIDATES)}] Processing: {cand['name']}...")
        # In real scenario, analyze raw resume text
        # profile = await cand_engine.analyze(resume_text=cand.get('raw_resume', ''), profile_data=cand)
        # For demo, use existing profile data
        enriched_candidates.append(cand)
    
    print(f"✅ All candidates profiled")
    
    # Step 3: Multi-Agent Ranking
    print(f"\n🤖 Step 3: Running 6-Agent Scoring Engine...")
    print("   Agents: SkillMatch | Experience | Behavior | Learning | Leadership | CultureFit")
    
    ranked = await rank_candidates_for_job(job_profile, enriched_candidates, max_concurrent=3)
    
    print(f"✅ Ranked {len(ranked)} candidates")
    
    # Step 4: Generate Output Files
    print(f"\n📊 Step 4: Generating submission files...")
    
    # CSV Output (hackathon format)
    csv_rows = []
    for r in ranked:
        d = r.get("decision")
        c = next((c for c in enriched_candidates if c["id"] == r["candidate_id"]), {})
        
        row = {
            "rank": r["rank"],
            "candidate_id": r["candidate_id"],
            "candidate_name": r["candidate_name"],
            "final_fit_score": d.final_fit_score if d else 0,
            "skill_match_score": d.skill_match_score if d else 0,
            "experience_score": d.experience_score if d else 0,
            "learning_score": d.learning_score if d else 0,
            "leadership_score": d.leadership_score if d else 0,
            "behavior_score": d.behavior_score if d else 0,
            "culture_fit_score": d.culture_fit_score if d else 0,
            "interview_success_probability": d.interview_success_probability if d else 0,
            "retention_probability": d.retention_probability if d else 0,
            "growth_potential": d.growth_potential if d else "Unknown",
            "top_strengths": " | ".join(d.strengths[:2]) if d and d.strengths else "",
            "key_risks": " | ".join(d.risks[:1]) if d and d.risks else "",
            "recruiter_summary": d.recruiter_summary if d else "",
        }
        csv_rows.append(row)
    
    # Write CSV
    if csv_rows:
        fieldnames = list(csv_rows[0].keys())
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(csv_rows)
    
    # JSON output (detailed)
    json_output = {
        "generated_at": datetime.now().isoformat(),
        "system": "TalentGPT v1.0",
        "job_profile": job_profile,
        "total_candidates": len(ranked),
        "scoring_weights": {
            "skills": "35%", "experience": "25%", "learning": "15%",
            "leadership": "10%", "behavior": "10%", "culture_fit": "5%"
        },
        "top_10": [
            {
                "rank": r["rank"],
                "candidate_id": r["candidate_id"],
                "candidate_name": r["candidate_name"],
                "final_fit_score": r["decision"].final_fit_score if r["decision"] else 0,
                "agent_scores": {
                    "skill_match": r["decision"].skill_match_score if r["decision"] else 0,
                    "experience": r["decision"].experience_score if r["decision"] else 0,
                    "learning": r["decision"].learning_score if r["decision"] else 0,
                    "leadership": r["decision"].leadership_score if r["decision"] else 0,
                    "behavior": r["decision"].behavior_score if r["decision"] else 0,
                    "culture_fit": r["decision"].culture_fit_score if r["decision"] else 0,
                },
                "predictions": {
                    "interview_success": r["decision"].interview_success_probability if r["decision"] else 0,
                    "retention": r["decision"].retention_probability if r["decision"] else 0,
                },
                "explanation": {
                    "strengths": r["decision"].strengths if r["decision"] else [],
                    "risks": r["decision"].risks if r["decision"] else [],
                    "summary": r["decision"].recruiter_summary if r["decision"] else "",
                }
            }
            for r in ranked[:10]
        ]
    }
    
    json_file = output_file.replace('.csv', '_detailed.json')
    with open(json_file, 'w') as f:
        json.dump(json_output, f, indent=2)
    
    print(f"✅ CSV output: {output_file}")
    print(f"✅ JSON output: {json_file}")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 RANKING SUMMARY")
    print("=" * 50)
    for r in ranked[:5]:
        d = r.get("decision")
        score = d.final_fit_score if d else 0
        label = "🔥 STRONG" if score >= 85 else "✅ GOOD" if score >= 70 else "⚡ PARTIAL"
        print(f"#{r['rank']:2} {label} | {r['candidate_name']:<25} | Score: {score:.1f}/100")
    
    print(f"\n✨ Submission ready! Generated by TalentGPT Multi-Agent AI System")
    return ranked


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="TalentGPT Submission Generator")
    parser.add_argument("--output", default="ranked_output.csv", help="Output CSV file path")
    args = parser.parse_args()
    
    asyncio.run(generate_submission(args.output))
