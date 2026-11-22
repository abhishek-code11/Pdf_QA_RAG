"""
main.py — the web server (API) the React frontend talks to.

It exposes just two URLs:
    GET  /pdf  -> sends the PDF file so the browser can display it on the left side
    POST /ask  -> receives {"question": "..."} and returns {"answer": "...", "sources": [...]}

Start it with:   uvicorn main:app --reload --port 8000
Then open:       http://localhost:8000/docs   (FastAPI gives you a free test page there)
"""

from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

import rag  # our own file: rag.py

app = FastAPI(title="PDF RAG")

# Build the index ONCE when the server starts (reading + embedding the PDF takes a few seconds).
# Every question afterwards reuses it, so answers are faster.
index = rag.build_index()


class Question(BaseModel):
    """Shape of the JSON body the frontend sends. min_length=1 rejects empty questions automatically."""
    question: str = Field(min_length=1)


@app.get("/pdf")
def get_pdf():
    # No `filename=` on purpose: that would make the browser download the file instead of showing it.
    return FileResponse(rag.PDF_PATH, media_type="application/pdf")


@app.post("/ask")
def ask(body: Question):
    # FastAPI already turned the incoming JSON into a `Question` object for us.
    return rag.answer(body.question, index)
