[ai_interview_system_icons.html](https://github.com/user-attachments/files/28253792/ai_interview_system_icons.html)# AI-Powered Role-Based Interview System

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

[Uploading ai_interview_system_
<h2 class="sr-only">AI Interview System architecture with icons showing frontend, backend, RAG pipeline, and storage layers</h2>
<style>
.layer { display:flex; gap:12px; margin-bottom:10px; align-items:stretch; }
.layer-label { writing-mode:vertical-rl; text-orientation:mixed; transform:rotate(180deg); font-size:11px; color:var(--color-text-tertiary); min-width:18px; display:flex; align-items:center; justify-content:center; letter-spacing:1px; }
.layer-cards { display:flex; gap:10px; flex:1; }
.card { flex:1; border-radius:var(--border-radius-lg); padding:14px 12px; display:flex; flex-direction:column; align-items:center; gap:6px; cursor:pointer; transition:opacity .15s; border:0.5px solid; }
.card:hover { opacity:.8; }
.card i { font-size:22px; }
.card-title { font-size:13px; font-weight:500; text-align:center; }
.card-sub { font-size:11px; text-align:center; opacity:.75; }
.purple { background:#EEEDFE; border-color:#534AB7; color:#3C3489; }
.teal   { background:#E1F5EE; border-color:#0F6E56; color:#085041; }
.amber  { background:#FAEEDA; border-color:#854F0B; color:#633806; }
.gray   { background:#F1EFE8; border-color:#5F5E5A; color:#444441; }
.coral  { background:#FAECE7; border-color:#993C1D; color:#712B13; }
.divider { border:none; border-top:0.5px dashed var(--color-border-tertiary); margin:4px 0; }
.arr-row { display:flex; justify-content:center; align-items:center; gap:8px; margin:2px 0; color:var(--color-text-tertiary); font-size:11px; }
@media (prefers-color-scheme: dark) {
  .purple { background:#3C3489; border-color:#AFA9EC; color:#CECBF6; }
  .teal   { background:#085041; border-color:#5DCAA5; color:#9FE1CB; }
  .amber  { background:#633806; border-color:#EF9F27; color:#FAC775; }
  .gray   { background:#444441; border-color:#B4B2A9; color:#D3D1C7; }
  .coral  { background:#712B13; border-color:#F0997B; color:#F5C4B3; }
}
</style>

<div style="padding:4px 0 8px">

  <div class="layer">
    <div class="layer-label">frontend</div>
    <div class="layer-cards">
      <div class="card purple" onclick="sendPrompt('How does the UploadResume component work?')">
        <i class="ti ti-upload" aria-hidden="true"></i>
        <div class="card-title">Upload resume</div>
        <div class="card-sub">PDF → backend</div>
      </div>
      <div class="card purple" onclick="sendPrompt('How does role selection work?')">
        <i class="ti ti-briefcase" aria-hidden="true"></i>
        <div class="card-title">Role select</div>
        <div class="card-sub">Pick target role</div>
      </div>
      <div class="card purple" onclick="sendPrompt('How does the Interview component work?')">
        <i class="ti ti-message-2" aria-hidden="true"></i>
        <div class="card-title">Interview</div>
        <div class="card-sub">Q&A interface</div>
      </div>
      <div class="card purple" onclick="sendPrompt('How does the Summary component work?')">
        <i class="ti ti-chart-bar" aria-hidden="true"></i>
        <div class="card-title">Summary</div>
        <div class="card-sub">Scores & feedback</div>
      </div>
    </div>
  </div>

  <div class="arr-row">
    <i class="ti ti-arrow-down" aria-hidden="true"></i>
    <span>Axios / REST API</span>
    <i class="ti ti-arrow-down" aria-hidden="true"></i>
  </div>

  <hr class="divider"/>

  <div class="layer">
    <div class="layer-label">backend</div>
    <div class="layer-cards">
      <div class="card teal" onclick="sendPrompt('What endpoints does FastAPI expose?')">
        <i class="ti ti-api" aria-hidden="true"></i>
        <div class="card-title">FastAPI</div>
        <div class="card-sub">/upload /start /question /answer /summary</div>
      </div>
      <div class="card teal" onclick="sendPrompt('How does skill extraction work?')">
        <i class="ti ti-tags" aria-hidden="true"></i>
        <div class="card-title">Skills extractor</div>
        <div class="card-sub">Regex → skills list</div>
      </div>
      <div class="card teal" onclick="sendPrompt('How does session management work?')">
        <i class="ti ti-id" aria-hidden="true"></i>
        <div class="card-title">Session mgmt</div>
        <div class="card-sub">UUID per user</div>
      </div>
      <div class="card teal" onclick="sendPrompt('How does PDF parsing work?')">
        <i class="ti ti-file-text" aria-hidden="true"></i>
        <div class="card-title">PDF parser</div>
        <div class="card-sub">PyMuPDF → text</div>
      </div>
    </div>
  </div>

  <div class="arr-row">
    <i class="ti ti-arrow-down" aria-hidden="true"></i>
    <span>RAG pipeline</span>
    <i class="ti ti-arrow-down" aria-hidden="true"></i>
  </div>

  <hr class="divider"/>

  <div class="layer">
    <div class="layer-label">RAG</div>
    <div class="layer-cards">
      <div class="card amber" onclick="sendPrompt('How does document chunking work?')">
        <i class="ti ti-cut" aria-hidden="true"></i>
        <div class="card-title">Ingest</div>
        <div class="card-sub">500-word chunks, 50 overlap</div>
      </div>
      <div class="card amber" onclick="sendPrompt('How does vector retrieval work?')">
        <i class="ti ti-vector" aria-hidden="true"></i>
        <div class="card-title">Retrieve</div>
        <div class="card-sub">FAISS L2, top-3 chunks</div>
      </div>
      <div class="card amber" onclick="sendPrompt('How does question generation work?')">
        <i class="ti ti-brain" aria-hidden="true"></i>
        <div class="card-title">Generate</div>
        <div class="card-sub">LLaMA 3, 2-skill focus</div>
      </div>
      <div class="card amber" onclick="sendPrompt('How are answers evaluated?')">
        <i class="ti ti-star" aria-hidden="true"></i>
        <div class="card-title">Evaluate</div>
        <div class="card-sub">Score + feedback</div>
      </div>
    </div>
  </div>

  <div class="arr-row">
    <i class="ti ti-arrow-down" aria-hidden="true"></i>
    <span>Persist</span>
    <i class="ti ti-arrow-down" aria-hidden="true"></i>
  </div>

  <hr class="divider"/>

  <div class="layer">
    <div class="layer-label">storage</div>
    <div class="layer-cards">
      <div class="card gray" onclick="sendPrompt('What tables are in the SQLite database?')">
        <i class="ti ti-database" aria-hidden="true"></i>
        <div class="card-title">SQLite</div>
        <div class="card-sub">sessions · questions · answers</div>
      </div>
      <div class="card gray" onclick="sendPrompt('How does FAISS store embeddings?')">
        <i class="ti ti-topology-star" aria-hidden="true"></i>
        <div class="card-title">FAISS index</div>
        <div class="card-sub">KB + resume vectors</div>
      </div>
      <div class="card coral" onclick="sendPrompt('How does Ollama run LLaMA 3 locally?')">
        <i class="ti ti-cpu" aria-hidden="true"></i>
        <div class="card-title">Ollama</div>
        <div class="card-sub">LLaMA 3 local LLM</div>
      </div>
    </div>
  </div>

</div>
icons.html…]()
