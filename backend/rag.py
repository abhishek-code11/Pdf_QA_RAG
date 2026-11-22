"""
rag.py — the RAG ("Retrieval-Augmented Generation") logic.

What is RAG, in plain words?
    An LLM doesn't know what's inside YOUR PDF. So before asking it a question we:
      1. RETRIEVE: find the few pieces of the PDF that are most related to the question.
      2. AUGMENT:  paste those pieces into the prompt as "context".
      3. GENERATE: ask the LLM to answer using ONLY that context.

How do we "find related pieces"? With EMBEDDINGS:
    An embedding model turns text into a list of numbers (a vector) that captures its meaning.
    Texts with similar meaning get vectors that point in a similar direction.
    So we embed every PDF chunk once, embed the question, and pick the chunks whose
    vectors are closest to the question's vector (cosine similarity).

Run this file directly (`python rag.py`) to test it without the web server.
"""

import math
from pathlib import Path

import ollama  # Python client that talks to the local Ollama app (http://localhost:11434)
from pypdf import PdfReader  # reads text out of PDF files

# ---------------------------------------------------------------------------
# Settings — change these to experiment
# ---------------------------------------------------------------------------

# The PDF lives one folder up from this file (project root).
PDF_PATH = Path(__file__).resolve().parent.parent / "abhishek_resume.pdf"

EMBED_MODEL = "nomic-embed-text"  # small model that turns text -> vector
CHAT_MODEL = "llama3.1:8b"        # the LLM that writes the final answer

CHUNK_SIZE = 500     # characters per chunk. Small = precise, large = more context per chunk.
CHUNK_OVERLAP = 100  # chunks share this many characters so a sentence cut in half isn't lost.
TOP_K = 4            # how many best-matching chunks we send to the LLM.


# ---------------------------------------------------------------------------
# Step 1: read the PDF and cut it into chunks
# ---------------------------------------------------------------------------

def load_pdf_text(path: Path) -> str:
    """Return all the text from every page of the PDF, joined together."""
    reader = PdfReader(path)
    # extract_text() can return None for image-only pages, hence `or ""`.
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def split_into_chunks(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """
    Cut a long text into overlapping pieces.

    Example with size=10, overlap=3:
        "abcdefghijklmnop" -> ["abcdefghij", "hijklmnop"]
                                     ^^^ these 3 letters appear in both chunks
    """
    text = " ".join(text.split())  # squash newlines / repeated spaces into single spaces
    step = size - overlap          # how far we move forward each time
    chunks = []
    for start in range(0, len(text), step):
        chunks.append(text[start:start + size])
        if start + size >= len(text):  # this chunk already reached the end — stop
            break
    return chunks


# ---------------------------------------------------------------------------
# Step 2: embeddings + similarity
# ---------------------------------------------------------------------------

def embed(texts: list[str]) -> list[list[float]]:
    """Ask Ollama to turn each text into a vector (a list of floats)."""
    return ollama.embed(model=EMBED_MODEL, input=texts)["embeddings"]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """
    How similar are two vectors? 1.0 = same direction (same meaning), 0 = unrelated.
    Formula: (a · b) / (|a| * |b|)
    """
    dot = sum(x * y for x, y in zip(a, b))
    length_a = math.sqrt(sum(x * x for x in a))
    length_b = math.sqrt(sum(y * y for y in b))
    return dot / (length_a * length_b)


def build_index() -> list[tuple[str, list[float]]]:
    """
    Do the slow work ONCE at startup: read PDF -> chunk -> embed every chunk.
    Returns a list of (chunk_text, chunk_vector) pairs. This list is our tiny "vector database".
    """
    # ponytail: in-memory list + linear scan. Fine for one PDF; use a vector DB (Chroma, FAISS) for thousands of docs.
    chunks = split_into_chunks(load_pdf_text(PDF_PATH))
    vectors = embed(chunks)
    print(f"Indexed {len(chunks)} chunks from {PDF_PATH.name}")
    return list(zip(chunks, vectors))


# ---------------------------------------------------------------------------
# Step 3: answer a question (Retrieve -> Augment -> Generate)
# ---------------------------------------------------------------------------

def answer(question: str, index: list[tuple[str, list[float]]]) -> dict:
    # RETRIEVE: embed the question and score every chunk against it.
    question_vector = embed([question])[0]
    scored = [(cosine_similarity(question_vector, vector), chunk) for chunk, vector in index]
    scored.sort(reverse=True)                       # highest similarity first
    top_chunks = [chunk for _, chunk in scored[:TOP_K]]

    # The first chunk is the document's header (name, contact, title). Questions like "whose resume is this?"
    # don't *sound* similar to a block of contact details, so similarity search can miss it. Always include it.
    # ponytail: header heuristic fits resumes/papers; for long multi-section docs, try hybrid (keyword + vector) search.
    header = index[0][0]
    if header not in top_chunks:
        top_chunks.insert(0, header)

    # AUGMENT: put the retrieved chunks into the prompt.
    context = "\n\n---\n\n".join(top_chunks)
    system_prompt = (
        "You answer questions about a PDF document. "
        "Use ONLY the context below. If the answer is not in the context, say: "
        "\"I couldn't find that in the PDF.\" Keep answers short and clear.\n\n"
        f"CONTEXT:\n{context}"
    )

    # GENERATE: let the LLM write the answer.
    response = ollama.chat(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
    )

    # We also return the chunks we used ("sources") so the UI can show WHERE the answer came from.
    return {"answer": response["message"]["content"], "sources": top_chunks}


# ---------------------------------------------------------------------------
# Quick self-test: `python rag.py`
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # 1) Chunking works without Ollama — check it first.
    assert split_into_chunks("abcdefghijklmnop", size=10, overlap=3) == ["abcdefghij", "hijklmnop"]
    assert split_into_chunks("short", size=10, overlap=3) == ["short"]
    print("Chunking OK")

    # 2) Full pipeline (needs Ollama running).
    idx = build_index()
    result = answer("What are the main skills mentioned?", idx)
    print("\nANSWER:\n", result["answer"])
