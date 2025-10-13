# 🧭 AI Career Coach: Beginner's Guide

> **No coding experience? No problem!**  
> This guide walks you through using the AI Career Coach **step by step**, even if you’ve never used Python, Git, or APIs before.

---

## 🎯 What This Tool Does

The AI Career Coach helps **job seekers**:
- Predict how well their resume matches a job description (0–100%)
- See **missing skills** (e.g., “You’re missing: AWS, Docker”)
- Get **actionable advice** (e.g., “Add ‘MLOps’—it appears in 89% of similar roles”)

---

## 🚀 Use the Live Demo

You don’t need to install anything. Just follow these easy steps:

Open this link in your web browser:

👉 https://ai-career-coach-zwr6.onrender.com

⚠️ Note: The page may look blank — that’s normal! This is an “API” (a behind-the-scenes tool), not a regular website. 

To test it, use a free, beginner-friendly tool called Postman:
Go to https://www.postman.com/

Click “Download Postman” and install it (it’s free and safe)
Open Postman and click “+ New” → “HTTP Request”

Fill in:
Method: POST
URL: https://ai-career-coach-zwr6.onrender.com/match

Click the “Body” tab → choose “raw” → select “JSON” from the dropdown
Paste this into the box:

{
  "resume": "Experienced in Python, SQL, and Scikit-learn.",
  "job": "We seek AWS, Spark, and MLOps experience."
}


Click the blue “Send” button

You’ll instantly see your result!

It will show:
1. How well your resume matches the job (0–100%)
2. What skills you’re missing
3. Actionable advice to improve