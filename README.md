# 🧠 TalentGPT — AI Recruiter Intelligence Platform

> **"AI that understands talent, not keywords."**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![Next.js 14](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org)

---

## 🎯 What is TalentGPT?

TalentGPT is an **enterprise-grade AI Talent Intelligence Platform** that goes beyond traditional keyword-based ATS systems. It thinks like an elite human recruiter — understanding context, inferring skills, predicting success, and explaining every decision.

### The Problem
Recruiters spend 80% of their time screening resumes manually. Traditional ATS misses top candidates because they don't match exact keywords. Bias creeps in. Great talent goes undiscovered.

### Our Solution
A multi-agent AI system that:
1. **Deeply understands** job descriptions (extracts hidden requirements, infers seniority, maps skills)
2. **Profiles candidates** holistically (career trajectory, learning velocity, leadership signals)
3. **Scores across 6 dimensions** using independent AI agents
4. **Explains every decision** with recruiter-friendly summaries
5. **Predicts hiring success** before the first interview
6. **Learns from feedback** to get smarter with every hire

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     TalentGPT Platform                      │
├─────────────────┬───────────────────┬───────────────────────┤
│   Next.js 14    │    FastAPI         │   AI Engine           │
│   React/TS      │    Python 3.11     │   Multi-Agent System  │
│   TailwindCSS   │    PostgreSQL      │   Vector Embeddings   │
│   ShadCN UI     │    Redis Cache     │   LLM (Claude API)    │
│   Recharts      │    Celery Queue    │   Semantic Search     │
└─────────────────┴───────────────────┴───────────────────────┘
```

---

## 🤖 AI Modules

| Module | Description |
|--------|-------------|
| **JD Intelligence Engine** | Extracts required/preferred/hidden skills, generates role embeddings |
| **Candidate Intelligence Engine** | Builds 360° candidate capability vectors |
| **Skill Match Agent** | Semantic + exact skill matching (0-100) |
| **Experience Agent** | Career trajectory & domain relevance (0-100) |
| **Behavior Agent** | Platform activity & consistency signals (0-100) |
| **Learning Agent** | Upskilling velocity & certifications (0-100) |
| **Leadership Agent** | Team management & ownership indicators (0-100) |
| **Culture Fit Agent** | Communication & collaboration style (0-100) |
| **Committee Ranking Engine** | Weighted multi-agent score aggregation |
| **Explainable AI Layer** | Per-candidate decision explanations |
| **Success Predictor** | Interview/offer/retention probability |
| **Recruiter CoPilot** | Conversational AI assistant |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 15
- Redis 7

### 1. Clone Repository
```bash
git clone https://github.com/yourname/talentgpt.git
cd talentgpt
```

### 2. Environment Setup
```bash
cp .env.example .env
# Add your API keys (Anthropic, OpenAI optional)
```

### 3. Run with Docker
```bash
docker-compose up -d
```

### 4. Access
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Admin**: http://localhost:3000/admin

---

## 📊 Scoring Methodology

```
Final Fit Score = 
  Skills Match    × 35% +
  Experience      × 25% +
  Learning        × 15% +
  Leadership      × 10% +
  Behavior        × 10% +
  Culture Fit     ×  5%
```

---

## 🗂️ Repository Structure

```
talentgpt/
├── backend/                    # FastAPI Python backend
│   ├── app/
│   │   ├── api/v1/endpoints/   # REST API routes
│   │   ├── core/               # Config, security, database
│   │   ├── models/             # SQLAlchemy ORM models
│   │   ├── schemas/            # Pydantic schemas
│   │   ├── services/
│   │   │   ├── agents/         # 6 AI scoring agents
│   │   │   ├── ai/             # LLM, embeddings, RAG
│   │   │   └── ml/             # Prediction models
│   │   └── utils/              # Helpers
│   └── tests/
├── frontend/                   # Next.js 14 frontend
│   └── src/
│       ├── components/         # React components
│       ├── pages/              # Next.js pages
│       └── lib/                # API client, utils
├── infrastructure/             # Docker, Nginx, scripts
├── data/                       # Sample datasets
└── docs/                       # Architecture docs
```

---

## 🏆 Hackathon Differentiators

1. **Multi-Agent Architecture** — 6 specialized AI agents, not one monolithic scorer
2. **Explainable AI** — Every ranking has a human-readable reason
3. **Success Prediction** — ML models predicting interview/retention probability  
4. **Semantic Understanding** — Vector embeddings, not keyword matching
5. **Recruiter CoPilot** — Natural language queries via LLM
6. **Feedback Learning** — System improves with every recruiter action
7. **Candidate Clustering** — Discovery of similar talent pools
8. **Production-Ready** — Docker, CI/CD, monitoring, auth — all included

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

*Built with ❤️ for the AI Hiring Hackathon*
