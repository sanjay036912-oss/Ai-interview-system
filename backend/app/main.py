from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uuid

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import init_db, get_connection
from rag.ingest import index_knowledge_base, index_resume
from rag.retrieve import retrieve_from_kb
from rag.skills import extract_skills
from rag.generate import generate_question, analyze_answer
from utils.parser import extract_text

# ----------------------------
# KNOWLEDGE BASE (Backend Engineer role)
# Edit this with actual book content or load from file
# ----------------------------
BACKEND_KB = """
APIs are application programming interfaces that allow systems to communicate.
REST APIs use HTTP methods: GET POST PUT DELETE PATCH.
A GET request retrieves data. POST creates. PUT updates. DELETE removes.
Stateless architecture means each request contains all necessary information.
Scalability is a system's ability to handle increased load.
Horizontal scaling adds more machines. Vertical scaling adds more power to one machine.
Load balancers distribute traffic across multiple servers.
Databases store structured data. SQL databases use tables and relationships.
PostgreSQL MySQL are popular relational databases.
Indexes improve query performance by allowing faster lookups.
Normalization reduces data redundancy in relational databases.
Docker containers package applications with all dependencies.
A Dockerfile defines how to build a container image.
Docker Compose manages multi-container applications.
Kubernetes orchestrates containers at scale.
A pod is the smallest deployable unit in Kubernetes.
CI/CD pipelines automate testing and deployment.
GitHub Actions is a popular CI/CD tool.
Environment variables store configuration outside code.
Authentication verifies identity. Authorization controls access.
JWT tokens are used for stateless authentication.
OAuth2 is a standard for delegated authorization.
Rate limiting protects APIs from abuse.
Caching improves performance by storing frequently accessed data.
Redis is an in-memory cache and message broker.
Message queues decouple services. RabbitMQ and Kafka are popular choices.
Microservices architecture splits applications into small independent services.
Monolithic architecture keeps all code in one deployable unit.
HTTP status codes: 200 OK, 201 Created, 400 Bad Request, 401 Unauthorized,
403 Forbidden, 404 Not Found, 500 Internal Server Error.
Async programming allows non-blocking I/O operations.
FastAPI is a modern Python web framework with async support.
Connection pooling reuses database connections for efficiency.
"""

AIML_KB = """
Machine learning is a subset of AI where systems learn from data.
Supervised learning uses labeled training data.
Unsupervised learning finds patterns in unlabeled data.
Reinforcement learning learns through rewards and penalties.
A neural network consists of layers of interconnected nodes.
Deep learning uses neural networks with many layers.
Overfitting occurs when a model memorizes training data but fails on new data.
Underfitting occurs when a model is too simple to capture patterns.
Regularization techniques like L1 L2 dropout prevent overfitting.
Train test split divides data for training and evaluation.
Cross validation provides more robust model evaluation.
Gradient descent optimizes model parameters by minimizing loss.
Learning rate controls how much parameters are updated each step.
Backpropagation computes gradients for neural network training.
Convolutional neural networks are used for image processing.
Recurrent neural networks handle sequential data like text.
Transformers use attention mechanisms for NLP tasks.
BERT and GPT are popular transformer-based language models.
Embeddings are dense vector representations of data.
Retrieval Augmented Generation combines retrieval with language generation.
Vector databases store embeddings for similarity search.
FAISS is a library for efficient similarity search.
Precision and recall measure classification model performance.
F1 score balances precision and recall.
Feature engineering creates meaningful inputs for models.
"""

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB
    init_db()
    # Load knowledge bases
    index_knowledge_base(BACKEND_KB + AIML_KB)
    print("[Startup] DB and knowledge base ready")
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------
# ROOT
# ----------------------------
@app.get("/")
def root():
    return {"message": "AI Interview System Running"}


# ----------------------------
# UPLOAD RESUME
# ----------------------------
@app.post("/upload")
def upload_resume(file: UploadFile = File(...)):
    text = extract_text(file)
    index_resume(text)
    skills = extract_skills(text)
    return {"message": "Resume processed", "skills": skills}


# ----------------------------
# START SESSION
# ----------------------------
@app.post("/start")
def start_interview(role: str, skills: str = ""):
    session_id = str(uuid.uuid4())

    conn = get_connection()
    conn.execute(
        "INSERT INTO sessions (id, role, skills) VALUES (?, ?, ?)",
        (session_id, role, skills)
    )
    conn.commit()
    conn.close()

    return {"session_id": session_id}


# ----------------------------
# GET QUESTION
# ----------------------------
@app.get("/question")
def get_question(session_id: str):
    conn = get_connection()
    session = conn.execute(
        "SELECT * FROM sessions WHERE id = ?", (session_id,)
    ).fetchone()

    if not session:
        conn.close()
        return {"error": "Invalid session_id"}

    role = session["role"]
    skills = session["skills"] or "python, backend, api"

    # Retrieve from knowledge base
    query = f"{role} {skills}"
    context = retrieve_from_kb(query)

    # Generate question
    question = generate_question(role, skills, context)

    # Store question with context
    cursor = conn.execute(
        "INSERT INTO questions (session_id, question, context_used) VALUES (?, ?, ?)",
        (session_id, question, context[:300])
    )
    question_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return {"question": question, "question_id": question_id}


# ----------------------------
# SUBMIT ANSWER
# ----------------------------
@app.post("/answer")
def submit_answer(session_id: str, answer: str, question_id: int = 0):
    conn = get_connection()
    session = conn.execute(
        "SELECT * FROM sessions WHERE id = ?", (session_id,)
    ).fetchone()

    if not session:
        conn.close()
        return {"error": "Invalid session_id"}

    # Get latest question if no question_id provided
    if question_id == 0:
        row = conn.execute(
            "SELECT id FROM questions WHERE session_id = ? ORDER BY id DESC LIMIT 1",
            (session_id,)
        ).fetchone()
        question_id = row["id"] if row else 0

    conn.execute(
        "INSERT INTO answers (session_id, question_id, answer) VALUES (?, ?, ?)",
        (session_id, question_id, answer)
    )
    conn.commit()
    conn.close()

    return {"message": "Answer recorded"}


# ----------------------------
# SUMMARY
# ----------------------------
@app.get("/summary")
def get_summary(session_id: str):
    conn = get_connection()

    session = conn.execute(
        "SELECT * FROM sessions WHERE id = ?", (session_id,)
    ).fetchone()

    if not session:
        conn.close()
        return {"error": "Invalid session_id"}

    questions = conn.execute(
        "SELECT * FROM questions WHERE session_id = ? ORDER BY id ASC",
        (session_id,)
    ).fetchall()

    answers = conn.execute(
        "SELECT * FROM answers WHERE session_id = ? ORDER BY id ASC",
        (session_id,)
    ).fetchall()

    conn.close()

    role = session["role"]
    answer_map = {a["question_id"]: a["answer"] for a in answers}

    breakdown = []
    for q in questions:
        answer = answer_map.get(q["id"], "No answer given")
        analysis = analyze_answer(q["question"], answer, role)
        breakdown.append({
            "question": q["question"],
            "answer": answer,
            "score": analysis["score"],
            "quality": analysis["quality"],
            "feedback": analysis["feedback"],
            "missing_concept": analysis["missing"]
        })

    scores = [b["score"] for b in breakdown if b["score"] > 0]
    avg = round(sum(scores) / len(scores), 1) if scores else 0

    return {
        "role": role,
        "total_questions": len(questions),
        "answered": len(answers),
        "average_score": avg,
        "overall_rating": (
            "Excellent" if avg >= 8 else
            "Good" if avg >= 6 else
            "Average" if avg >= 4 else
            "Needs Improvement"
        ),
        "breakdown": breakdown
    }