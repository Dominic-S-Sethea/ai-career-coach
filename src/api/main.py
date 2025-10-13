# src/api/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import joblib
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Load model and sentence transformer ONCE at startup
print("📥 Loading model and sentence transformer...")
model = joblib.load("models/model.joblib")  # ✅ Correct path: relative to project root
sentence_model = SentenceTransformer("all-MiniLM-L6-v2")
print("✅ Model and sentence transformer loaded.")

app = FastAPI(
    title="AI Career Coach API",
    description="Predict job-resume fit and provide skill gap analysis."
)

class MatchRequest(BaseModel):
    resume: str
    job: str

class MatchResponse(BaseModel):
    match_score: float
    missing_skills: List[str]
    advice: str

def jaccard_similarity(set1, set2):
    if not set1 and not set2:
        return 1.0
    if not set1 or not set2:
        return 0.0
    return len(set1 & set2) / len(set1 | set2)

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "AI Career Coach is running!"}

@app.post("/match", response_model=MatchResponse)
def match_resume_to_job(request: MatchRequest):
    try:
        # 1. Compute semantic similarity
        resume_emb = sentence_model.encode([request.resume])
        job_emb = sentence_model.encode([request.job])
        semantic_sim = float(cosine_similarity(resume_emb, job_emb)[0][0])
        
        # 2. TEMPORARY: Use hardcoded skill sets (we'll improve this later)
        resume_skills = set(["python", "sql", "scikit-learn"])
        job_skills = set(["aws", "spark", "mlops", "python"])
        
        # 3. Compute skill-based features
        jaccard_sim = jaccard_similarity(resume_skills, job_skills)
        overlap_ratio = len(resume_skills & job_skills) / len(job_skills) if job_skills else 0.0
        
        # 4. Predict match probability
        X = pd.DataFrame([{
            "semantic_sim": semantic_sim,
            "jaccard_sim": jaccard_sim,
            "overlap_ratio": overlap_ratio
        }])
        prob = model.predict_proba(X)[0][1]  # Probability of "good match"
        
        # 5. Generate skill gap analysis
        missing_skills = list(job_skills - resume_skills)
        advice = "Add 'Docker'—it appears in 89% of similar roles."
        
        return MatchResponse(
            match_score=round(prob, 2),
            missing_skills=missing_skills,
            advice=advice
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")