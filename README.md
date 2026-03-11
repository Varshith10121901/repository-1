# repository-1

A collection of AI / Gemini / NLP experiments and web-UI demos built with Python, Flask, FastAPI, and vanilla HTML/CSS/JS.

---

## 📂 Repository Overview

| Category | Files |
|---|---|
| **Gemini AI – Flask/FastAPI backends** | `geminiflas.py`, `geminimixture.py`, `geminijsclone.py`, `gemini_flask_app.py`, `geminiflas.py` |
| **Gemini AI – scripts** | `gemini code analyser.py`, `geminiimage.py`, `geminiimagegenerator.py`, `geminiaudio.py` |
| **NLP / NLTK** | `NLPunderstanding.py`, `cluadenltk.py`, `endcluadenltk.py`, `pythonnltk.py`, `gemininltk.py` |
| **Web UI – HTML pages** | `index.html`, `seprate.html`, `menubar.html`, `login.html`, `logindatabase.html`, `geminijs.html`, `geminijsclone.html`, `geminiimagejs.html`, `image_analyzer.html`, `newaura.html` |
| **Stylesheets** | `index.css`, `seprate.css`, `micbutton.css` |
| **JavaScript** | `seprate.js`, `newaura.js` |
| **Database / Login backend** | `connectdatabase.py`, `loginhtmldatabase.py`, `fastapi.py` |
| **Other Python utilities** | `googlevoice.py`, `merge.py`, `calculator.py`, `orginal.py` |
| **Data files** | `database.csv`, `database2.csv` |
| **Notebook** | `Python_Basics_18-07-2025.ipynb` |

---

## ✨ Highlights

### 🤖 Gemini AI Chat & Image Apps
- **`geminiflas.py`** – Full-featured Flask application with Gemini AI chat integration.
- **`geminimixture.py`** – Mixing multiple Gemini AI responses/modes.
- **`geminijsclone.py`** – Python backend for the `geminijsclone.html` front-end.
- **`geminijs.html`** / **`geminijsclone.html`** – Rich chat UIs powered by Gemini.
- **`geminiimagejs.html`** – Front-end for Gemini image generation/analysis.
- **`gemini code analyser.py`** – Analyse code snippets using Gemini.
- **`image_analyzer.html`** – HTML UI for image analysis features.

### 🧠 NLP / NLTK Experiments
- **`NLPunderstanding.py`** – Core NLP utilities using NLTK.
- **`cluadenltk.py`** / **`endcluadenltk.py`** – Claude + NLTK hybrid experiments.
- **`pythonnltk.py`** / **`gemininltk.py`** – NLTK pipelines for Python and Gemini queries.

### 🌐 Web UI
- **`index.html`** + **`index.css`** – Main landing / dashboard page.
- **`seprate.html`** + **`seprate.css`** + **`seprate.js`** – Separate chat/tool interface.
- **`menubar.html`** – Reusable navigation menu component.
- **`login.html`** / **`logindatabase.html`** – User login interface with database back-end.
- **`newaura.html`** + **`newaura.js`** – Aura UI experiment.

### ⚡ API Servers
- **`fastapi.py`** – FastAPI server exposing REST endpoints.
- **`gemini_flask_app.py`** – Lightweight Flask wrapper around Gemini API.
- **`loginhtmldatabase.py`** / **`connectdatabase.py`** – Login + database connectivity layer.

---

## 🗂️ Suggested Folder Structure

```
repository-1/
├── backend/          # Python backends (Flask, FastAPI, DB connectors)
├── frontend/         # HTML / CSS / JS front-end files
├── nlp/              # NLP and NLTK experiment scripts
├── gemini/           # Gemini AI scripts and utilities
├── data/             # CSV and other data files
├── notebooks/        # Jupyter notebooks
├── .gitignore
├── requirements.txt  # (create this – see Setup)
├── README.md
├── LICENSE
└── CONTRIBUTING.md
```

> **Current state:** All files are in the repository root. The structure above is a recommended goal for future organisation.

---

## ⚙️ Setup

### Prerequisites
- Python 3.9 or higher
- `pip` package manager
- A [Google Gemini API key](https://ai.google.dev/) (for AI scripts)

### Install dependencies

> A `requirements.txt` does not yet exist. Below are the key packages used across scripts. Create a `requirements.txt` with the versions you need:

```
flask
fastapi
uvicorn
google-generativeai
anthropic
nltk
requests
python-dotenv
mysql-connector-python
pandas
SpeechRecognition
```

Then install:

```bash
pip install -r requirements.txt
```

### Environment variables

> ⚠️ **Never hard-code API keys in source files.** Store them in a `.env` file (already in `.gitignore`).

Create a `.env` file in the project root:

```dotenv
GEMINI_API_KEY=your_gemini_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
DB_HOST=localhost
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_NAME=your_database_name
```

Load them in Python:

```python
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
```

---

## ▶️ How to Run

### FastAPI server
```bash
uvicorn fastapi:app --reload
# API available at http://127.0.0.1:8000
```

### Flask / Gemini Flask app
```bash
python gemini_flask_app.py
# or
python geminiflas.py
# Server starts on http://127.0.0.1:5000
```

### Gemini JS Clone backend
```bash
python geminijsclone.py
# then open geminijsclone.html in your browser
```

### Static HTML pages
Open any `.html` file directly in a browser (no server required for static pages):
- `index.html` – Main dashboard
- `geminijs.html` – Gemini chat UI
- `geminiimagejs.html` – Gemini image UI
- `login.html` – Login page

### Login + Database backend
```bash
python loginhtmldatabase.py
# then open login.html
```

---

## 🔒 Security Notes

- **Never commit API keys or passwords** to this repository.
- All secret-like file patterns (`*.key`, `*apikey*`, `.env`, etc.) are listed in `.gitignore`.
- If you accidentally commit a secret, revoke/rotate the key immediately and use `git filter-branch` or BFG Repo Cleaner to purge it from history.

---

## 🗺️ Roadmap / Tasks

- [ ] **Organise files** into `backend/`, `frontend/`, `nlp/`, `gemini/`, `data/` subfolders
- [ ] **Create `requirements.txt`** listing all package dependencies with pinned versions
- [ ] **Add unit tests** for key Python modules (NLP, Gemini helpers, DB connectors)
- [ ] **Modularise** large scripts (`geminiflas.py`, `endcluadenltk.py`, `geminimixture.py`) into smaller modules
- [ ] **Document each script** with module-level docstrings and README entries
- [ ] **Add CI/CD** workflow (GitHub Actions) for linting and testing
- [ ] **Environment variable validation** – add startup checks for required env vars
- [ ] **Error handling** – improve error messages for missing API keys or DB connection failures

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.
