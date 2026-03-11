# repository-1

A collection of AI-powered applications, chatbots, and web tools built with **Google Gemini AI**, **OpenAI**, **Flask**, **FastAPI**, and **NLTK**. This repository includes everything from simple Python scripts to full-stack web applications with database integration.

---

## 📁 Project Structure

```
repository-1/
├── ai/                        # AI model integrations
│   ├── gemini/
│   │   ├── chatbot/           # Gemini AI chat applications
│   │   ├── image/             # Gemini image analysis & generation
│   │   ├── audio/             # Gemini audio description tool
│   │   └── code/              # Gemini code execution scripts
│   ├── openai/                # OpenAI & DeepSeek API integrations
│   └── nlp/                   # NLTK-based chatbots
│
├── backend/                   # Server-side code
│   ├── flask/                 # Flask web server apps
│   ├── fastapi/               # FastAPI web server app
│   └── database/              # Database connectors & SQL schemas
│
├── desktop/                   # Tkinter desktop GUI applications
│
├── frontend/                  # Web UI assets
│   ├── html/                  # HTML pages
│   ├── css/                   # Stylesheets
│   └── js/                    # JavaScript files
│
├── computer-vision/           # OpenCV image processing scripts
├── voice-assistant/           # Voice recognition & text-to-speech assistant
├── data/                      # CSV data files
├── notebooks/                 # Jupyter notebooks
├── basics/                    # Python learning scripts
└── config/                    # Setup notes & configuration
```

---

## 🤖 AI Modules (`ai/`)

### Gemini AI — Chatbot (`ai/gemini/chatbot/`)
| File | Description |
|------|-------------|
| `gemini_chat_flask.py` | Flask web app with Gemini 2.0 Flash chat API and conversation history |
| `gemini_connector.py` | Lightweight Flask server using the `google.genai` client library |
| `gemini_basic.py` | Minimal Gemini API usage example (getting started) |
| `gemini_v2.py` | Image generation using Imagen 3 via the `google.genai` client |

### Gemini AI — Image (`ai/gemini/image/`)
| File | Description |
|------|-------------|
| `gemini_image_analyzer.py` | Analyze images using `gemini-2.0-flash` via PIL |
| `gemini_image_generator.py` | Generate images using `gemini-2.0-flash-exp` model |
| `gemini_image_v2.py` | Alternative image analyzer using PIL and the genai client |
| `gemini_image_creator.py` | Generate images and save locally with `gemini-2.0-flash-exp-image-generation` |

### Gemini AI — Audio (`ai/gemini/audio/`)
| File | Description |
|------|-------------|
| `gemini_audio.py` | Tkinter GUI app to load an audio file and generate a text description with Gemini |

### Gemini AI — Code Execution (`ai/gemini/code/`)
| File | Description |
|------|-------------|
| `gemini_code_executor.py` | Send a math/code problem to Gemini and let it run code to solve it |

### OpenAI / DeepSeek (`ai/openai/`)
| File | Description |
|------|-------------|
| `beta_api_test.py` | Test chat completions using the beta OpenAI-compatible API with DeepSeek/GPT-4o |
| `openai_deepseek.py` | Single-turn chat completion using the DeepSeek-R1 model |

### NLP Chatbots (`ai/nlp/`)
| File | Description |
|------|-------------|
| `nlp_understanding.py` | NLP demo: tokenization, POS tagging, and Named Entity Recognition with NLTK |
| `chatbot_nltk_edit.py` | Flask chatbot with NLTK, sentiment analysis, weather, Wikipedia, and MySQL |
| `chatbot_v5.py` | Flask chatbot enhanced with spaCy, TextBlob, ML classifier, and news feeds |
| `claude_nltk_chatbot.py` | Flask chatbot with TF-IDF similarity, weather, Wikipedia, and jokes |
| `claude_nltk_enhanced.py` | Flask chatbot with advanced NLP using NLTK WordNet lemmatizer |
| `build_chatbot.py` | Deep-learning chatbot using TensorFlow and NLTK (loads `intents.json`) |
| `gemini_nltk_chatbot.py` | NLTK-based rule-matching chatbot (command-line) |

---

## 🖥️ Backend (`backend/`)

### Flask Apps (`backend/flask/`)
| File | Description |
|------|-------------|
| `gemini_flask_app.py` | Full-featured Flask + Gemini AI Suite with image analysis, chat, and code generation (with MySQL) |
| `gemini_flask_full.py` | Extended Flask + Gemini app with MySQL database and CORS support |
| `gemini_flask_clone.py` | Flask backend that serves the Gemini JS-clone frontend |
| `nltk_chatbot_original.py` | Original Flask NLTK chatbot with knowledge base and CORS |
| `nltk_chatbot_flask.py` | Flask NLTK chatbot with web UI (renders `index.html`) |
| `login_database.py` | Flask login system backed by MySQL (`varshith` database) |
| `connect_database.py` | Flask app with MySQL connection and CORS for DB queries |
| `simple_flask_chat.py` | Minimal Flask chat endpoint returning simple responses |

### FastAPI App (`backend/fastapi/`)
| File | Description |
|------|-------------|
| `gemini_ai_suite_api.py` | Full FastAPI app — image analysis, AI chat, and code generation with MySQL and Jinja2 templates |

### Database (`backend/database/`)
| File | Description |
|------|-------------|
| `db_connector.py` | MySQL connection test script |
| `image_database.py` | Helper to store image analysis results in MySQL |
| `chatbot.sql` | SQL schema for chatbot message storage |
| `coding.sql` | SQL schema for code generation history |
| `mixture.sql` | SQL schema for mixed AI session storage |
| `mongodb_playground.js` | MongoDB playground script for experimenting with collections |

---

## 🖱️ Desktop Apps (`desktop/`)
| File | Description |
|------|-------------|
| `gemini_chat_tkinter.py` | Tkinter GUI chat app powered by Gemini 2.0 Flash |
| `gemini_suite_tkinter.py` | Full-featured Tkinter app: image analysis, chat, and code generation (with MySQL) |
| `gemini_suite_extended.py` | Extended Tkinter Gemini suite with file dialog, tabs, and image preview |
| `gemini_code_tkinter.py` | Tkinter GUI for generating code with Gemini AI |
| `gemini_code_analyser.py` | Tkinter GUI code analyser powered by Gemini AI |

---

## 🌐 Frontend (`frontend/`)

### HTML Pages (`frontend/html/`)
| File | Description |
|------|-------------|
| `index.html` | Main landing page |
| `aura.html` | AURA AI chat interface |
| `newaura.html` | Updated AURA AI interface |
| `newaura_chatbot.html` | Basic chatbot web UI (originally misnamed as `.js`) |
| `copilot.html` | AI Copilot chat page |
| `geminijs.html` | Gemini AI chat (JavaScript-driven) |
| `geminijsclone.html` | Gemini JS clone chat interface |
| `geminiimagejs.html` | Gemini image analysis interface |
| `image_analyzer.html` | Image upload and analysis page |
| `code_generator.html` | AI code generator interface |
| `code_analysis.html` | Code analysis tool page |
| `code_analysis_tool.html` | Alternative code analysis page (originally misnamed as `.js`) |
| `database.html` | Database management UI |
| `logindatabase.html` | Login/register interface with database |
| `login.html` | Simple login page |
| `menubar.html` | Navigation menu bar component |
| `pyscrip.html` | Python script runner page |
| `cluadeedit.html` | Claude/AI edit interface |
| `suhas2.html` | AURA AI advanced assistant interface |
| `realme.html` | Real-time chat page |
| `new.html` | New features/demo page |
| `none.html` | Placeholder/empty page |
| `bile.html` | Miscellaneous page |
| `seprate.html` | Separate chat UI |
| `seprat.html` | Alternate separate chat page |

### CSS (`frontend/css/`)
| File | Description |
|------|-------------|
| `index.css` | Main stylesheet |
| `micbutton.css` | Microphone button styles |
| `seprate.css` | Separate UI component styles |

### JavaScript (`frontend/js/`)
| File | Description |
|------|-------------|
| `gemini.js` | Gemini AI frontend integration |
| `seprate.js` | Separate UI component logic |
| `sepratesendbutton.js` | Send button handler for separate chat |
| `jstest.js` | JavaScript testing/experiments |

---

## 👁️ Computer Vision (`computer-vision/`)
| File | Description |
|------|-------------|
| `image_cartoonizer.py` | Convert a photo to a cartoon-style image using OpenCV bilateral filtering |

---

## 🎤 Voice Assistant (`voice-assistant/`)
| File | Description |
|------|-------------|
| `google_voice_assistant.py` | Voice-enabled chatbot with speech recognition (SpeechRecognition), text-to-speech (pyttsx3), Gemini AI, Wikipedia, weather, and more |

---

## 📊 Data (`data/`)
| File | Description |
|------|-------------|
| `database.csv` | Sample/exported database data |
| `database2.csv` | Additional sample database data |

---

## 📒 Notebooks (`notebooks/`)
| File | Description |
|------|-------------|
| `Python_Basics_18-07-2025.ipynb` | Jupyter notebook covering Python basics |

---

## 🐍 Basics (`basics/`)
| File | Description |
|------|-------------|
| `calculator.py` | Command-line calculator supporting natural language expressions and trig functions |
| `hello_world_animation.py` | Animated "Hello World!" text using character iteration |
| `python_basics.py` | Simple Python type system demonstrations |

---

## ⚙️ Config (`config/`)
| File | Description |
|------|-------------|
| `flask_setup.txt` | Flask environment setup notes and useful links |
| `betaapikey.txt` | Beta API key (see security note below) |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- `pip` package manager
- MySQL Server (for database-backed apps)
- Google Gemini API key

### Installation

```bash
# Clone the repository
git clone https://github.com/Varshith10121901/repository-1.git
cd repository-1

# Install common dependencies
pip install flask flask-cors google-generativeai python-dotenv Pillow
pip install fastapi uvicorn mysql-connector-python
pip install nltk pyjokes wikipedia-api requests
pip install opencv-python speechrecognition pyttsx3
```

### Environment Setup

Create a `.env` file in the project root:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

> ⚠️ **Security Note:** Never commit API keys directly to source code or config files. Use environment variables or a `.env` file (which is already listed in `.gitignore`). The `config/betaapikey.txt` file and any hardcoded API keys in the source code should be rotated. Keys should be loaded via `os.getenv()` or `python-dotenv`.

### Running Applications

**Flask Chat App (Gemini):**
```bash
python backend/flask/gemini_flask_app.py
# Visit http://localhost:5000
```

**FastAPI Suite:**
```bash
uvicorn backend.fastapi.gemini_ai_suite_api:app --reload
# Visit http://localhost:8000
```

**Tkinter Desktop Chat:**
```bash
python desktop/gemini_chat_tkinter.py
```

**Voice Assistant:**
```bash
python voice-assistant/google_voice_assistant.py
```

---

## 🛠️ Technologies Used

| Category | Technologies |
|----------|-------------|
| AI / ML | Google Gemini 2.0 Flash, OpenAI, DeepSeek, NLTK, spaCy, TensorFlow |
| Backend | Flask, FastAPI, Uvicorn |
| Database | MySQL, MongoDB |
| Frontend | HTML5, CSS3, JavaScript, Tailwind CSS |
| Desktop | Tkinter |
| Computer Vision | OpenCV (cv2), Pillow |
| Voice | SpeechRecognition, pyttsx3 |
| Data | Pandas, CSV |

---

## 📝 License

This project is open source. Feel free to use and modify the code for learning and personal projects.