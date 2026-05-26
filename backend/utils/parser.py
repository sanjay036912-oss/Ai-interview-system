import re
from typing import List
import fitz  # PyMuPDF


# -------------------------------
# 📄 Extract text from PDF
# -------------------------------
def extract_text(file) -> str:
    text = ""

    try:
        pdf_bytes = file.file.read()   # ✅ FIX HERE
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")

        for page in doc:
            text += page.get_text()

    except Exception as e:
        print(f"Error reading PDF: {e}")

    return text


# -------------------------------
# 🧠 Simple Skill Extraction
# -------------------------------
SKILL_KEYWORDS = [
    # Programming
    "python", "java", "c++", "javascript", "typescript",

    # Web / Backend
    "fastapi", "flask", "django", "node", "express",

    # Data / ML
    "machine learning", "deep learning", "nlp",
    "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch",

    # Databases
    "sql", "mysql", "postgresql", "mongodb",

    # Tools
    "docker", "kubernetes", "git", "aws", "azure"
]


def extract_skills(text: str) -> List[str]:
    text = text.lower()
    found_skills = []

    for skill in SKILL_KEYWORDS:
        if re.search(rf"\b{re.escape(skill)}\b", text):
            found_skills.append(skill)

    return list(set(found_skills))