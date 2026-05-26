# AI-Powered Role-Based Interview System

An intelligent technical interview platform that dynamically generates questions based on a candidate's resume, selected job role, and a role-specific knowledge base using Retrieval-Augmented Generation (RAG).

---

## System Architecture

```
ai-interview-system/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app, routes, lifecycle
│   │   └── database.py      # SQLite connection and schema
│   ├── rag/
│   │   ├── ingest.py        # Document chunking and FAISS indexing
│   │   ├── retrieve.py      # Vector similarity search
│   │   ├── generate.py      # LLM question generation and answer analysis
│   │   └── skills.py        # Resume skill extraction
│   ├── utils/
│   │   └── parser.py        # PDF text extraction
│   ├── requirements.txt
│   └── .env
└── frontend/
    └── src/
        ├── components/
        │   ├── UploadResume.jsx   # Step 1 - Resume upload
        │   ├── RoleSelect.jsx     # Step 2 - Role selection
        │   ├── Interview.jsx      # Step 3 - Q&A interface
        │   └── Summary.jsx        # Step 4 - Results and analysis
        ├── api/
        │   └── client.js          # Axios API client
        └── App.jsx                # Main flow controller
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React + Vite |
| Backend | FastAPI (Python) |
| LLM | LLaMA 3 via Ollama (local) |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| Vector Search | FAISS |
| Database | SQLite |
| PDF Parsing | PyMuPDF |

---

## Key Design Decisions

### RAG Pipeline
- **Two separate FAISS indexes** — one for the knowledge base (ML/backend concepts), one for the resume
- **Chunking strategy** — 500-word chunks with 50-word overlap for context preservation
- **Dynamic query construction** — role + extracted skills used as the retrieval query
- Knowledge base is loaded once at startup; resume is indexed per upload

### Question Generation
- Focused on 1–2 skills per question to avoid compound questions
- Temperature set to 0.7 for variety, `num_predict` capped at 80 tokens
- Prompt enforces single-sentence questions ending with `?`

### Database
- SQLite for zero-configuration persistence
- Auto-created on first startup as `interview.db`
- Three tables: `sessions`, `questions`, `answers`
- Questions store the context chunk used to generate them (full traceability)

### Session Management
- Each session scoped by UUID stored in SQLite
- Skills stored per session — no global state
- Answer analysis runs at summary time using the same LLM

---

## Setup Instructions

### Prerequisites
- Python 3.11+
- Node.js 18+
- [Ollama](https://ollama.com) installed

### 1. Clone the repository
```bash
git clone https://github.com/sanjay036912-oss/Ai-interview-system.git
cd Ai-interview-system
```

### 2. Backend setup
```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure environment
Create a `.env` file in `backend/`:
```env
DB_PATH=interview.db
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3
APP_ENV=development
APP_PORT=8000
```

### 4. Set up Ollama
```bash
# Install from https://ollama.com, then:
ollama pull llama3
ollama serve
```

### 5. Start the backend
```bash
cd backend
uvicorn app.main:app --reload
```
Backend runs at `http://localhost:8000`

> SQLite database `interview.db` is created automatically on first startup. No database setup needed.

### 6. Frontend setup
```bash
cd frontend
npm install
npm run dev
```
Frontend runs at `http://localhost:5173`

---

## System Flow

```
Candidate uploads resume (PDF)
        ↓
Resume parsed → skills extracted → resume indexed in FAISS
        ↓
Candidate selects role → session created in SQLite
        ↓
Role + skills → query knowledge base (FAISS) → retrieve relevant chunks
        ↓
Retrieved context + skills → LLaMA 3 → generate focused question
        ↓
Question stored in SQLite → displayed to candidate
        ↓
Candidate answers → answer stored in SQLite
        ↓
Repeat for 5 questions
        ↓
Summary: LLM evaluates each answer → score + feedback + missing concepts
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/upload` | Upload and process resume PDF |
| POST | `/start` | Create a new interview session |
| GET | `/question` | Generate and retrieve next question |
| POST | `/answer` | Submit answer for current question |
| GET | `/summary` | Get full session analysis with scores |

---

## Database Schema

```sql
-- Stores each interview session
CREATE TABLE sessions (
    id TEXT PRIMARY KEY,
    role TEXT NOT NULL,
    skills TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Stores generated questions with context traceability
CREATE TABLE questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    question TEXT NOT NULL,
    context_used TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Stores candidate answers
CREATE TABLE answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    question_id INTEGER NOT NULL,
    answer TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Features

- Resume-aware question generation (skills influence topic and difficulty)
- RAG pipeline with FAISS vector search and chunked knowledge base
- Per-answer scoring (1–10) with qualitative feedback and missing concept detection
- Session persistence in SQLite — survives server restarts
- Clean 4-step UI: Upload → Role → Interview → Summary
- Modular backend with clear separation of concerns
- All configuration via environment variables

## Architecture

<img width="788" height="556" alt="Screenshot 2026-05-26 133637" src="https://github.com/user-attachments/assets/a82f60f6-7687-4cc2-bd39-bbbb6ec6be81" />

