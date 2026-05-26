import requests
import random


def generate_question(role: str, skills: str, context: str) -> str:
    skill_list = [s.strip() for s in skills.split(",") if s.strip()]
    focused = ", ".join(random.sample(skill_list, min(2, len(skill_list))))

    prompt = f"""You are a strict technical interviewer.

Role: {role}
Candidate Skills (focus on these): {focused}

Knowledge Base Context:
{context[:800]}

Rules:
- Output ONLY the question itself, nothing else
- One clear focused question
- No greetings, no preamble, no numbering
- Must end with a question mark
- Max 1 sentence
- Test only the focus skills above

Question:"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.7, "num_predict": 80}
        }
    )

    raw = response.json()["response"].strip()
    lines = [l.strip() for l in raw.split("\n") if l.strip()]
    for line in lines:
        if line.endswith("?") and len(line) < 200:
            return line
    return lines[0] if lines else "Could not generate question."


def analyze_answer(question: str, answer: str, role: str) -> dict:
    prompt = f"""You are a strict technical interview evaluator.

Role: {role}
Question: {question}
Candidate Answer: {answer}

Respond in this exact format, nothing else:
Score: <1-10>
Quality: <Poor / Average / Good / Excellent>
Feedback: <one honest sentence>
Missing: <key concept missed or None>"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.3, "num_predict": 120}
        }
    )

    raw = response.json()["response"].strip()
    result = {"score": 0, "quality": "N/A", "feedback": raw, "missing": "N/A"}

    for line in raw.split("\n"):
        if line.startswith("Score:"):
            try:
                result["score"] = int(line.split(":")[1].strip().split("/")[0])
            except:
                pass
        elif line.startswith("Quality:"):
            result["quality"] = line.split(":", 1)[1].strip()
        elif line.startswith("Feedback:"):
            result["feedback"] = line.split(":", 1)[1].strip()
        elif line.startswith("Missing:"):
            result["missing"] = line.split(":", 1)[1].strip()

    return result