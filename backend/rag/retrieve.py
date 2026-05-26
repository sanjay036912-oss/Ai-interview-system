from rag.ingest import kb_index, kb_documents, model
import numpy as np


def retrieve_from_kb(query: str, top_k: int = 3) -> str:
    if kb_index is None or len(kb_documents) == 0:
        return "No knowledge base loaded."

    query_vector = model.encode([query])
    distances, indices = kb_index.search(np.array(query_vector), top_k)

    results = [kb_documents[i] for i in indices[0] if i < len(kb_documents)]
    return "\n\n".join(results)