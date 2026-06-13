"""
TalentGPT — Redrob AI Challenge Ranker
=======================================
Reads candidates.jsonl, scores every candidate against the JD,
and writes a submission.csv in the required format:
    candidate_id, rank, score, reasoning

Run:
    python rank.py --candidates candidates.jsonl --out submission.csv

No network calls during ranking. No GPU needed.
Runs in ~2-5 min for 50K candidates on CPU.
"""

import json
import csv
import argparse
import math
from pathlib import Path
from datetime import datetime, date

# ─── JOB DESCRIPTION CONTEXT ──────────────────────────────────────────────────
# Redrob wants to rank candidates for AI/ML engineering roles.
# Scoring targets depth of AI skills + engagement signals.

AI_CORE_SKILLS = {
    "machine learning", "deep learning", "nlp", "llm", "llms",
    "large language models", "transformers", "fine-tuning llms",
    "fine tuning", "pytorch", "tensorflow", "keras",
    "hugging face transformers", "sentence transformers",
    "embeddings", "vector search", "faiss", "pinecone", "weaviate",
    "milvus", "qdrant", "opensearch", "elasticsearch",
    "langchain", "llamaindex", "rag", "reinforcement learning",
    "rlhf", "peft", "lora", "computer vision", "image classification",
    "object detection", "yolo", "opencv", "cnn", "gans",
    "recommendation systems", "information retrieval",
    "mlops", "mlflow", "weights & biases",
    "scikit-learn", "xgboost", "lightgbm",
    "feature engineering", "data science", "speech recognition",
    "tts", "prompt engineering", "bm25", "kubeflow", "bentoml",
    "haystack", "forecasting", "statistical modeling",
    "python", "spark", "kafka", "airflow", "sql",
    "aws", "gcp", "azure", "docker", "kubernetes",
    "data pipelines", "etl", "databricks", "bigquery", "snowflake",
    "fastapi", "flask", "django", "postgresql", "redis",
    "apache beam", "apache flink", "dbt",
}

AI_TIER1_SKILLS = {
    "machine learning", "deep learning", "nlp", "llm", "llms",
    "transformers", "fine-tuning llms", "pytorch", "tensorflow",
    "hugging face transformers", "sentence transformers", "embeddings",
    "vector search", "faiss", "pinecone", "langchain", "llamaindex",
    "reinforcement learning", "rlhf", "peft", "computer vision",
    "object detection", "yolo", "recommendation systems",
    "information retrieval", "mlops", "mlflow", "weights & biases",
    "scikit-learn", "xgboost", "lightgbm", "feature engineering",
    "data science", "prompt engineering", "bm25", "gans", "cnn",
    "image classification", "speech recognition", "forecasting",
}

EDUCATION_TIER_SCORE = {
    "tier_1": 1.0, "tier_2": 0.85, "tier_3": 0.70,
    "tier_4": 0.55, "unknown": 0.60,
}

PROFICIENCY_WEIGHT = {
    "expert": 1.0, "advanced": 0.85,
    "intermediate": 0.65, "beginner": 0.40,
}


def score_skills(candidate):
    skills = candidate.get("skills", [])
    ai_skill_count = 0
    weighted_score = 0.0
    matched_skills = []

    for skill in skills:
        name = skill.get("name", "").lower().strip()
        proficiency = skill.get("proficiency", "beginner")
        endorsements = skill.get("endorsements", 0)
        duration_months = skill.get("duration_months", 0)

        if name in AI_CORE_SKILLS:
            ai_skill_count += 1
            prof_w = PROFICIENCY_WEIGHT.get(proficiency, 0.4)
            end_mult = min(1.2, 0.8 + (endorsements / 100) * 0.4)
            dur_mult = min(1.15, 1.0 + (duration_months / 60) * 0.15)
            skill_score = prof_w * end_mult * dur_mult
            if name in AI_TIER1_SKILLS:
                skill_score *= 1.3
            weighted_score += skill_score
            matched_skills.append(name)

    assessment_scores = candidate.get("redrob_signals", {}).get("skill_assessment_scores", {})
    assessment_bonus = sum(
        (s / 100) * 10 for sk, s in assessment_scores.items()
        if sk.lower() in AI_CORE_SKILLS
    )

    normalized = min(100, (weighted_score / 27) * 100 + assessment_bonus)
    return normalized, ai_skill_count, matched_skills


def score_experience(candidate):
    profile = candidate.get("profile", {})
    career = candidate.get("career_history", [])
    years = profile.get("years_of_experience", 0)

    if years < 1:
        years_score = 20
    elif years < 3:
        years_score = 40 + years * 10
    elif years < 5:
        years_score = 60 + (years - 3) * 8
    elif years < 8:
        years_score = 76 + (years - 5) * 6
    elif years < 12:
        years_score = 94 - (years - 8) * 1.5
    else:
        years_score = max(60, 94 - (years - 8) * 2)

    tenure_bonus = 0
    if career:
        avg_tenure = sum(r.get("duration_months", 0) for r in career) / len(career)
        if avg_tenure >= 24:
            tenure_bonus = 5
        elif avg_tenure >= 18:
            tenure_bonus = 3
        elif avg_tenure < 12:
            tenure_bonus = -5

    tech_industries = {"software", "ai/ml", "fintech", "food delivery",
                       "transportation", "e-commerce", "saas"}
    tech_count = sum(1 for r in career if r.get("industry", "").lower() in tech_industries)
    tech_bonus = min(8, tech_count * 3)

    current = career[0] if career else {}
    progression_bonus = 4 if current.get("industry", "").lower() in tech_industries else 0

    return min(100, max(0, years_score + tenure_bonus + tech_bonus + progression_bonus))


def score_education(candidate):
    education = candidate.get("education", [])
    if not education:
        return 40.0

    cs_fields = {
        "computer science", "artificial intelligence", "machine learning",
        "data science", "information technology", "computer engineering",
        "electronics", "mathematics", "statistics", "software engineering",
    }

    best = 0.0
    for edu in education:
        tier_score = EDUCATION_TIER_SCORE.get(edu.get("tier", "unknown"), 0.60) * 60
        field = edu.get("field_of_study", "").lower()
        field_bonus = 20 if any(f in field for f in cs_fields) else 5
        degree = edu.get("degree", "").lower()
        if any(d in degree for d in ["ph.d", "phd", "m.tech", "m.e.", "m.s.", "m.sc"]):
            degree_bonus = 15
        elif any(d in degree for d in ["b.tech", "b.e.", "b.sc"]):
            degree_bonus = 10
        else:
            degree_bonus = 5
        best = max(best, tier_score + field_bonus + degree_bonus)

    return min(100, best)


def score_behavior(candidate):
    signals = candidate.get("redrob_signals", {})

    completeness = signals.get("profile_completeness_score", 0)
    completeness_score = completeness * 0.30

    rr = signals.get("recruiter_response_rate", 0)
    response_score = rr * 35

    last_active_str = signals.get("last_active_date", "2020-01-01")
    try:
        last_active = datetime.strptime(last_active_str, "%Y-%m-%d").date()
        days_inactive = (date(2026, 6, 13) - last_active).days
        recency_score = 15 if days_inactive <= 30 else 10 if days_inactive <= 90 else 5 if days_inactive <= 180 else 0
    except:
        recency_score = 5

    icr = signals.get("interview_completion_rate", 0)
    interview_score = icr * 10

    github = signals.get("github_activity_score", -1)
    github_score = min(8, github * 0.08) if github > 0 else 0

    verified = (int(signals.get("verified_email", False)) +
                int(signals.get("verified_phone", False)) +
                int(signals.get("linkedin_connected", False)))
    verify_score = verified * 0.7

    otw_score = 3 if signals.get("open_to_work_flag", False) else 0

    total = (completeness_score + response_score + recency_score +
             interview_score + github_score + verify_score + otw_score)
    return min(100, total)


def score_certifications(candidate):
    certs = candidate.get("certifications", [])
    if not certs:
        return 30.0

    ai_cert_keywords = ["machine learning", "tensorflow", "pytorch", "deep learning",
                        "ai engineer", "hugging face"]
    score = 30.0
    for cert in certs:
        name = cert.get("name", "").lower()
        year = cert.get("year", 2000)
        recency = min(1.0, (year - 2018) / 6) if year >= 2018 else 0
        if any(kw in name for kw in ai_cert_keywords):
            score += 20 * (0.5 + 0.5 * recency)
        elif any(kw in name for kw in ["aws", "gcp", "azure", "cloud"]):
            score += 10 * (0.5 + 0.5 * recency)
        else:
            score += 5 * (0.5 + 0.5 * recency)
    return min(100, score)


def compute_final_score(candidate):
    skill_score, ai_skill_count, matched_skills = score_skills(candidate)
    behavior_score = score_behavior(candidate)
    experience_score = score_experience(candidate)
    education_score = score_education(candidate)
    cert_score = score_certifications(candidate)

    final = (
        skill_score      * 0.38 +
        behavior_score   * 0.28 +
        experience_score * 0.18 +
        education_score  * 0.10 +
        cert_score       * 0.06
    )

    final_normalized = round(min(1.0, final / 100), 4)

    profile = candidate.get("profile", {})
    signals = candidate.get("redrob_signals", {})
    title = profile.get("current_title", "Professional")
    years = profile.get("years_of_experience", 0)
    rr = signals.get("recruiter_response_rate", 0)

    reasoning = (
        f"{title} with {years:.1f} yrs; "
        f"{ai_skill_count} AI core skills; "
        f"response rate {rr:.2f}."
    )

    return final_normalized, reasoning


def rank_candidates(input_path, output_path):
    print("🚀 TalentGPT Ranking Engine")
    print(f"📂 Input:  {input_path}")
    print(f"📝 Output: {output_path}")
    print("=" * 50)

    print("📖 Loading candidates...")
    candidates = []
    with open(input_path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            try:
                candidates.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"  ⚠ Skipping line {i+1}: {e}")

    print(f"✅ Loaded {len(candidates):,} candidates")
    print("🤖 Running 5-agent scoring pipeline...")

    results = []
    for i, candidate in enumerate(candidates):
        if i % 5000 == 0 and i > 0:
            print(f"  ... {i:,}/{len(candidates):,} scored")
        candidate_id = candidate.get("candidate_id", f"UNKNOWN_{i}")
        try:
            score, reasoning = compute_final_score(candidate)
            results.append({"candidate_id": candidate_id, "score": score, "reasoning": reasoning})
        except Exception as e:
            print(f"  ⚠ Error on {candidate_id}: {e}")
            results.append({"candidate_id": candidate_id, "score": 0.0, "reasoning": "Scoring error."})

    results.sort(key=lambda x: x["score"], reverse=True)
    for i, r in enumerate(results):
        r["rank"] = i + 1

    print("💾 Writing submission CSV...")
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["candidate_id", "rank", "score", "reasoning"])
        writer.writeheader()
        for r in results:
            writer.writerow({
                "candidate_id": r["candidate_id"],
                "rank": r["rank"],
                "score": r["score"],
                "reasoning": r["reasoning"],
            })

    scores = [r["score"] for r in results]
    print("\n" + "=" * 50)
    print("📊 RANKING SUMMARY")
    print("=" * 50)
    print(f"Total ranked:  {len(results):,}")
    print(f"Top score:     {max(scores):.4f}")
    print(f"Median score:  {sorted(scores)[len(scores)//2]:.4f}")
    print(f"Bottom score:  {min(scores):.4f}")
    print("\n🏆 TOP 10:")
    for r in results[:10]:
        print(f"  #{r['rank']:3}  {r['candidate_id']}  {r['score']:.4f}  {r['reasoning']}")
    print(f"\n✅ Done! Saved to: {output_path}")
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TalentGPT Redrob Challenge Ranker")
    parser.add_argument("--candidates", default="candidates.jsonl")
    parser.add_argument("--out", default="submission.csv")
    args = parser.parse_args()

    if not Path(args.candidates).exists():
        print(f"❌ File not found: {args.candidates}")
        exit(1)

    rank_candidates(args.candidates, args.out)
