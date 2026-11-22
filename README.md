# PDF Q&A with RAG (Ollama + Python + React)

Ask questions about `abhishek_resume.pdf` — answers come only from the PDF.

```
poc-pdf-rag/
├── abhishek_resume.pdf
├── backend/          Python — reads the PDF, does RAG, talks to Ollama
│   ├── rag.py        the RAG logic (chunk → embed → retrieve → answer)  ← start reading here
│   ├── main.py       the web API (/pdf and /ask)
│   └── requirements.txt
└── frontend/         React — PDF on the left, chat on the right
    └── src/App.jsx
```

## How it works (RAG in 4 steps)
1. **Chunk** – split the PDF text into ~500-character pieces.
2. **Embed** – `nomic-embed-text` turns each piece into a vector of numbers (done once at startup).
3. **Retrieve** – embed the question, pick the 4 most similar pieces (cosine similarity).
4. **Generate** – send those pieces + the question to `llama3.1:8b`, told to answer only from them.

## Run it (two terminals)

Make sure Ollama is running, and you have the models: `ollama pull llama3.1:8b` and `ollama pull nomic-embed-text`.

**Terminal 1 – backend**
```powershell
cd backend
python -m venv .venv                     # one time
.\.venv\Scripts\pip install -r requirements.txt   # one time
.\.venv\Scripts\uvicorn main:app --reload --port 8000
```

**Terminal 2 – frontend**
```powershell
cd frontend
npm install        # one time
npm run dev
```

Open http://localhost:5173

Tip: `python rag.py` (inside backend, using the venv) tests the RAG part alone, no UI needed.
