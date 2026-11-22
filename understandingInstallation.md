# Understanding the Installation

This page explains **which tools this project uses, why, and how to install them**.
If everything is already installed, just double-click **`start.bat`**.

---

## 1. The big picture

```
 Browser (http://localhost:5173)
   │   PDF on the left, chat on the right
   ▼
 FRONTEND  – React app, run by Vite (Node.js)          frontend/
   │   forwards /pdf and /ask to the backend
   ▼
 BACKEND   – Python API, run by FastAPI + Uvicorn     backend/
   │   reads the PDF, finds the relevant parts (RAG)
   ▼
 OLLAMA    – runs the AI models on your own computer   (localhost:11434)
     • nomic-embed-text  → turns text into numbers (embeddings)
     • llama3.1:8b       → writes the answer
```

Everything runs **on your machine**. No internet or API key is needed once it's installed.

---

## 2. Tools you install yourself (one time)

| Tool | What it is | Why we need it | Download |
|------|-----------|----------------|----------|
| **Python** (3.10 or newer) | Programming language | Runs the backend (`backend/`) | https://www.python.org/downloads/ — tick **"Add Python to PATH"** during install |
| **Node.js** (18 or newer) | Runs JavaScript outside the browser; comes with `npm` | Runs the React dev server (`frontend/`) | https://nodejs.org (LTS version) |
| **Ollama** | App that runs AI models locally | Our LLM + embedding model | https://ollama.com/download |

Check they're installed by opening a terminal (PowerShell) and running:

```powershell
python --version
node --version
npm --version
ollama --version
```

Each should print a version number. If one says "not recognized", install it (or reopen the terminal after installing).

### Download the two AI models (one time, ~5 GB)

```powershell
ollama pull llama3.1:8b
ollama pull nomic-embed-text
```

Check with `ollama list`. Both names should appear.

---

## 3. Packages installed automatically

You don't install these by hand: **`start.bat` installs them on the first run.**

### Python packages (listed in `backend/requirements.txt`)

| Package | What it does in this project |
|---------|------------------------------|
| `fastapi` | Creates the web API: the `/pdf` and `/ask` URLs in `main.py` |
| `uvicorn` | The server program that actually runs the FastAPI app |
| `pypdf` | Reads the text out of the PDF (`load_pdf_text` in `rag.py`) |
| `ollama` | Python client for talking to Ollama (`ollama.embed`, `ollama.chat` in `rag.py`) |

They're installed into a **virtual environment** (`backend/.venv`): a private folder of packages
just for this project, so it never conflicts with other Python projects on your PC.

### JavaScript packages (listed in `frontend/package.json`)

| Package | What it does in this project |
|---------|------------------------------|
| `react`, `react-dom` | The UI library: builds the chat screen in `App.jsx` |
| `vite` | Dev server: serves the React app and forwards `/pdf`, `/ask` to Python (`vite.config.js`) |
| `@vitejs/plugin-react` | Lets Vite understand React's JSX syntax |

These are installed into `frontend/node_modules`.

---

## 4. Running the app

### Easy way
Double-click **`start.bat`** in the project folder. It will:
1. Check Python, Node.js and Ollama exist
2. Start Ollama if it isn't running
3. Install packages (first run only, takes a few minutes)
4. Open a **Backend** window (port 8000) and a **Frontend** window (port 5173)
5. Wait until the PDF is loaded, then open http://localhost:5173 in your browser

**To stop:** close the "Backend" and "Frontend" windows.

### Manual way (useful for learning or debugging)

```powershell
# Terminal 1 — backend
cd backend
python -m venv .venv                               # one time
.\.venv\Scripts\pip install -r requirements.txt    # one time
.\.venv\Scripts\uvicorn main:app --reload --port 8000

# Terminal 2 — frontend
cd frontend
npm install        # one time
npm run dev
```

Then open http://localhost:5173.

Useful extras:
- http://localhost:8000/docs gives you an automatic test page for the API (from FastAPI).
- `.\.venv\Scripts\python rag.py` (inside `backend`) tests the RAG logic alone, without the UI.

---

## 5. Common problems

| Problem | Fix |
|---------|-----|
| `python` / `npm` / `ollama` "not recognized" | Not installed, or not on PATH. Reinstall (tick "Add to PATH") and **open a new terminal**. |
| Backend window shows `model "llama3.1:8b" not found` | Run `ollama pull llama3.1:8b` and `ollama pull nomic-embed-text`. |
| Backend window shows a connection error to Ollama | Open the Ollama app, or run `ollama serve`. |
| Browser says "Is the backend running?" | Look at the **Backend** window for the error message. |
| `start.bat` keeps saying "Waiting for the backend…" | The backend crashed. Read the Backend window, fix the issue, close all windows and run `start.bat` again. |
| Port 8000 or 5173 "already in use" | An old Backend/Frontend window is still open. Close it first. |
| Answers are slow | Normal on a CPU: an 8B model takes a few seconds per answer. |

---

## 6. Want to use a different PDF?
Put the PDF in the project folder and change `PDF_PATH` at the top of `backend/rag.py`.
Restart the backend. It re-reads and re-embeds the PDF on every start.
