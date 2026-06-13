import { useState, useRef, useEffect } from "react";

// ─── SAMPLE DATA ─────────────────────────────────────────────────────────────

const SAMPLE_JD = `Senior Machine Learning Engineer - AI Products Team

We are building next-generation AI-powered products and looking for an exceptional ML Engineer to join our core team.

Requirements:
- 5+ years of experience in machine learning and deep learning
- Strong Python programming skills (PyTorch, TensorFlow)
- Experience with NLP, LLMs, and transformer architectures
- Production ML systems: model serving, MLOps, monitoring
- Experience with vector databases (FAISS, Pinecone, Weaviate)
- Strong SQL and data pipeline skills
- Experience with AWS/GCP cloud infrastructure

Nice to have:
- Publications or open source contributions in ML/NLP
- Experience with LangChain, LlamaIndex
- Knowledge of RLHF, fine-tuning large models
- Team leadership or mentoring experience

You'll be working on: building RAG systems, LLM applications, recommendation engines, and real-time ML pipelines.`;

const SAMPLE_CANDIDATES = [
  {
    id: "c001",
    name: "Arjun Sharma",
    headline: "Senior ML Engineer | NLP & LLMs | Ex-Google Brain",
    location: "Bangalore, India",
    experience_years: 7,
    skills: ["Python", "PyTorch", "TensorFlow", "NLP", "LLMs", "FAISS", "AWS", "MLflow", "LangChain", "Kubernetes"],
    education: "M.Tech AI/ML - IIT Delhi (2017)",
    certifications: ["AWS ML Specialty", "GCP Professional ML Engineer"],
    recent_role: "Staff ML Engineer at MindTree (2.5 years)",
    achievements: ["Led 8-person team building production NLP pipeline", "Reduced model latency 60%", "3 ML papers published"],
    platform_activity: 88,
    career_trajectory: "ascending",
  },
  {
    id: "c002",
    name: "Priya Nair",
    headline: "ML Engineer | Computer Vision & NLP | Building AI at Scale",
    location: "Hyderabad, India",
    experience_years: 5,
    skills: ["Python", "PyTorch", "NLP", "Transformers", "Docker", "AWS", "FastAPI", "LangChain", "FAISS"],
    education: "B.Tech CS - NIT Trichy (2019)",
    certifications: ["Deep Learning Specialization (Coursera)", "AWS Developer"],
    recent_role: "ML Engineer at Ola (3 years)",
    achievements: ["Built real-time fraud detection system (99.2% accuracy)", "Led migration to transformer-based NLP", "Open source contributor"],
    platform_activity: 92,
    career_trajectory: "ascending",
  },
  {
    id: "c003",
    name: "Rahul Verma",
    headline: "Data Scientist | Python | ML | Analytics",
    location: "Pune, India",
    experience_years: 4,
    skills: ["Python", "Sklearn", "SQL", "Tableau", "Pandas", "Random Forest", "XGBoost"],
    education: "B.Sc Statistics - Pune University (2020)",
    certifications: ["IBM Data Science Professional"],
    recent_role: "Data Scientist at Wipro (2 years)",
    achievements: ["Built churn prediction model", "Improved reporting automation by 40%"],
    platform_activity: 65,
    career_trajectory: "lateral",
  },
  {
    id: "c004",
    name: "Sneha Patel",
    headline: "AI Research Engineer | Generative AI | LLMs Fine-tuning | MLOps",
    location: "Mumbai, India",
    experience_years: 6,
    skills: ["Python", "PyTorch", "LLMs", "RLHF", "Fine-tuning", "LangChain", "LlamaIndex", "Pinecone", "AWS", "Kubernetes", "MLflow"],
    education: "M.Tech CS - IIT Bombay (2018)",
    certifications: ["AWS Solutions Architect", "Hugging Face Expert"],
    recent_role: "Senior AI Engineer at Jio AI Cloud (3.5 years)",
    achievements: ["Fine-tuned LLaMA 2 for domain-specific tasks", "Built enterprise RAG system", "Mentored 5 junior engineers", "2 patents filed"],
    platform_activity: 95,
    career_trajectory: "ascending",
  },
  {
    id: "c005",
    name: "Karthik Reddy",
    headline: "Backend Engineer | Python | Microservices",
    location: "Chennai, India",
    experience_years: 5,
    skills: ["Python", "Django", "FastAPI", "PostgreSQL", "Redis", "Docker", "AWS", "REST APIs"],
    education: "B.Tech CS - VIT (2019)",
    certifications: ["AWS Developer Associate"],
    recent_role: "Senior Backend Engineer at Zoho (2 years)",
    achievements: ["Built payment processing microservice handling 1M txns/day", "Led API redesign project"],
    platform_activity: 72,
    career_trajectory: "lateral",
  },
  {
    id: "c006",
    name: "Meera Krishnan",
    headline: "Junior Data Analyst | SQL | Power BI",
    location: "Kochi, India",
    experience_years: 1.5,
    skills: ["SQL", "Python basics", "Power BI", "Excel", "Tableau"],
    education: "BCA - MG University (2022)",
    certifications: ["Google Data Analytics Certificate"],
    recent_role: "Data Analyst at TCS (1.5 years)",
    achievements: ["Created automated reporting dashboards"],
    platform_activity: 55,
    career_trajectory: "ascending",
  },
];

// ─── SCORING LOGIC ───────────────────────────────────────────────────────────

function scoreCandidate(candidate, jdSkills) {
  const required = ["Python", "PyTorch", "NLP", "LLMs", "AWS", "FAISS", "MLOps"];
  const preferred = ["LangChain", "LlamaIndex", "RLHF", "Fine-tuning", "Kubernetes"];

  const cSkills = candidate.skills.map(s => s.toLowerCase());
  
  // Skill agent
  const reqMatched = required.filter(s => cSkills.includes(s.toLowerCase())).length;
  const prefMatched = preferred.filter(s => cSkills.includes(s.toLowerCase())).length;
  const skillScore = Math.min(100, (reqMatched / required.length) * 70 + (prefMatched / preferred.length) * 30);
  
  // Experience agent
  const yearsScore = Math.min(100, candidate.experience_years >= 5 
    ? 85 + Math.min(15, (candidate.experience_years - 5) * 3)
    : candidate.experience_years * 17);
  
  // Learning agent
  const certCount = candidate.certifications.length;
  const hasAdvCert = candidate.certifications.some(c => c.includes("ML") || c.includes("AI") || c.includes("Deep"));
  const learningScore = Math.min(100, 40 + certCount * 15 + (hasAdvCert ? 25 : 0));
  
  // Leadership agent
  const hasLead = candidate.achievements.some(a => a.toLowerCase().includes("led") || a.toLowerCase().includes("managed") || a.toLowerCase().includes("mentor"));
  const hasPubs = candidate.achievements.some(a => a.toLowerCase().includes("paper") || a.toLowerCase().includes("patent"));
  const leadershipScore = Math.min(100, 30 + (hasLead ? 40 : 0) + (hasPubs ? 20 : 0) + (candidate.experience_years > 5 ? 10 : 0));
  
  // Behavior agent
  const behaviorScore = Math.min(100, candidate.platform_activity * 0.6 + 
    (candidate.career_trajectory === "ascending" ? 30 : candidate.career_trajectory === "lateral" ? 15 : 5));
  
  // Culture agent
  const cultureScore = Math.min(100, 55 + (candidate.experience_years >= 4 ? 20 : 0) + (candidate.achievements.length >= 3 ? 15 : 0) + 10);
  
  const final = 
    skillScore * 0.35 +
    yearsScore * 0.25 +
    learningScore * 0.15 +
    leadershipScore * 0.10 +
    behaviorScore * 0.10 +
    cultureScore * 0.05;
  
  return {
    final: Math.round(final * 10) / 10,
    skill: Math.round(skillScore),
    experience: Math.round(yearsScore),
    learning: Math.round(learningScore),
    leadership: Math.round(leadershipScore),
    behavior: Math.round(behaviorScore),
    culture: Math.round(cultureScore),
    interview_prob: Math.min(0.97, final / 100 * 0.95 + 0.05),
    retention_prob: Math.min(0.97, (final / 100) * 0.8 + learningScore / 100 * 0.2),
  };
}

function getStrengths(candidate, scores) {
  const s = [];
  if (scores.skill >= 80) s.push(`Strong skill match — ${candidate.skills.slice(0, 3).join(", ")} align with core requirements`);
  if (scores.experience >= 80) s.push(`${candidate.experience_years} years of directly relevant ML experience`);
  if (scores.learning >= 80) s.push(`High learning velocity — ${candidate.certifications.length} relevant certifications`);
  if (scores.leadership >= 70) s.push("Demonstrated leadership and mentorship experience");
  if (candidate.achievements.some(a => a.includes("patent") || a.includes("paper"))) s.push("Research contributions show deep domain expertise");
  return s.slice(0, 3);
}

function getWeaknesses(candidate, scores) {
  const w = [];
  if (scores.skill < 60) w.push("Missing several core required skills (PyTorch, LLMs, FAISS)");
  if (scores.experience < 60) w.push(`${candidate.experience_years} years may be below the 5+ year requirement`);
  if (scores.leadership < 50) w.push("Limited evidence of team leadership or mentorship");
  if (!candidate.skills.includes("Kubernetes")) w.push("No MLOps/infrastructure experience (Kubernetes, monitoring)");
  return w.slice(0, 2);
}

function getRank(score) {
  if (score >= 85) return { label: "🔥 Strong Match", color: "#10b981", bg: "#064e3b" };
  if (score >= 70) return { label: "✅ Good Match", color: "#3b82f6", bg: "#083344" };
  if (score >= 55) return { label: "⚡ Partial Match", color: "#f59e0b", bg: "#451a03" };
  return { label: "❌ Weak Match", color: "#ef4444", bg: "#450a0a" };
}

// ─── COMPONENTS ──────────────────────────────────────────────────────────────

function ScoreBar({ label, value, color = "#06b6d4" }) {
  return (
    <div style={{ marginBottom: "8px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "4px" }}>
        <span style={{ fontSize: "11px", color: "#94a3b8" }}>{label}</span>
        <span style={{ fontSize: "11px", fontWeight: "700", color }}>{value}</span>
      </div>
      <div style={{ height: "4px", background: "#1e293b", borderRadius: "4px", overflow: "hidden" }}>
        <div style={{ 
          height: "100%", width: `${value}%`, background: color, 
          borderRadius: "4px", transition: "width 0.8s ease" 
        }} />
      </div>
    </div>
  );
}

function RadarMini({ scores }) {
  const dims = [
    { key: "skill", label: "Skills", color: "#06b6d4" },
    { key: "experience", label: "Exp", color: "#10b981" },
    { key: "learning", label: "Learn", color: "#f59e0b" },
    { key: "leadership", label: "Lead", color: "#ec4899" },
    { key: "behavior", label: "Behavior", color: "#3b82f6" },
    { key: "culture", label: "Culture", color: "#14b8a6" },
  ];
  
  return (
    <div style={{ display: "flex", gap: "4px", flexWrap: "wrap" }}>
      {dims.map(d => (
        <div key={d.key} style={{ 
          background: `${d.color}20`, border: `1px solid ${d.color}40`,
          borderRadius: "6px", padding: "4px 8px", textAlign: "center"
        }}>
          <div style={{ fontSize: "13px", fontWeight: "700", color: d.color }}>{scores[d.key]}</div>
          <div style={{ fontSize: "9px", color: "#94a3b8" }}>{d.label}</div>
        </div>
      ))}
    </div>
  );
}

function CandidateCard({ candidate, rank, scores, onClick, selected }) {
  const rankInfo = getRank(scores.final);
  const strengths = getStrengths(candidate, scores);
  
  return (
    <div
      onClick={() => onClick(candidate, scores)}
      style={{
        background: selected ? "#1e293b" : "#0f172a",
        border: selected ? "1px solid #06b6d4" : "1px solid #1e293b",
        borderRadius: "12px", padding: "16px", cursor: "pointer",
        transition: "all 0.2s", marginBottom: "8px",
        boxShadow: selected ? "0 0 0 2px #06b6d430" : "none",
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "10px" }}>
        <div style={{ display: "flex", gap: "10px", alignItems: "flex-start" }}>
          <div style={{ 
            width: "36px", height: "36px", borderRadius: "50%", 
            background: `linear-gradient(135deg, #06b6d4, #14b8a6)`,
            display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: "14px", fontWeight: "800", color: "#e2e8f0", flexShrink: 0
          }}>
            {candidate.name.split(" ").map(n => n[0]).join("")}
          </div>
          <div>
            <div style={{ fontWeight: "700", color: "#e2e8f0", fontSize: "14px" }}>
              #{rank} {candidate.name}
            </div>
            <div style={{ fontSize: "11px", color: "#94a3b8", marginTop: "1px" }}>{candidate.headline.slice(0, 50)}...</div>
          </div>
        </div>
        <div style={{ textAlign: "right" }}>
          <div style={{ 
            fontSize: "22px", fontWeight: "900", 
            color: scores.final >= 85 ? "#10b981" : scores.final >= 70 ? "#06b6d4" : scores.final >= 55 ? "#f59e0b" : "#ef4444"
          }}>
            {scores.final}
          </div>
          <div style={{ fontSize: "9px", color: "#94a3b8" }}>FIT SCORE</div>
        </div>
      </div>
      
      <div style={{ 
        display: "inline-block", padding: "2px 8px", borderRadius: "12px",
        background: rankInfo.bg, color: rankInfo.color, fontSize: "10px", fontWeight: "600",
        marginBottom: "10px"
      }}>
        {rankInfo.label}
      </div>
      
      <RadarMini scores={scores} />
      
      {strengths.length > 0 && (
        <div style={{ marginTop: "10px" }}>
          <div style={{ fontSize: "10px", color: "#10b981", fontWeight: "600", marginBottom: "4px" }}>TOP STRENGTHS</div>
          {strengths.slice(0, 1).map((s, i) => (
            <div key={i} style={{ fontSize: "11px", color: "#94a3b8" }}>• {s}</div>
          ))}
        </div>
      )}
    </div>
  );
}

function DetailPanel({ candidate, scores, onClose }) {
  const strengths = getStrengths(candidate, scores);
  const weaknesses = getWeaknesses(candidate, scores);
  const rankInfo = getRank(scores.final);
  
  return (
    <div style={{ 
      position: "fixed", right: 0, top: 0, bottom: 0, width: "380px",
      background: "#0f172a", borderLeft: "1px solid #1e293b",
      overflowY: "auto", padding: "20px", zIndex: 100,
      boxShadow: "-10px 0 40px rgba(0,0,0,0.5)"
    }}>
      <button onClick={onClose} style={{ 
        position: "absolute", top: "16px", right: "16px",
        background: "#1e293b", border: "none", color: "#94a3b8",
        borderRadius: "8px", padding: "6px 12px", cursor: "pointer", fontSize: "12px"
      }}>✕ Close</button>
      
      <div style={{ marginBottom: "20px", paddingRight: "40px" }}>
        <div style={{ 
          width: "52px", height: "52px", borderRadius: "50%",
          background: "linear-gradient(135deg, #06b6d4, #14b8a6)",
          display: "flex", alignItems: "center", justifyContent: "center",
          fontSize: "18px", fontWeight: "800", color: "#e2e8f0", marginBottom: "12px"
        }}>
          {candidate.name.split(" ").map(n => n[0]).join("")}
        </div>
        <div style={{ fontSize: "18px", fontWeight: "800", color: "#e2e8f0" }}>{candidate.name}</div>
        <div style={{ fontSize: "12px", color: "#94a3b8", marginTop: "2px" }}>{candidate.headline}</div>
        <div style={{ fontSize: "11px", color: "#94a3b8", marginTop: "4px" }}>📍 {candidate.location}</div>
      </div>

      {/* Overall Score */}
      <div style={{ 
        background: "#1e293b", borderRadius: "12px", padding: "16px", marginBottom: "16px",
        textAlign: "center"
      }}>
        <div style={{ fontSize: "48px", fontWeight: "900", color: rankInfo.color, lineHeight: 1 }}>
          {scores.final}
        </div>
        <div style={{ fontSize: "12px", color: "#94a3b8", marginTop: "4px" }}>Overall Fit Score / 100</div>
        <div style={{ 
          display: "inline-block", marginTop: "8px", padding: "3px 10px", borderRadius: "12px",
          background: `${rankInfo.color}20`, color: rankInfo.color, fontSize: "11px", fontWeight: "600"
        }}>
          {rankInfo.label}
        </div>
      </div>

      {/* Agent Scores */}
      <div style={{ background: "#1e293b", borderRadius: "12px", padding: "16px", marginBottom: "16px" }}>
        <div style={{ fontSize: "11px", color: "#06b6d4", fontWeight: "700", marginBottom: "12px", letterSpacing: "0.1em" }}>
          AI AGENT SCORES
        </div>
        <ScoreBar label="Skill Match (35%)" value={scores.skill} color="#06b6d4" />
        <ScoreBar label="Experience (25%)" value={scores.experience} color="#10b981" />
        <ScoreBar label="Learning Velocity (15%)" value={scores.learning} color="#f59e0b" />
        <ScoreBar label="Leadership (10%)" value={scores.leadership} color="#ec4899" />
        <ScoreBar label="Behavior (10%)" value={scores.behavior} color="#3b82f6" />
        <ScoreBar label="Culture Fit (5%)" value={scores.culture} color="#14b8a6" />
      </div>

      {/* Predictions */}
      <div style={{ background: "#1e293b", borderRadius: "12px", padding: "16px", marginBottom: "16px" }}>
        <div style={{ fontSize: "11px", color: "#f59e0b", fontWeight: "700", marginBottom: "12px", letterSpacing: "0.1em" }}>
          🔮 SUCCESS PREDICTIONS
        </div>
        {[
          { label: "Interview Success", value: scores.interview_prob, color: "#10b981" },
          { label: "Offer Acceptance", value: 0.65 + scores.experience / 400, color: "#06b6d4" },
          { label: "18-Month Retention", value: scores.retention_prob, color: "#3b82f6" },
          { label: "High Performer Probability", value: (scores.skill + scores.learning) / 200, color: "#ec4899" },
        ].map(p => (
          <div key={p.label} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
            <span style={{ fontSize: "11px", color: "#94a3b8" }}>{p.label}</span>
            <span style={{ 
              fontSize: "12px", fontWeight: "700", color: p.color,
              background: `${p.color}20`, padding: "2px 8px", borderRadius: "8px"
            }}>
              {Math.min(97, Math.round(p.value * 100))}%
            </span>
          </div>
        ))}
      </div>

      {/* Explainability */}
      {strengths.length > 0 && (
        <div style={{ background: "#064e3b40", border: "1px solid #10b98130", borderRadius: "12px", padding: "14px", marginBottom: "12px" }}>
          <div style={{ fontSize: "11px", color: "#10b981", fontWeight: "700", marginBottom: "8px" }}>✅ STRENGTHS</div>
          {strengths.map((s, i) => (
            <div key={i} style={{ fontSize: "11px", color: "#94a3b8", marginBottom: "4px" }}>• {s}</div>
          ))}
        </div>
      )}
      
      {weaknesses.length > 0 && (
        <div style={{ background: "#450a0a50", border: "1px solid #ef444430", borderRadius: "12px", padding: "14px", marginBottom: "12px" }}>
          <div style={{ fontSize: "11px", color: "#ef4444", fontWeight: "700", marginBottom: "8px" }}>⚠️ GAPS & RISKS</div>
          {weaknesses.map((w, i) => (
            <div key={i} style={{ fontSize: "11px", color: "#94a3b8", marginBottom: "4px" }}>• {w}</div>
          ))}
        </div>
      )}

      {/* Skills */}
      <div style={{ background: "#1e293b", borderRadius: "12px", padding: "14px", marginBottom: "12px" }}>
        <div style={{ fontSize: "11px", color: "#94a3b8", fontWeight: "700", marginBottom: "8px" }}>SKILL PROFILE</div>
        <div style={{ display: "flex", flexWrap: "wrap", gap: "4px" }}>
          {candidate.skills.map(s => {
            const isRequired = ["Python", "PyTorch", "NLP", "LLMs", "AWS", "FAISS"].includes(s);
            return (
              <span key={s} style={{ 
                fontSize: "10px", padding: "2px 7px", borderRadius: "4px",
                background: isRequired ? "#06b6d420" : "#1e293b",
                color: isRequired ? "#67e8f9" : "#94a3b8",
                border: `1px solid ${isRequired ? "#06b6d440" : "#1e293b"}`
              }}>
                {isRequired ? "✓ " : ""}{s}
              </span>
            );
          })}
        </div>
      </div>

      {/* Experience */}
      <div style={{ background: "#1e293b", borderRadius: "12px", padding: "14px" }}>
        <div style={{ fontSize: "11px", color: "#94a3b8", fontWeight: "700", marginBottom: "8px" }}>BACKGROUND</div>
        <div style={{ fontSize: "12px", color: "#e2e8f0", marginBottom: "4px" }}>💼 {candidate.recent_role}</div>
        <div style={{ fontSize: "12px", color: "#94a3b8", marginBottom: "4px" }}>🎓 {candidate.education}</div>
        <div style={{ fontSize: "11px", color: "#94a3b8", marginTop: "8px" }}>
          {candidate.achievements.map((a, i) => (
            <div key={i} style={{ marginBottom: "3px" }}>⚡ {a}</div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ─── MAIN APP ─────────────────────────────────────────────────────────────────

export default function TalentGPT() {
  const [tab, setTab] = useState("dashboard");
  const [jdText, setJdText] = useState(SAMPLE_JD);
  const [analyzed, setAnalyzed] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [rankings, setRankings] = useState([]);
  const [selectedCandidate, setSelectedCandidate] = useState(null);
  const [selectedScores, setSelectedScores] = useState(null);
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const [jdAnalysis, setJdAnalysis] = useState(null);
  const [jdLoading, setJdLoading] = useState(false);
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatMessages]);

  const runAnalysis = async () => {
    setAnalyzing(true);
    await new Promise(r => setTimeout(r, 1500)); // Simulate AI processing
    
    const scored = SAMPLE_CANDIDATES.map(c => ({
      candidate: c,
      scores: scoreCandidate(c, []),
    }));
    scored.sort((a, b) => b.scores.final - a.scores.final);
    
    setRankings(scored.map((r, i) => ({ ...r, rank: i + 1 })));
    setAnalyzed(true);
    setAnalyzing(false);
    setTab("candidates");
  };

  const analyzeJD = async () => {
    setJdLoading(true);
    try {
      const response = await fetch("https://api.anthropic.com/v1/messages", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          model: "claude-sonnet-4-6",
          max_tokens: 1000,
          system: "You are an expert AI recruiter. Extract structured data from job descriptions. Return only valid JSON with no markdown.",
          messages: [{
            role: "user",
            content: `Analyze this job description and return JSON with: required_skills (array), preferred_skills (array), hidden_skills (array, inferred), seniority_level, experience_min_years, experience_max_years, industry, key_soft_skills (array), top_3_must_haves (array).

JD: ${jdText.slice(0, 2000)}`
          }]
        })
      });
      const data = await response.json();
      const text = data.content[0].text;
      try {
        setJdAnalysis(JSON.parse(text));
      } catch {
        const match = text.match(/\{[\s\S]*\}/);
        if (match) setJdAnalysis(JSON.parse(match[0]));
      }
    } catch (e) {
      console.error(e);
    }
    setJdLoading(false);
  };

  const sendChat = async () => {
    if (!chatInput.trim() || chatLoading) return;
    const userMsg = chatInput;
    setChatInput("");
    setChatLoading(true);
    
    const newMessages = [...chatMessages, { role: "user", content: userMsg }];
    setChatMessages(newMessages);
    
    const candidateContext = rankings.map(r => 
      `#${r.rank} ${r.candidate.name}: Score ${r.scores.final}/100 | Skills: ${r.candidate.skills.slice(0,5).join(", ")} | Experience: ${r.candidate.experience_years}yr | ${r.candidate.recent_role}`
    ).join("\n");
    
    try {
      const response = await fetch("https://api.anthropic.com/v1/messages", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          model: "claude-sonnet-4-6",
          max_tokens: 1000,
          system: `You are TalentGPT CoPilot — an elite AI Recruiter Assistant. Be concise, insightful, and data-driven. Use bullet points. Reference specific candidates by name and scores.

RANKED CANDIDATES:
${candidateContext}

JOB: Senior ML Engineer requiring Python, PyTorch, NLP, LLMs, FAISS, AWS (5+ years experience)`,
          messages: newMessages.map(m => ({ role: m.role, content: m.content }))
        })
      });
      const data = await response.json();
      const reply = data.content[0].text;
      setChatMessages(prev => [...prev, { role: "assistant", content: reply }]);
    } catch (e) {
      setChatMessages(prev => [...prev, { role: "assistant", content: "Unable to connect to AI. Please check your connection." }]);
    }
    setChatLoading(false);
  };

  const tabs = [
    { id: "dashboard", label: "🏠 Dashboard" },
    { id: "jd", label: "📋 JD Analyzer" },
    { id: "candidates", label: `👥 Rankings ${analyzed ? `(${rankings.length})` : ""}` },
    { id: "chat", label: "🤖 AI CoPilot" },
    { id: "compare", label: "⚖️ Compare" },
  ];

  const s = { background: "#020617", minHeight: "100vh", fontFamily: "'Inter', system-ui, sans-serif", color: "#e2e8f0" };
  const accent = "#06b6d4";

  return (
    <div style={s}>
      {/* Header */}
      <div style={{ 
        background: "#020617", borderBottom: "1px solid #1e293b",
        padding: "0 24px", display: "flex", alignItems: "center", gap: "32px", height: "52px"
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <div style={{ 
            width: "28px", height: "28px", background: "linear-gradient(135deg, #06b6d4, #14b8a6)",
            borderRadius: "8px", display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: "14px", fontWeight: "800"
          }}>T</div>
          <span style={{ fontWeight: "800", fontSize: "15px", letterSpacing: "-0.3px" }}>
            Talent<span style={{ color: accent }}>GPT</span>
          </span>
          <span style={{ fontSize: "10px", color: "#94a3b8", background: "#1e293b", padding: "1px 6px", borderRadius: "4px" }}>
            v1.0
          </span>
        </div>
        
        <div style={{ display: "flex", gap: "2px" }}>
          {tabs.map(t => (
            <button key={t.id} onClick={() => setTab(t.id)} style={{
              padding: "6px 12px", borderRadius: "6px", border: "none", cursor: "pointer",
              background: tab === t.id ? "#1e293b" : "transparent",
              color: tab === t.id ? "white" : "#94a3b8", fontSize: "12px", fontWeight: "500",
              transition: "all 0.15s"
            }}>
              {t.label}
            </button>
          ))}
        </div>

        <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: "8px" }}>
          <div style={{ width: "6px", height: "6px", borderRadius: "50%", background: "#10b981" }} />
          <span style={{ fontSize: "11px", color: "#94a3b8" }}>AI Ready</span>
        </div>
      </div>

      {/* Content */}
      <div style={{ padding: "24px", maxWidth: selectedCandidate ? "calc(100% - 400px)" : "100%", transition: "max-width 0.3s" }}>
        
        {/* DASHBOARD */}
        {tab === "dashboard" && (
          <div>
            <div style={{ marginBottom: "32px" }}>
              <h1 style={{ fontSize: "28px", fontWeight: "900", margin: "0 0 8px", letterSpacing: "-0.5px" }}>
                AI Talent Intelligence Platform
              </h1>
              <p style={{ color: "#94a3b8", margin: 0, fontSize: "14px" }}>
                Multi-agent AI that thinks like an elite recruiter. Not keywords — intelligence.
              </p>
            </div>

            {/* Stats */}
            {analyzed && (
              <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "12px", marginBottom: "24px" }}>
                {[
                  { label: "Candidates Analyzed", value: rankings.length, color: accent },
                  { label: "Strong Matches", value: rankings.filter(r => r.scores.final >= 85).length, color: "#10b981" },
                  { label: "Avg Fit Score", value: `${(rankings.reduce((s, r) => s + r.scores.final, 0) / rankings.length).toFixed(1)}`, color: "#f59e0b" },
                  { label: "AI Agents Used", value: "6", color: "#ec4899" },
                ].map(stat => (
                  <div key={stat.label} style={{ background: "#0f172a", border: "1px solid #1e293b", borderRadius: "12px", padding: "16px" }}>
                    <div style={{ fontSize: "28px", fontWeight: "900", color: stat.color }}>{stat.value}</div>
                    <div style={{ fontSize: "11px", color: "#94a3b8", marginTop: "4px" }}>{stat.label}</div>
                  </div>
                ))}
              </div>
            )}

            {/* How it works */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "12px", marginBottom: "24px" }}>
              {[
                { icon: "📋", title: "JD Intelligence Engine", desc: "Deeply understands job requirements. Extracts hidden skills, seniority signals, capability graphs — not just keyword lists." },
                { icon: "🤖", title: "6-Agent Scoring System", desc: "Independent AI agents evaluate Skills, Experience, Learning, Leadership, Behavior, and Culture Fit in parallel." },
                { icon: "🔮", title: "Success Prediction", desc: "ML models predict interview success, offer acceptance, and 18-month retention probability before first call." },
              ].map(item => (
                <div key={item.title} style={{ background: "#0f172a", border: "1px solid #1e293b", borderRadius: "12px", padding: "20px" }}>
                  <div style={{ fontSize: "28px", marginBottom: "10px" }}>{item.icon}</div>
                  <div style={{ fontWeight: "700", marginBottom: "6px", fontSize: "14px" }}>{item.title}</div>
                  <div style={{ fontSize: "12px", color: "#94a3b8", lineHeight: "1.5" }}>{item.desc}</div>
                </div>
              ))}
            </div>

            {/* Scoring breakdown */}
            <div style={{ background: "#0f172a", border: "1px solid #1e293b", borderRadius: "12px", padding: "20px", marginBottom: "24px" }}>
              <div style={{ fontWeight: "700", marginBottom: "16px", fontSize: "14px" }}>📊 Committee Scoring Weights</div>
              <div style={{ display: "flex", gap: "8px", alignItems: "flex-end" }}>
                {[
                  { label: "Skills", pct: 35, color: "#06b6d4" },
                  { label: "Experience", pct: 25, color: "#10b981" },
                  { label: "Learning", pct: 15, color: "#f59e0b" },
                  { label: "Leadership", pct: 10, color: "#ec4899" },
                  { label: "Behavior", pct: 10, color: "#3b82f6" },
                  { label: "Culture", pct: 5, color: "#14b8a6" },
                ].map(w => (
                  <div key={w.label} style={{ flex: 1, textAlign: "center" }}>
                    <div style={{ height: `${w.pct * 3}px`, background: w.color, borderRadius: "4px 4px 0 0", marginBottom: "6px", opacity: 0.8 }} />
                    <div style={{ fontSize: "11px", fontWeight: "700", color: w.color }}>{w.pct}%</div>
                    <div style={{ fontSize: "9px", color: "#94a3b8" }}>{w.label}</div>
                  </div>
                ))}
              </div>
            </div>

            <button
              onClick={runAnalysis}
              disabled={analyzing}
              style={{
                padding: "14px 32px", background: "linear-gradient(135deg, #06b6d4, #14b8a6)",
                border: "none", borderRadius: "10px", color: "#e2e8f0", fontSize: "14px",
                fontWeight: "700", cursor: analyzing ? "not-allowed" : "pointer",
                opacity: analyzing ? 0.7 : 1, transition: "all 0.2s",
              }}
            >
              {analyzing ? "🔄 Running 6 AI Agents..." : "🚀 Analyze Candidates Now"}
            </button>
          </div>
        )}

        {/* JD ANALYZER */}
        {tab === "jd" && (
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px" }}>
            <div>
              <h2 style={{ fontSize: "18px", fontWeight: "800", marginBottom: "16px" }}>📋 Job Description Analyzer</h2>
              <textarea
                value={jdText}
                onChange={e => setJdText(e.target.value)}
                style={{ 
                  width: "100%", height: "400px", background: "#0f172a", border: "1px solid #1e293b",
                  borderRadius: "10px", padding: "16px", color: "#e2e8f0", fontSize: "12px",
                  lineHeight: "1.6", resize: "vertical", boxSizing: "border-box"
                }}
                placeholder="Paste your job description here..."
              />
              <button
                onClick={analyzeJD}
                disabled={jdLoading}
                style={{ 
                  marginTop: "12px", padding: "10px 24px", background: accent,
                  border: "none", borderRadius: "8px", color: "#e2e8f0",
                  fontSize: "13px", fontWeight: "600", cursor: "pointer"
                }}
              >
                {jdLoading ? "🔄 Analyzing with AI..." : "🧠 Extract Intelligence"}
              </button>
            </div>
            
            <div>
              <h2 style={{ fontSize: "18px", fontWeight: "800", marginBottom: "16px" }}>🎯 Role Intelligence</h2>
              {!jdAnalysis && !jdLoading && (
                <div style={{ 
                  height: "400px", background: "#0f172a", border: "1px dashed #1e293b",
                  borderRadius: "10px", display: "flex", alignItems: "center", justifyContent: "center",
                  color: "#94a3b8", fontSize: "13px"
                }}>
                  Click "Extract Intelligence" to analyze the JD
                </div>
              )}
              {jdLoading && (
                <div style={{ 
                  height: "400px", background: "#0f172a", border: "1px solid #1e293b",
                  borderRadius: "10px", display: "flex", alignItems: "center", justifyContent: "center",
                  flexDirection: "column", gap: "12px"
                }}>
                  <div style={{ fontSize: "32px" }}>🧠</div>
                  <div style={{ color: "#06b6d4", fontSize: "13px" }}>Claude AI analyzing JD...</div>
                </div>
              )}
              {jdAnalysis && (
                <div style={{ background: "#0f172a", border: "1px solid #1e293b", borderRadius: "10px", padding: "16px", overflowY: "auto", maxHeight: "500px" }}>
                  {[
                    { label: "Required Skills", key: "required_skills", color: "#ef4444" },
                    { label: "Preferred Skills", key: "preferred_skills", color: "#f59e0b" },
                    { label: "Hidden Skills (AI-Inferred)", key: "hidden_skills", color: "#06b6d4" },
                    { label: "Top 3 Must-Haves", key: "top_3_must_haves", color: "#10b981" },
                    { label: "Soft Skills", key: "key_soft_skills", color: "#ec4899" },
                  ].map(section => (
                    jdAnalysis[section.key] && (
                      <div key={section.key} style={{ marginBottom: "14px" }}>
                        <div style={{ fontSize: "10px", color: section.color, fontWeight: "700", marginBottom: "6px", letterSpacing: "0.1em" }}>
                          {section.label.toUpperCase()}
                        </div>
                        <div style={{ display: "flex", flexWrap: "wrap", gap: "4px" }}>
                          {(Array.isArray(jdAnalysis[section.key]) ? jdAnalysis[section.key] : []).map(s => (
                            <span key={s} style={{ 
                              fontSize: "11px", padding: "2px 8px", borderRadius: "4px",
                              background: `${section.color}15`, color: section.color,
                              border: `1px solid ${section.color}30`
                            }}>{s}</span>
                          ))}
                        </div>
                      </div>
                    )
                  ))}
                  {jdAnalysis.seniority_level && (
                    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "8px", marginTop: "8px" }}>
                      {[
                        { label: "Seniority", value: jdAnalysis.seniority_level },
                        { label: "Experience", value: `${jdAnalysis.experience_min_years || 0}-${jdAnalysis.experience_max_years || 10} years` },
                        { label: "Industry", value: jdAnalysis.industry || "Technology" },
                      ].map(item => (
                        <div key={item.label} style={{ background: "#1e293b", borderRadius: "8px", padding: "10px" }}>
                          <div style={{ fontSize: "9px", color: "#94a3b8", marginBottom: "2px" }}>{item.label.toUpperCase()}</div>
                          <div style={{ fontSize: "13px", fontWeight: "600", color: "#e2e8f0", textTransform: "capitalize" }}>{item.value}</div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        )}

        {/* RANKINGS */}
        {tab === "candidates" && (
          <div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
              <h2 style={{ fontSize: "18px", fontWeight: "800", margin: 0 }}>
                👥 Ranked Candidates
                {analyzed && <span style={{ color: "#94a3b8", fontWeight: "400", fontSize: "14px", marginLeft: "8px" }}>
                  — {rankings.length} candidates analyzed
                </span>}
              </h2>
              {!analyzed && (
                <button onClick={runAnalysis} disabled={analyzing} style={{
                  padding: "8px 20px", background: accent, border: "none", borderRadius: "8px",
                  color: "#e2e8f0", fontSize: "12px", fontWeight: "600", cursor: "pointer"
                }}>
                  {analyzing ? "Running..." : "Run AI Analysis"}
                </button>
              )}
            </div>
            
            {!analyzed && (
              <div style={{ 
                textAlign: "center", padding: "60px 20px",
                background: "#0f172a", border: "1px dashed #1e293b", borderRadius: "12px"
              }}>
                <div style={{ fontSize: "48px", marginBottom: "16px" }}>🤖</div>
                <div style={{ fontSize: "16px", fontWeight: "700", marginBottom: "8px" }}>Ready to Rank Candidates</div>
                <div style={{ color: "#94a3b8", fontSize: "13px" }}>6 AI agents will evaluate all candidates in parallel</div>
              </div>
            )}

            {analyzed && (
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))", gap: "8px" }}>
                {rankings.map(r => (
                  <CandidateCard
                    key={r.candidate.id}
                    candidate={r.candidate}
                    rank={r.rank}
                    scores={r.scores}
                    selected={selectedCandidate?.id === r.candidate.id}
                    onClick={(c, s) => { setSelectedCandidate(c); setSelectedScores(s); }}
                  />
                ))}
              </div>
            )}
          </div>
        )}

        {/* CHAT */}
        {tab === "chat" && (
          <div>
            <h2 style={{ fontSize: "18px", fontWeight: "800", marginBottom: "4px" }}>🤖 Recruiter CoPilot</h2>
            <p style={{ color: "#94a3b8", fontSize: "12px", marginBottom: "20px" }}>
              Ask anything about candidates, get AI-powered hiring intelligence
            </p>

            {!analyzed && (
              <div style={{ background: "#451a0340", border: "1px solid #f59e0b30", borderRadius: "10px", padding: "12px", marginBottom: "16px", fontSize: "12px", color: "#f59e0b" }}>
                ⚠️ Run candidate analysis first for best results. Go to Dashboard → Analyze Candidates Now
              </div>
            )}

            <div style={{ 
              background: "#0f172a", border: "1px solid #1e293b", borderRadius: "12px",
              height: "400px", overflowY: "auto", padding: "16px", marginBottom: "12px"
            }}>
              {chatMessages.length === 0 && (
                <div style={{ color: "#94a3b8", fontSize: "13px" }}>
                  <div style={{ marginBottom: "16px" }}>💬 Start chatting with your AI Recruiter CoPilot</div>
                  <div style={{ fontSize: "12px" }}>Try:</div>
                  {[
                    "Who are your top 3 candidates and why?",
                    "Which candidate has the best Python + ML skills?",
                    "Who is most likely to stay long-term?",
                    "Compare Arjun Sharma and Sneha Patel",
                    "Who has leadership potential?",
                  ].map(q => (
                    <div
                      key={q}
                      onClick={() => { setChatInput(q); }}
                      style={{ 
                        fontSize: "11px", color: "#06b6d4", cursor: "pointer", 
                        marginTop: "6px", padding: "6px 10px", background: "#06b6d410",
                        borderRadius: "6px", display: "inline-block", marginRight: "6px"
                      }}
                    >
                      {q}
                    </div>
                  ))}
                </div>
              )}
              {chatMessages.map((msg, i) => (
                <div key={i} style={{ 
                  marginBottom: "16px", 
                  display: "flex", justifyContent: msg.role === "user" ? "flex-end" : "flex-start"
                }}>
                  <div style={{
                    maxWidth: "80%", padding: "10px 14px", borderRadius: "12px",
                    background: msg.role === "user" ? accent : "#1e293b",
                    fontSize: "13px", lineHeight: "1.5",
                    whiteSpace: "pre-wrap"
                  }}>
                    {msg.role === "assistant" && (
                      <div style={{ fontSize: "10px", color: "#06b6d4", fontWeight: "700", marginBottom: "6px" }}>
                        🤖 TALENTGPT COPILOT
                      </div>
                    )}
                    {msg.content}
                  </div>
                </div>
              ))}
              {chatLoading && (
                <div style={{ display: "flex", gap: "4px", padding: "10px 14px", background: "#1e293b", borderRadius: "12px", width: "fit-content" }}>
                  {[0, 1, 2].map(i => (
                    <div key={i} style={{ 
                      width: "6px", height: "6px", borderRadius: "50%", background: accent,
                      animation: `pulse 1s ease-in-out ${i * 0.2}s infinite alternate`
                    }} />
                  ))}
                </div>
              )}
              <div ref={chatEndRef} />
            </div>

            <div style={{ display: "flex", gap: "8px" }}>
              <input
                value={chatInput}
                onChange={e => setChatInput(e.target.value)}
                onKeyDown={e => e.key === "Enter" && sendChat()}
                placeholder="Ask about candidates, skills, predictions..."
                style={{ 
                  flex: 1, background: "#0f172a", border: "1px solid #1e293b",
                  borderRadius: "8px", padding: "10px 14px", color: "#e2e8f0",
                  fontSize: "13px", outline: "none"
                }}
              />
              <button
                onClick={sendChat}
                disabled={chatLoading || !chatInput.trim()}
                style={{
                  padding: "10px 20px", background: accent, border: "none",
                  borderRadius: "8px", color: "#e2e8f0", fontSize: "13px",
                  fontWeight: "600", cursor: "pointer", opacity: chatLoading ? 0.6 : 1
                }}
              >
                Send
              </button>
            </div>
          </div>
        )}

        {/* COMPARE */}
        {tab === "compare" && analyzed && (
          <div>
            <h2 style={{ fontSize: "18px", fontWeight: "800", marginBottom: "20px" }}>⚖️ Candidate Comparison</h2>
            <div style={{ display: "grid", gridTemplateColumns: `repeat(${Math.min(3, rankings.length)}, 1fr)`, gap: "12px" }}>
              {rankings.slice(0, 3).map(r => (
                <div key={r.candidate.id} style={{ background: "#0f172a", border: "1px solid #1e293b", borderRadius: "12px", padding: "16px" }}>
                  <div style={{ fontWeight: "700", marginBottom: "4px", fontSize: "15px" }}>#{r.rank} {r.candidate.name}</div>
                  <div style={{ fontSize: "11px", color: "#94a3b8", marginBottom: "16px" }}>{r.candidate.recent_role}</div>
                  
                  <div style={{ 
                    fontSize: "36px", fontWeight: "900", textAlign: "center", marginBottom: "16px",
                    color: r.scores.final >= 85 ? "#10b981" : r.scores.final >= 70 ? "#06b6d4" : "#f59e0b"
                  }}>
                    {r.scores.final}
                  </div>
                  
                  {[
                    { label: "Skills", value: r.scores.skill, color: "#06b6d4" },
                    { label: "Experience", value: r.scores.experience, color: "#10b981" },
                    { label: "Learning", value: r.scores.learning, color: "#f59e0b" },
                    { label: "Leadership", value: r.scores.leadership, color: "#ec4899" },
                    { label: "Behavior", value: r.scores.behavior, color: "#3b82f6" },
                    { label: "Culture", value: r.scores.culture, color: "#14b8a6" },
                  ].map(dim => <ScoreBar key={dim.label} label={dim.label} value={dim.value} color={dim.color} />)}
                  
                  <div style={{ marginTop: "12px", fontSize: "11px", color: "#10b981" }}>
                    ✅ {getStrengths(r.candidate, r.scores)[0]}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
        
        {tab === "compare" && !analyzed && (
          <div style={{ textAlign: "center", padding: "60px", color: "#94a3b8" }}>
            Run analysis first to compare candidates side by side
          </div>
        )}
      </div>

      {/* Detail Panel */}
      {selectedCandidate && selectedScores && (
        <DetailPanel
          candidate={selectedCandidate}
          scores={selectedScores}
          onClose={() => { setSelectedCandidate(null); setSelectedScores(null); }}
        />
      )}
      
      <style>{`
        @keyframes pulse { from { opacity: 0.4; } to { opacity: 1; } }
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-track { background: #0f172a; }
        ::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 4px; }
        * { box-sizing: border-box; }
      `}</style>
    </div>
  );
}
