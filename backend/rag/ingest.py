from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

# Two separate indexes
kb_documents = []
kb_index = None

resume_documents = []
resume_index = None


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
    return chunks


def index_knowledge_base(text: str):
    global kb_documents, kb_index

    chunks = chunk_text(text, chunk_size=500, overlap=50)
    kb_documents.extend(chunks)

    embeddings = model.encode(kb_documents)
    dim = embeddings.shape[1]
    kb_index = faiss.IndexFlatL2(dim)
    kb_index.add(np.array(embeddings))
    print(f"[RAG] Knowledge base indexed: {len(kb_documents)} chunks")


def index_resume(text: str):
    global resume_documents, resume_index

    chunks = chunk_text(text, chunk_size=300, overlap=30)
    resume_documents = chunks

    embeddings = model.encode(resume_documents)
    dim = embeddings.shape[1]
    resume_index = faiss.IndexFlatL2(dim)
    resume_index.add(np.array(embeddings))
    print(f"[RAG] Resume indexed: {len(resume_documents)} chunks")