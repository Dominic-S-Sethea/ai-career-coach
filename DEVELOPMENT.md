# 🛠️ Development Guide — AI Career Coach (v1-intermediate)

This guide helps you set up, run, and test the AI Career Coach locally.  
Designed for **absolute beginners** — no prior experience needed!

---

## 📋 Prerequisites

Before you begin, install these:

1. **Python 3.10 or higher**  
   → Download from https://www.python.org/downloads/  
   → ✅ **Important**: Check **“Add Python to PATH”** during installation

2. **Git (optional but recommended)**  
   → Download from https://git-scm.com/

---

## 🚀 Quick Start (Run in 2 Minutes)

### Step 1: Clone or Download the Project
#### Option A: With Git
git clone https://github.com/Dominic-S-Sethea/ai-career-coach.git
cd ai-career-coach

#### Option B: Without Git
1. Go to your GitHub repo: https://github.com/Dominic-S-Sethea/ai-career-coach
2. Click **Code → Download ZIP**
3. Extract the ZIP file to a folder (e.g., `ai-career-coach`)

---

### Step 2: Set Up the Environment

Open **Command Prompt** (Windows) or **Terminal** (Mac/Linux) in your project folder.

#### Create a virtual environment (isolates this project):
python -m venv .venv

#### Activate it:
- **Windows (PowerShell)**:
  .venv\Scripts\Activate.ps1
  
  > ⚠️ If you get an error about execution policy, run:  
  > Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

- **Mac/Linux**:
  source .venv/bin/activate

You’ll see `(.venv)` in your prompt when active.

---

### Step 3: Install Dependencies

pip install -r requirements.txt

✅ This installs:
- FastAPI (web framework)
- Uvicorn (server)
- Sentence Transformers (AI model)
- Scikit-learn (machine learning)
- Pandas (data handling)

---

### Step 4: Start the API

uvicorn src.api.main:app --host 0.0.0.0 --port 8000

✅ You’ll see:
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.

> 💡 Keep this terminal open — your API is running here.

---

### Step 5: Test the API

Open a **new terminal tab** and run:

#### On Windows (PowerShell):
$body = @{
    resume = "Experienced in Python, SQL, and Scikit-learn."
    job = "We seek AWS, Spark, and MLOps experience."
} | ConvertTo-Json

Invoke-RestMethod http://localhost:8000/match -Method Post -Body $body -ContentType "application/json"

#### On Mac/Linux (Terminal):
curl -X POST http://localhost:8000/match \
  -H "Content-Type: application/json" \
  -d '{"resume": "Experienced in Python, SQL, and Scikit-learn.", "job": "We seek AWS, Spark, and MLOps experience."}'

✅ Expected response:
{
  "match_score": 0.68,
  "missing_skills": ["aws", "spark", "mlops"],
  "advice": "Add 'Docker'—it appears in 89% of similar roles."
}

---

## 🧪 Running Tests

We include basic tests to verify core functionality:

pytest tests/

> 💡 Tests check:
> - API returns `200 OK`
> - Match score is between `0` and `1`

---

## 📂 Project Structure

| Path | Purpose |
|------|--------|
| src/api/main.py | FastAPI application (the live API) |
| src/models/train_model.py | Trains the match prediction model |
| src/features/build_features.py | Computes semantic + skill features |
| src/data/make_dataset.py | Builds labeled job-resume pairs |
| models/model.joblib | Pre-trained model (no need to retrain) |
| data/raw/ | Original datasets (do not modify) |
| data/processed/ | Cleaned data and features |
| Dockerfile | One-command container setup |
| tests/ | Automated tests |

---

## 🐳 Docker (Optional)

Build and run with Docker:

# Build
docker build -t career-coach .

# Run
docker run -p 8000:8000 career-coach

Then test at http://localhost:8000/match.

---

## ❓ Troubleshooting

### “uvicorn is not recognized”
→ You forgot to activate your virtual environment. Run:
.venv\Scripts\Activate.ps1  # Windows

### “FileNotFoundError: models/model.joblib”
→ The model file is missing. Re-run the pipeline:
python src/data/make_dataset.py
python src/features/build_features.py
python src/models/train_model.py

### “ModuleNotFoundError”
→ Install missing packages:
pip install -r requirements.txt

---

## 🤝 Contributing

This is a **learning-phase project** (`v1-intermediate`).  
For the production-ready version, see the `main` branch.

To contribute:
1. Fork the repo
2. Create a feature branch
3. Submit a pull request

---

> 🔗 **Back to main README**: README.md  
> 🧭 **Beginner’s full guide**: USAGE.md




ai-career-coach/
├── data/                 # Raw and processed data
│   ├── raw/              # Original datasets (e.g., ai_job_dataset.csv, resume_data.csv) - Not committed if large/sensitive
│   └── processed/        # Cleaned and feature-engineered data (e.g., jobs_clean.csv, resumes_clean.csv, features.csv)
├── models/               # Trained model artifacts (e.g., model.joblib)
├── src/                  # Source code
│   ├── api/              # FastAPI application (main.py)
│   ├── data/             # Data processing scripts (make_dataset.py)
│   ├── features/         # Feature engineering scripts (build_features.py)
│   └── models/           # Model training scripts (train_model.py)
├── tests/                # Unit and integration tests (if added)
├── .dockerignore         # Files and directories to ignore in Docker builds
├── .gitignore            # Files and directories to ignore in Git
├── Dockerfile            # Instructions for Docker
├── LICENSE               # Project license
├── Makefile              # Common development commands (optional)
├── README.md             # Project overview and usage
├── DEVELOPMENT.md        # This file
├── USAGE.md              # User guide for non-technical users
└── requirements.txt      # Python dependencies