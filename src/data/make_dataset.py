# src/data/make_dataset.py
import pandas as pd
import ast
import re
import random
from pathlib import Path
from collections import defaultdict
from tqdm import tqdm

# ======================
# CONFIG
# ======================

RAW = Path("data/raw")
PROCESSED = Path("data/processed")
PROCESSED.mkdir(parents=True, exist_ok=True)

# Skill normalization
SKILL_MAP = {
    "scikit learn": "scikit-learn",
    "scikit-learn": "scikit-learn",
    "sklearn": "scikit-learn",
    "tensorflow": "tensorflow",
    "pytorch": "pytorch",
    "keras": "keras",
    "pandas": "pandas",
    "numpy": "numpy",
    "matplotlib": "matplotlib",
    "seaborn": "seaborn",
    "sql": "sql",
    "mysql": "mysql",
    "postgresql": "postgresql",
    "postgres": "postgresql",
    "aws": "aws",
    "azure": "azure",
    "gcp": "gcp",
    "docker": "docker",
    "kubernetes": "kubernetes",
    "spark": "spark",
    "hadoop": "hadoop",
    "git": "git",
    "linux": "linux",
    "tableau": "tableau",
    "powerbi": "power bi",
    "power bi": "power bi",
    "nlp": "nlp",
    "computer vision": "computer vision",
    "deep learning": "deep learning",
    "machine learning": "machine learning",
    "mlops": "mlops",
    "java": "java",
    "python": "python",
    "r": "r",
    "scala": "scala",
}

NON_TECH = {
    "communication", "teamwork", "leadership", "problem solving", "analytical thinking",
    "self-starter", "proactive", "collaboration", "presentation", "english", "fluent",
    "spanish", "management", "recruitment", "hr", "accounting", "marketing", "sales",
    "business development", "client", "customer", "project management", "agile",
    "scrum", "documentation", "reporting", "team collaboration", "fast typing",
    "ielts", "administrative", "support", "mechanical", "civil", "finance", "audit"
}

DS_KEYWORDS = {
    "data science", "machine learning", "deep learning", "artificial intelligence",
    "nlp", "natural language processing", "computer vision", "data analyst",
    "ml engineer", "tensorflow", "pytorch", "scikit", "pandas", "numpy",
    "predictive modeling", "data mining", "statistical analysis", "ai",
    "generative ai", "llm", "transformers", "huggingface", "data scientist"
}

MAX_POSITIVE = 20_000
MAX_NEGATIVE = 40_000

# ======================
# UTILS
# ======================

def normalize_skill(s: str) -> str:
    if not isinstance(s, str):
        return ""
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return SKILL_MAP.get(s, s)

def parse_skills(text):
    if not isinstance(text, str) or not text.strip():
        return []
    try:
        parsed = ast.literal_eval(text)
        if isinstance(parsed, list):
            return [str(x).strip() for x in parsed if isinstance(x, str)]
    except (ValueError, SyntaxError):
        pass
    cleaned = re.sub(r"[\[\]\"\'\n]", "", text)
    parts = re.split(r"[,;]", cleaned)
    return [p.strip() for p in parts if p.strip()]

def clean_skills(raw_list):
    cleaned = []
    for s in raw_list:
        norm = normalize_skill(s)
        if norm and norm not in NON_TECH and len(norm) > 1:
            cleaned.append(norm)
    return sorted(set(cleaned))

def is_relevant_resume(summary: str, skills: list) -> bool:
    text = (str(summary) + " " + " ".join(skills)).lower()
    return any(kw in text for kw in DS_KEYWORDS)

# ======================
# PROCESS RESUMES
# ======================

def process_resumes():
    df = pd.read_csv(RAW / "resume_data.csv", header=None, on_bad_lines="skip")
    resumes = []
    for _, row in df.iterrows():
        summary = ""
        skills_text = ""
        for col in row:
            if pd.isna(col):
                continue
            col = str(col)
            if ("Python" in col or "TensorFlow" in col or "['" in col or '["' in col) and len(col) < 500:
                skills_text = col
            elif ("data science" in col.lower() or "machine learning" in col.lower()) and len(col) > 50:
                summary = col

        if not skills_text:
            continue

        raw_skills = parse_skills(skills_text)
        clean_skills_list = clean_skills(raw_skills)
        if not clean_skills_list:
            continue
        if not is_relevant_resume(summary, clean_skills_list):
            continue

        resumes.append({
            "resume_id": f"r_{len(resumes)}",
            "summary": summary,
            "skills": clean_skills_list,
        })

    resumes_df = pd.DataFrame(resumes)
    resumes_df.to_csv(PROCESSED / "resumes_clean.csv", index=False)
    print(f"✅ Saved {len(resumes_df)} relevant DS resumes.")
    return resumes_df

# ======================
# PROCESS JOBS
# ======================

def process_jobs():
    jobs = []
    df_jobs = pd.read_csv(RAW / "ai_job_dataset.csv", header=None, on_bad_lines="skip")
    for _, row in df_jobs.iterrows():
        if len(row) < 11:
            continue
        job_id = row[0]
        title = row[1]
        skills_raw = row[10]
        if pd.isna(skills_raw) or not isinstance(skills_raw, str):
            continue
        raw_list = [s.strip() for s in str(skills_raw).split(",") if s.strip()]
        cleaned_skills = clean_skills(raw_list)
        if cleaned_skills:
            jobs.append({
                "job_id": job_id,
                "title": title,
                "skills": cleaned_skills,
            })

    jobs_df = pd.DataFrame(jobs)
    jobs_df.to_csv(PROCESSED / "jobs_clean.csv", index=False)
    print(f"✅ Saved {len(jobs_df)} job postings.")
    return jobs_df

# ======================
# GENERATE BALANCED PAIRS
# ======================

def generate_balanced_pairs(resumes_df, jobs_df):
    # Build skill index
    skill_to_jobs = defaultdict(list)
    job_skill_sets = {}
    for _, j in jobs_df.iterrows():
        job_id = j["job_id"]
        skill_set = frozenset(j["skills"])
        job_skill_sets[job_id] = skill_set
        for skill in skill_set:
            skill_to_jobs[skill].append(job_id)

    positive_pairs = []
    negative_pairs = []

    print("🔗 Generating candidate-based pairs (thresholds: pos≥0.35, neg≤0.25)...")
    for _, r in tqdm(resumes_df.iterrows(), total=len(resumes_df)):
        if len(positive_pairs) >= MAX_POSITIVE and len(negative_pairs) >= MAX_NEGATIVE:
            break
        r_skills = set(r["skills"])
        if not r_skills:
            continue

        candidate_job_ids = set()
        for skill in r_skills:
            candidate_job_ids.update(skill_to_jobs[skill])

        for job_id in candidate_job_ids:
            j_skill_set = job_skill_sets[job_id]
            if not j_skill_set:
                continue
            overlap = len(r_skills & j_skill_set)
            ratio = overlap / len(j_skill_set)

            if ratio >= 0.35 and len(positive_pairs) < MAX_POSITIVE:
                positive_pairs.append((r["resume_id"], job_id, ratio, 1))
            elif ratio <= 0.25 and len(negative_pairs) < MAX_NEGATIVE:
                negative_pairs.append((r["resume_id"], job_id, ratio, 0))

    # Add hard negatives if needed
    if len(negative_pairs) < MAX_NEGATIVE:
        print(f"🔗 Adding {MAX_NEGATIVE - len(negative_pairs)} hard negatives...")
        all_job_ids = list(job_skill_sets.keys())
        added = 0
        for _ in tqdm(range(MAX_NEGATIVE - len(negative_pairs))):
            r = resumes_df.sample(n=1).iloc[0]
            j_id = random.choice(all_job_ids)
            j_skills = job_skill_sets[j_id]
            r_skills = set(r["skills"])
            if len(r_skills & j_skills) == 0:
                negative_pairs.append((r["resume_id"], j_id, 0.0, 0))
                added += 1
            if added >= MAX_NEGATIVE - len(negative_pairs):
                break

    # Combine and shuffle
    all_pairs = positive_pairs + negative_pairs
    random.shuffle(all_pairs)

    pairs_df = pd.DataFrame([
        {"resume_id": pid, "job_id": jid, "overlap_ratio": ratio, "label": label}
        for (pid, jid, ratio, label) in all_pairs
    ])

    pairs_df.to_csv(PROCESSED / "train_pairs.csv", index=False)
    pos_count = pairs_df["label"].sum()
    print(f"✅ Generated {len(pairs_df)} balanced pairs ({pos_count} positive, {len(pairs_df)-pos_count} negative).")
    return pairs_df

# ======================
# MAIN
# ======================

def main():
    print("🔧 Processing resumes from resume_data.csv...")
    resumes = process_resumes()

    print("🔧 Processing jobs from ai_job_dataset.csv...")
    jobs = process_jobs()

    print("🔗 Generating labeled pairs...")
    generate_balanced_pairs(resumes, jobs)

    print("🎉 Dataset pipeline complete!")

if __name__ == "__main__":
    main()