# src/features/build_features.py
import pandas as pd
import numpy as np
from pathlib import Path
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# ======================
# CONFIG
# ======================

PROCESSED = Path("data/processed")
FEATURES_OUTPUT = PROCESSED / "features.parquet"

# Initialize sentence transformer (downloads model on first run)
print("📥 Loading sentence transformer model...")
model = SentenceTransformer("all-MiniLM-L6-v2")
print("✅ Model loaded.")

# ======================
# UTILS
# ======================

def jaccard_similarity(set1, set2):
    if not set1 and not set2:
        return 1.0
    if not set1 or not set2:
        return 0.0
    return len(set1 & set2) / len(set1 | set2)

# ======================
# MAIN PIPELINE
# ======================

def main():
    # Load data
    print("📂 Loading processed data...")
    resumes = pd.read_csv(PROCESSED / "resumes_clean.csv")
    jobs = pd.read_csv(PROCESSED / "jobs_clean.csv")
    pairs = pd.read_csv(PROCESSED / "train_pairs.csv")

    # Convert skill strings back to sets
    print("🔧 Parsing skill lists...")
    resumes["skill_set"] = resumes["skills"].apply(lambda x: set(eval(x)) if pd.notna(x) else set())
    jobs["skill_set"] = jobs["skills"].apply(lambda x: set(eval(x)) if pd.notna(x) else set())

    # Create lookup dicts
    resume_lookup = resumes.set_index("resume_id")[["summary", "skill_set"]].to_dict("index")
    job_lookup = jobs.set_index("job_id")[["title", "skills", "skill_set"]].to_dict("index")

    # Prepare texts for embedding
    print("🔤 Preparing texts for embedding...")
    resume_texts = []
    job_texts = []
    valid_pairs = []

    for _, row in tqdm(pairs.iterrows(), total=len(pairs), desc="Building texts"):
        rid = row["resume_id"]
        jid = row["job_id"]

        if rid not in resume_lookup or jid not in job_lookup:
            continue

        resume_summary = resume_lookup[rid]["summary"] or ""
        job_title = job_lookup[jid]["title"] or ""
        job_skills = job_lookup[jid]["skills"] or ""

        # Combine job title + skills as proxy for full description
        job_text = f"{job_title}. Skills: {job_skills}"

        resume_texts.append(resume_summary)
        job_texts.append(job_text)
        valid_pairs.append(row)

    # Generate embeddings
    print("🧠 Generating embeddings...")
    resume_embeddings = model.encode(resume_texts, show_progress_bar=True, convert_to_numpy=True)
    job_embeddings = model.encode(job_texts, show_progress_bar=True, convert_to_numpy=True)

    # Compute cosine similarities
    print("🧮 Computing semantic similarities...")
    semantic_sims = []
    for i in tqdm(range(len(resume_embeddings)), desc="Cosine similarity"):
        sim = cosine_similarity([resume_embeddings[i]], [job_embeddings[i]])[0][0]
        semantic_sims.append(float(sim))

    # Build feature records
    print("📊 Building feature records...")
    features = []
    for i, row in enumerate(valid_pairs):
        rid = row["resume_id"]
        jid = row["job_id"]

        r_skills = resume_lookup[rid]["skill_set"]
        j_skills = job_lookup[jid]["skill_set"]

        jaccard = jaccard_similarity(r_skills, j_skills)
        overlap_ratio = row["overlap_ratio"]
        label = row["label"]

        features.append({
            "resume_id": rid,
            "job_id": jid,
            "label": label,
            "semantic_sim": semantic_sims[i],
            "jaccard_sim": jaccard,
            "overlap_ratio": overlap_ratio
        })

    # Save
    features_df = pd.DataFrame(features)
    features_df.to_csv(PROCESSED / "features.csv", index=False)
    print(f"✅ Features saved as CSV to data/processed/features.csv")
    print(f"✅ Features saved to {FEATURES_OUTPUT}")
    print(f"📊 Shape: {features_df.shape}")
    print(f"✅ Positive samples: {features_df['label'].sum()}")
    print(f"✅ Features saved to {PROCESSED / 'features.csv'}")

if __name__ == "__main__":
    main()