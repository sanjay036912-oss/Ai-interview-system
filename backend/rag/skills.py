import re

def extract_skills(text: str):
    skills_list = [
        "python", "java", "c++", "fastapi", "django", "flask",
        "machine learning", "deep learning", "nlp",
        "sql", "mongodb", "docker", "kubernetes",
        "aws", "git", "linux", "react", "pytorch", "tensorflow"
    ]

    text_lower = text.lower()

    found = set()

    for skill in skills_list:
        # match whole words (handles commas, dots, etc.)
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, text_lower):
            found.add(skill)

    return ", ".join(sorted(found))