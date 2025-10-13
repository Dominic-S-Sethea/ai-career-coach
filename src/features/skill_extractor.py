pip install spacy
from skillner import SkillExtractor  # ✅ Correct
python -m spacy download en_core_web_sm

# Load spaCy model (already downloaded in Step 2)
nlp = spacy.load("en_core_web_sm")
skillner = Skillner(nlp, debug=False)


def extract_skills(text: str) -> list:
    """
    Extract hard skills from raw text using skillner.
    Returns a list of unique skills (strings).
    """
    if not isinstance(text, str) or not text.strip():
        return []
    try:
        annotations = skillner.annotate(text)
        skills = [ann["doc"] for ann in annotations if ann["type"] == "hard skill"]
        return list(set(skills))  # Remove duplicates
    except Exception as e:
        print(f"Skill extraction error: {e}")
        return []
