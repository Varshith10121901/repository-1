import os
import mysql.connector
from datetime import datetime
import google.generativeai as genai
from flask import Flask, request, render_template_string, jsonify
from pathlib import Path
from PIL import Image
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure the script runs from its own directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))
logger.info(f"Current working directory: {os.getcwd()}")

# Flask application with Gemini AI integration
app = Flask(__name__)

# Ensure upload directory exists
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Define HTML templates as strings
UNIQUEFINAL_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI-Powered Application</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/styles.css') }}">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
</head>
<body>
    <header>
        <div class="container">
            <div class="header-content">
                <div class="logo">
                    <img src="{{ url_for('static', filename='images/logo.png') }}" alt="Logo">
                    <h1>AI Platform</h1>
                </div>
                <nav>
                    <ul>
                        <li><a href="{{ url_for('home') }}">Home</a></li>
                        <li><a href="{{ url_for('image_analyzer') }}">Image Analyzer</a></li>
                        <li><a href="{{ url_for('chat') }}">Chat</a></li>
                        <li><a href="{{ url_for('code_generator') }}">Code Generator</a></li>
                    </ul>
                </nav>
            </div>
        </div>
    </header>

    <section class="hero">
        <div class="hero-content">
            <h2>Experience the Power of AI</h2>
            <p>Analyze images, chat with AI, and generate code with our advanced AI platform.</p>
            <a href="{{ url_for('image_analyzer') }}" class="btn">Get Started</a>
        </div>
    </section>

    <section class="features">
        <div class="container">
            <h2 class="section-title">Our Features</h2>
            <div class="features-grid">
                <div class="feature-item">
                    <div class="feature-icon"><i class="fas fa-image"></i></div>
                    <h3>Image Analysis</h3>
                    <p>Analyze and understand images with our powerful AI vision capabilities.</p>
                </div>
                <div class="feature-item">
                    <div class="feature-icon"><i class="fas fa-comments"></i></div>
                    <h3>AI Chat</h3>
                    <p>Engage in intelligent conversations with our AI-powered chatbot.</p>
                </div>
                <div class="feature-item">
                    <div class="feature-icon"><i class="fas fa-code"></i></div>
                    <h3>Code Generation</h3>
                    <p>Generate clean, well-commented code for your projects instantly.</p>
                </div>
            </div>
        </div>
    </section>

    <footer>
        <div class="container">
            <div class="footer-content">
                <div class="footer-col">
                    <h3>About Us</h3>
                    <p>We're passionate about making AI accessible to everyone.</p>
                </div>
                <div class="footer-col">
                    <h3>Quick Links</h3>
                    <ul class="footer-links">
                        <li><a href="{{ url_for('home') }}">Home</a></li>
                        <li><a href="{{ url_for('image_analyzer') }}">Image Analyzer</a></li>
                        <li><a href="{{ url_for('chat') }}">Chat</a></li>
                        <li><a href="{{ url_for('code_generator') }}">Code Generator</a></li>
                    </ul>
                </div>
                <div class="footer-col">
                    <h3>Contact</h3>
                    <p>Email: support@aiplatform.com</p>
                    <p>Phone: (123) 456-7890</p>
                </div>
            </div>
            <div class="copyright">
                <p>© 2025 AI Platform. All rights reserved.</p>
            </div>
        </div>
    </footer>

    <script src="https://kit.fontawesome.com/your-fontawesome-kit.js"></script>
    <script src="{{ url_for('static', filename='js/main.js') }}"></script>
</body>
</html>
"""

IMAGE_ANALYZER_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Image Analyzer - AI Platform</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/styles.css') }}">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
</head>
<body>
    <header>
        <div class="container">
            <div class="header-content">
                <div class="logo">
                    <img src="{{ url_for('static', filename='images/logo.png') }}" alt="Logo">
                    <h1>AI Platform</h1>
                </div>
                <nav>
                    <ul>
                        <li><a href="{{ url_for('home') }}">Home</a></li>
                        <li><a href="{{ url_for('image_analyzer') }}" class="active">Image Analyzer</a></li>
                        <li><a href="{{ url_for('chat') }}">Chat</a></li>
                        <li><a href="{{ url_for('code_generator') }}">Code Generator</a></li>
                    </ul>
                </nav>
            </div>
        </div>
    </header>

    <section class="image-analyzer-container">
        <div class="container">
            <h2 class="section-title">Image Analyzer</h2>
            <div class="card">
                <h3 class="card-title">Upload and Analyze Image</h3>
                <div class="image-preview" id="image-drop-zone">
                    <p>Drag and drop image here or click to upload</p>
                    <input type="file" id="image-file" accept="image/*" style="display: none;">
                    <div id="image-preview"></div>
                </div>
                <div class="form-group">
                    <label for="prompt-input" class="form-label">Analysis Prompt</label>
                    <textarea id="prompt-input" class="form-control" placeholder="Enter your analysis prompt"></textarea>
                </div>
                <button id="analyze-button" class="btn" disabled>Analyze Image</button>
                <div id="loading-indicator" class="loader hidden"></div>
            </div>
            <div id="analysis-results" class="mt-3"></div>
            <div id="image-history" class="mt-3"></div>
        </div>
    </section>

    <footer>
        <div class="container">
            <div class="footer-content">
                <div class="footer-col">
                    <h3>About Us</h3>
                    <p>We're passionate about making AI accessible to everyone.</p>
                </div>
                <div class="footer-col">
                    <h3>Quick Links</h3>
                    <ul class="footer-links">
                        <li><a href="{{ url_for('home') }}">Home</a></li>
                        <li><a href="{{ url_for('image_analyzer') }}">Image Analyzer</a></li>
                        <li><a href="{{ url_for('chat') }}">Chat</a></li>
                        <li><a href="{{ url_for('code_generator') }}">Code Generator</a></li>
                    </ul>
                </div>
                <div class="footer-col">
                    <h3>Contact</h3>
                    <p>Email: support@aiplatform.com</p>
                    <p>Phone: (123) 456-7890</p>
                </div>
            </div>
            <div class="copyright">
                <p>© 2025 AI Platform. All rights reserved.</p>
            </div>
        </div>
    </footer>

    <script src="https://kit.fontawesome.com/your-fontawesome-kit.js"></script>
    <script src="{{ url_for('static', filename='js/main.js') }}"></script>
</body>
</html>
"""

CHAT_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Chat - AI Platform</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/styles.css') }}">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
</head>
<body>
    <header>
        <div class="container">
            <div class="header-content">
                <div class="logo">
                    <img src="{{ url_for('static', filename='images/logo.png') }}" alt="Logo">
                    <h1>AI Platform</h1>
                </div>
                <nav>
                    <ul>
                        <li><a href="{{ url_for('home') }}">Home</a></li>
                        <li><a href="{{ url_for('image_analyzer') }}">Image Analyzer</a></li>
                        <li><a href="{{ url_for('chat') }}" class="active">Chat</a></li>
                        <li><a href="{{ url_for('code_generator') }}">Code Generator</a></li>
                    </ul>
                </nav>
            </div>
        </div>
    </header>

    <section class="chat-section">
        <div class="container">
            <h2 class="section-title">AI Chat</h2>
            <div class="chat-container card">
                <div id="chat-history" class="chat-history">
                    <p>Loading chat history...</p>
                </div>
                <div class="chat-input">
                    <input type="text" id="message-input" class="form-control" placeholder="Type your message...">
                    <button id="send-button" class="btn">Send</button>
                </div>
            </div>
        </div>
    </section>

    <footer>
        <div class="container">
            <div class="footer-content">
                <div class="footer-col">
                    <h3>About Us</h3>
                    <p>We're passionate about making AI accessible to everyone.</p>
                </div>
                <div class="footer-col">
                    <h3>Quick Links</h3>
                    <ul class="footer-links">
                        <li><a href="{{ url_for('home') }}">Home</a></li>
                        <li><a href="{{ url_for('image_analyzer') }}">Image Analyzer</a></li>
                        <li><a href="{{ url_for('chat') }}">Chat</a></li>
                        <li><a href="{{ url_for('code_generator') }}">Code Generator</a></li>
                    </ul>
                </div>
                <div class="footer-col">
                    <h3>Contact</h3>
                    <p>Email: support@aiplatform.com</p>
                    <p>Phone: (123) 456-7890</p>
                </div>
            </div>
            <div class="copyright">
                <p>© 2025 AI Platform. All rights reserved.</p>
            </div>
        </div>
    </footer>

    <script src="https://kit.fontawesome.com/your-fontawesome-kit.js"></script>
    <script src="{{ url_for('static', filename='js/main.js') }}"></script>
</body>
</html>
"""

CODE_GENERATOR_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Code Generator - AI Platform</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/styles.css') }}">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
</head>
<body>
    <header>
        <div class="container">
            <div class="header-content">
                <div class="logo">
                    <img src="{{ url_for('static', filename='images/logo.png') }}" alt="Logo">
                    <h1>AI Platform</h1>
                </div>
                <nav>
                    <ul>
                        <li><a href="{{ url_for('home') }}">Home</a></li>
                        <li><a href="{{ url_for('image_analyzer') }}">Image Analyzer</a></li>
                        <li><a href="{{ url_for('chat') }}">Chat</a></li>
                        <li><a href="{{ url_for('code_generator') }}" class="active">Code Generator</a></li>
                    </ul>
                </nav>
            </div>
        </div>
    </header>

    <section class="code-generator-container">
        <div class="container">
            <h2 class="section-title">Code Generator</h2>
            <div class="card">
                <h3 class="card-title">Generate Code</h3>
                <form id="code-form">
                    <div class="form-group">
                        <label for="query-input" class="form-label">Code Generation Request</label>
                        <textarea id="query-input" class="form-control" placeholder="Describe the code you want to generate" required></textarea>
                    </div>
                    <button id="generate-button" class="btn" type="submit">Generate Code</button>
                    <div id="loading-indicator" class="loader hidden"></div>
                </form>
            </div>
            <div id="code-results" class="mt-3"></div>
            <div id="code-history" class="mt-3"></div>
        </div>
    </section>

    <footer>
        <div class="container">
            <div class="footer-content">
                <div class="footer-col">
                    <h3>About Us</h3>
                    <p>We're passionate about making AI accessible to everyone.</p>
                </div>
                <div class="footer-col">
                    <h3>Quick Links</h3>
                    <ul class="footer-links">
                        <li><a href="{{ url_for('home') }}">Home</a></li>
                        <li><a href="{{ url_for('image_analyzer') }}">Image Analyzer</a></li>
                        <li><a href="{{ url_for('chat') }}">Chat</a></li>
                        <li><a href="{{ url_for('code_generator') }}">Code Generator</a></li>
                    </ul>
                </div>
                <div class="footer-col">
                    <h3>Contact</h3>
                    <p>Email: support@aiplatform.com</p>
                    <p>Phone: (123) 456-7890</p>
                </div>
            </div>
            <div class="copyright">
                <p>© 2025 AI Platform. All rights reserved.</p>
            </div>
        </div>
    </footer>

    <script src="https://kit.fontawesome.com/your-fontawesome-kit.js"></script>
    <script src="{{ url_for('static', filename='js/main.js') }}"></script>
</body>
</html>
"""

class GeminiAIService:
    """Centralized service for Gemini AI interactions"""
    
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("GEMINI_API_KEY")
        
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not found in environment variables.")
            
        if self.api_key:
            genai.configure(api_key=self.api_key)
            
        self.chat_model = genai.GenerativeModel("gemini-1.5-flash")
        self.vision_model = genai.GenerativeModel("gemini-1.5-pro")
        self.code_model = genai.GenerativeModel("gemini-1.5-pro")
        
        self.chat_sessions = {}
        self.db = DatabaseManager()
    
    def analyze_image(self, image_path, prompt):
        try:
            with Image.open(image_path) as img:
                response = self.vision_model.generate_content([prompt, img])
                analysis_result = response.text
                
                self.db.save_image_analysis(
                    image_path=str(image_path),
                    prompt=prompt,
                    result=analysis_result
                )
                
                return {
                    "success": True,
                    "result": analysis_result,
                    "image_path": str(image_path)
                }
        except Exception as e:
            logger.error(f"Error analyzing image: {e}")
            return {"success": False, "error": str(e)}
    
    def chat(self, message, session_id):
        try:
            if session_id not in self.chat_sessions:
                self.chat_sessions[session_id] = self.chat_model.start_chat(history=[])
            
            chat = self.chat_sessions[session_id]
            response = chat.send_message(message)
            bot_response = response.text
            
            self.db.save_chat_message(
                session_id=session_id,
                user_message=message,
                bot_response=bot_response
            )
            
            return {"success": True, "response": bot_response}
        except Exception as e:
            logger.error(f"Error in chat processing: {e}")
            return {"success": False, "error": str(e)}
    
    def generate_code(self, query):
        try:
            prompt = f"Generate code for: {query}\n\nProvide clear, well-commented code."
            response = self.code_model.generate_content(prompt)
            code_result = response.text
            
            self.db.save_code_generation(query=query, code_result=code_result)
            
            return {"success": True, "code": code_result}
        except Exception as e:
            logger.error(f"Error generating code: {e}")
            return {"success": False, "error": str(e)}
    
    def get_chat_history(self, session_id):
        return self.db.get_chat_history(session_id)
    
    def get_image_history(self):
        return self.db.get_image_history()
    
    def get_code_history(self):
        return self.db.get_code_history()

class DatabaseManager:
    """Handles all database operations"""
    
    def __init__(self):
        try:
            self.conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password='1234',
                database='tommy'
            )
            self._create_tables()
            logger.info("Database connected successfully")
        except mysql.connector.Error as err:
            logger.error(f"Database connection error: {err}")
            self.conn = None
    
    def _create_tables(self):
        if not self.conn:
            return
            
        cursor = self.conn.cursor()
        tables = {
            'image_table': """
                CREATE TABLE IF NOT EXISTS image_table (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    image_path VARCHAR(255) NOT NULL,
                    prompt TEXT NOT NULL,
                    analysis_result TEXT NOT NULL,
                    analysis_date DATETIME NOT NULL
                )
            """,
            'chatbot_table': """
                CREATE TABLE IF NOT EXISTS chatbot_table (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    session_id VARCHAR(50) NOT NULL,
                    user_message TEXT NOT NULL,
                    bot_response TEXT NOT NULL,
                    chat_date DATETIME NOT NULL
                )
            """,
            'coding_table': """
                CREATE TABLE IF NOT EXISTS coding_table (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    query TEXT NOT NULL,
                    code_result TEXT NOT NULL,
                    execution_result TEXT,
                    analysis_date DATETIME NOT NULL
                )
            """
        }
        
        for table_name, create_query in tables.items():
            cursor.execute(create_query)
            logger.info(f"Created table {table_name} if not exists")
            
        self.conn.commit()
        cursor.close()
    
    def _ensure_connection(self):
        if not self.conn or not self.conn.is_connected():
            try:
                self.conn = mysql.connector.connect(
                    host='localhost',
                    user='root',
                    password='1234',
                    database='tommy'
                )
                return True
            except mysql.connector.Error as err:
                logger.error(f"Failed to reconnect to database: {err}")
                return False
        return True
    
    def save_image_analysis(self, image_path, prompt, result):
        if not self._ensure_connection():
            return False
            
        try:
            cursor = self.conn.cursor()
            query = """
                INSERT INTO image_table 
                (image_path, prompt, analysis_result, analysis_date) 
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (image_path, prompt, result, datetime.now()))
            self.conn.commit()
            cursor.close()
            return True
        except Exception as e:
            logger.error(f"Database error saving image analysis: {e}")
            return False
    
    def save_chat_message(self, session_id, user_message, bot_response):
        if not self._ensure_connection():
            return False
            
        try:
            cursor = self.conn.cursor()
            query = """
                INSERT INTO chatbot_table 
                (session_id, user_message, bot_response, chat_date) 
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (session_id, user_message, bot_response, datetime.now()))
            self.conn.commit()
            cursor.close()
            return True
        except Exception as e:
            logger.error(f"Database error saving chat message: {e}")
            return False
    
    def save_code_generation(self, query, code_result):
        if not self._ensure_connection():
            return False
            
        try:
            cursor = self.conn.cursor()
            query_sql = """
                INSERT INTO coding_table 
                (query, code_result, execution_result, analysis_date) 
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query_sql, (query, code_result, "Not executed", datetime.now()))
            self.conn.commit()
            cursor.close()
            return True
        except Exception as e:
            logger.error(f"Database error saving code generation: {e}")
            return False
    
    def get_chat_history(self, session_id):
        if not self._ensure_connection():
            return {"success": False, "error": "Database not connected"}
            
        try:
            cursor = self.conn.cursor(dictionary=True)
            query = """
                SELECT user_message, bot_response, chat_date 
                FROM chatbot_table 
                WHERE session_id = %s 
                ORDER BY chat_date ASC
            """
            cursor.execute(query, (session_id,))
            history = cursor.fetchall()
            cursor.close()
            
            for item in history:
                item['chat_date'] = item['chat_date'].strftime('%Y-%m-%d %H:%M:%S')
            
            return {"success": True, "history": history}
        except Exception as e:
            logger.error(f"Error retrieving chat history: {e}")
            return {"success": False, "error": str(e)}
    
    def get_image_history(self):
        if not self._ensure_connection():
            return {"success": False, "error": "Database not connected"}
            
        try:
            cursor = self.conn.cursor(dictionary=True)
            query = """
                SELECT image_path, prompt, analysis_result, analysis_date 
                FROM image_table 
                ORDER BY analysis_date DESC
            """
            cursor.execute(query)
            history = cursor.fetchall()
            cursor.close()
            
            for item in history:
                item['analysis_date'] = item['analysis_date'].strftime('%Y-%m-%d %H:%M:%S')
            
            return {"success": True, "history": history}
        except Exception as e:
            logger.error(f"Error retrieving image history: {e}")
            return {"success": False, "error": str(e)}
    
    def get_code_history(self):
        if not self._ensure_connection():
            return {"success": False, "error": "Database not connected"}
            
        try:
            cursor = self.conn.cursor(dictionary=True)
            query = """
                SELECT query, code_result, execution_result, analysis_date 
                FROM coding_table 
                ORDER BY analysis_date DESC
            """
            cursor.execute(query)
            history = cursor.fetchall()
            cursor.close()
            
            for item in history:
                item['analysis_date'] = item['analysis_date'].strftime('%Y-%m-%d %H:%M:%S')
            
            return {"success": True, "history": history}
        except Exception as e:
            logger.error(f"Error retrieving code history: {e}")
            return {"success": False, "error": str(e)}

# Initialize the Gemini service
gemini_service = GeminiAIService()

# Flask route definitions
@app.route('/')
def home():
    """Render the main page"""
    logger.info("Rendering home page")
    return render_template_string(UNIQUEFINAL_HTML)

@app.route('/image-analyzer')
def image_analyzer():
    """Render the image analyzer page"""
    logger.info("Rendering image analyzer page")
    return render_template_string(IMAGE_ANALYZER_HTML)

@app.route('/chat')
def chat():
    """Render the chat interface"""
    logger.info("Rendering chat page")
    return render_template_string(CHAT_HTML)

@app.route('/code-generator')
def code_generator():
    """Render the code generator page"""
    logger.info("Rendering code generator page")
    return render_template_string(CODE_GENERATOR_HTML)

@app.route('/api/analyze-image', methods=['POST'])
def api_analyze_image():
    """API endpoint for image analysis"""
    file = request.files.get('file')
    if not file:
        return jsonify({"success": False, "error": "No file provided"})
    
    prompt = request.form.get('prompt', 'Analyze this image in detail')
    
    try:
        filename = file.filename
        file_path = UPLOAD_DIR / filename
        file.save(file_path)
        result = gemini_service.analyze_image(file_path, prompt)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in /api/analyze-image: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """API endpoint for chat functionality"""
    message = request.form.get('message')
    if not message:
        return jsonify({"success": False, "error": "No message provided"})
    
    session_id = request.form.get('session_id', 'default_session')
    result = gemini_service.chat(message, session_id)
    return jsonify(result)

@app.route('/api/chat-history/<session_id>', methods=['GET'])
def api_chat_history(session_id):
    """API endpoint to retrieve chat history"""
    result = gemini_service.get_chat_history(session_id)
    return jsonify(result)

@app.route('/api/generate-code', methods=['POST'])
def api_generate_code():
    """API endpoint for code generation"""
    query = request.form.get('query')
    if not query:
        return jsonify({"success": False, "error": "No query provided"})
    
    result = gemini_service.generate_code(query)
    return jsonify(result)

@app.route('/api/image-history', methods=['GET'])
def api_image_history():
    """API endpoint to retrieve image analysis history"""
    result = gemini_service.get_image_history()
    return jsonify(result)

@app.route('/api/code-history', methods=['GET'])
def api_code_history():
    """API endpoint to retrieve code generation history"""
    result = gemini_service.get_code_history()
    return jsonify(result)

def setup_static_files():
    """Creates static directories and files (CSS and JS)"""
    static_dir = Path("static")
    static_dir.mkdir(exist_ok=True)
    logger.info(f"Created static directory: {static_dir}")
    
    css_dir = static_dir / "css"
    css_dir.mkdir(exist_ok=True)
    logger.info(f"Created css directory: {css_dir}")
    
    js_dir = static_dir / "js"
    js_dir.mkdir(exist_ok=True)
    logger.info(f"Created js directory: {js_dir}")
    
    img_dir = static_dir / "images"
    img_dir.mkdir(exist_ok=True)
    logger.info(f"Created images directory: {img_dir}")
    
    # Create main CSS file
    main_css = css_dir / "styles.css"
    try:
        with open(main_css, "w") as f:
            f.write("""
:root {
    --primary-color: #5C43F2;
    --secondary-color: #7D64FF;
    --accent-color: #4920E5;
    --dark-bg: #1A1A2E;
    --light-bg: #F5F5F7;
    --text-light: #FFFFFF;
    --text-dark: #333344;
    --success: #28a745;
    --warning: #ffc107;
    --danger: #dc3545;
    --info: #17a2b8;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: 'Poppins', sans-serif;
}

body {
    background-color: var(--light-bg);
    color: var(--text-dark);
    line-height: 1.6;
}

.container {
    width: 100%;
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}

header {
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    color: var(--text-light);
    padding: 20px 0;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

.header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.logo {
    display: flex;
    align-items: center;
}

.logo h1 {
    font-size: 24px;
    font-weight: 700;
    margin-left: 10px;
}

.logo img {
    width: 40px;
    height: 40px;
}

nav ul {
    display: flex;
    list-style: none;
}

nav ul li {
    margin-left: 30px;
}

nav ul li a {
    color: var(--text-light);
    text-decoration: none;
    font-weight: 500;
    font-size: 16px;
    transition: all 0.3s ease;
}

nav ul li a:hover {
    color: rgba(255, 255, 255, 0.8);
}

.hero {
    background: linear-gradient(rgba(92, 67, 242, 0.8), rgba(73, 32, 229, 0.9));
    background-size: cover;
    background-position: center;
    height: 400px;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    color: var(--text-light);
    padding: 0 20px;
}

.hero-content {
    max-width: 800px;
}

.hero h2 {
    font-size: 42px;
    margin-bottom: 20px;
    font-weight: 700;
}

.hero p {
    font-size: 18px;
    margin-bottom: 30px;
}

.card {
    background-color: white;
    border-radius: 10px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    padding: 30px;
    margin-bottom: 30px;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15);
}

.card-title {
    font-size: 24px;
    font-weight: 600;
    margin-bottom: 15px;
    color: var(--primary-color);
}

.card-text {
    color: var(--text-dark);
    margin-bottom: 20px;
}

.btn {
    display: inline-block;
    padding: 12px 25px;
    background-color: var(--primary-color);
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-size: 16px;
    font-weight: 500;
    text-decoration: none;
    transition: all 0.3s ease;
}

.btn:hover {
    background-color: var(--accent-color);
    transform: translateY(-2px);
}

.btn-outline {
    background-color: transparent;
    border: 2px solid var(--primary-color);
    color: var(--primary-color);
}

.btn-outline:hover {
    background-color: var(--primary-color);
    color: white;
}

.features {
    padding: 60px 0;
}

.section-title {
    text-align: center;
    font-size: 36px;
    font-weight: 700;
    margin-bottom: 50px;
    color: var(--primary-color);
}

.features-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 30px;
}

.feature-item {
    text-align: center;
}

.feature-icon {
    width: 80px;
    height: 80px;
    margin: 0 auto 20px;
    background-color: rgba(92, 67, 242, 0.1);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
}

.feature-icon i {
    font-size: 36px;
    color: var(--primary-color);
}

.feature-item h3 {
    font-size: 20px;
    margin-bottom: 15px;
    font-weight: 600;
}

.form-group {
    margin-bottom: 20px;
}

.form-label {
    display: block;
    margin-bottom: 8px;
    font-weight: 500;
}

.form-control {
    width: 100%;
    padding: 12px 15px;
    border: 1px solid #ddd;
    border-radius: 5px;
    font-size: 16px;
    transition: border-color 0.3s ease;
}

.form-control:focus {
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(92, 67, 242, 0.1);
}

textarea.form-control {
    min-height: 120px;
    resize: vertical;
}

.chat-container {
    display: flex;
    flex-direction: column;
    height: 600px;
    border-radius: 10px;
    overflow: hidden;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.chat-history {
    flex-grow: 1;
    padding: 20px;
    overflow-y: auto;
    background-color: #fff;
}

.message {
    max-width: 80%;
    margin-bottom: 15px;
    padding: 12px 15px;
    border-radius: 10px;
    position: relative;
}

.user-message {
    background-color: var(--primary-color);
    color: white;
    align-self: flex-end;
    margin-left: auto;
}

.bot-message {
    background-color: #f0f0f0;
    color: var(--text-dark);
    align-self: flex-start;
    margin-right: auto;
}

.chat-input {
    display: flex;
    padding: 15px;
    background-color: #fff;
    border-top: 1px solid #eee;
}

.chat-input input {
    flex-grow: 1;
    padding: 12px 15px;
    border: 1px solid #ddd;
    border-radius: 5px;
    margin-right: 10px;
}

.image-preview {
    width: 100%;
    height: 300px;
    border: 2px dashed #ddd;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 20px;
    position: relative;
    overflow: hidden;
}

.image-preview img {
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
}

.code-result {
    background-color: #1E1E3F;
    color: #A9B7C6;
    border-radius: 10px;
    padding: 20px;
    max-height: 500px;
    overflow-y: auto;
    font-family: 'Consolas', 'Monaco', monospace;
    line-height: 1.5;
    margin-top: 20px;
    white-space: pre-wrap;
}

footer {
    background-color: var(--dark-bg);
    color: var(--text-light);
    padding: 40px 0;
    margin-top: 60px;
}

.footer-content {
    display: flex;
    justify-content: space-between;
    flex-wrap: wrap;
}

.footer-col {
    flex: 1;
    min-width: 250px;
    margin-bottom: 30px;
}

.footer-col h3 {
    font-size: 18px;
    margin-bottom: 20px;
    position: relative;
    padding-bottom: 10px;
}

.footer-col h3:after {
    content: '';
    position: absolute;
    left: 0;
    bottom: 0;
    width: 50px;
    height: 2px;
    background-color: var(--primary-color);
}

.footer-links {
    list-style: none;
}

.footer-links li {
    margin-bottom: 10px;
}

.footer-links a {
    color: #bbb;
    text-decoration: none;
    transition: color 0.3s ease;
}

.footer-links a:hover {
    color: var(--primary-color);
}

.copyright {
    text-align: center;
    margin-top: 30px;
    padding-top: 20px;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    font-size: 14px;
}

@media (max-width: 768px) {
    .features-grid {
        grid-template-columns: 1fr;
    }
    
    .hero h2 {
        font-size: 32px;
    }
    
    .hero p {  
        font-size: 16px;
    }
    
    .header-content {
        flex-direction: column;
    }
    
    nav ul {
        margin-top: 20px;
    }
    
    nav ul li {
        margin: 0 10px;
    }
}

.loader {
    display: inline-block;
    width: 40px;
    height: 40px;
    border: 3px solid rgba(92, 67, 242, 0.3);
    border-radius: 50%;
    border-top-color: var(--primary-color);
    animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

.text-center { text-align: center; }
.mt-3 { margin-top: 1.5rem; }
.mb-3 { margin-bottom: 1.5rem; }
.d-flex { display: flex; }
.align-items-center { align-items: center; }
.justify-content-center { justify-content: center; }
.hidden { display: none; }
            """)
        logger.info(f"Created CSS file: {main_css}")
    except Exception as e:
        logger.error(f"Failed to create CSS file {main_css}: {e}")
        raise
    
    # Create main JS file
    main_js = js_dir / "main.js"
    try:
        with open(main_js, "w") as f:
            f.write("""
// Common functions for all pages
document.addEventListener('DOMContentLoaded', function() {
    const header = document.querySelector('header');
    if (header) {
        window.addEventListener('scroll', function() {
            header.classList.toggle('scrolled', window.scrollY > 50);
        });
    }
    
    const menuToggle = document.querySelector('.menu-toggle');
    const navMenu = document.querySelector('nav ul');
    if (menuToggle && navMenu) {
        menuToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
            menuToggle.classList.toggle('active');
        });
    }
    
    if (document.querySelector('.chat-container')) initializeChat();
    if (document.querySelector('.image-analyzer-container')) initializeImageAnalyzer();
    if (document.querySelector('.code-generator-container')) initializeCodeGenerator();
});

function initializeChat() {
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-button');
    const chatHistory = document.getElementById('chat-history');
    const sessionId = 'session_' + Math.random().toString(36).substring(2, 15);
    
    loadChatHistory(sessionId);
    
    if (sendButton && messageInput) {
        sendButton.addEventListener('click', sendMessage);
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });
    }
    
    function sendMessage() {
        const message = messageInput.value.trim();
        if (!message) return;
        
        addMessageToChat('user', message);
        messageInput.value = '';
        
        const loadingElement = document.createElement('div');
        loadingElement.className = 'message bot-message loading';
        loadingElement.innerHTML = '<div class="loader"></div>';
        chatHistory.appendChild(loadingElement);
        chatHistory.scrollTop = chatHistory.scrollHeight;
        
        const formData = new FormData();
        formData.append('message', message);
        formData.append('session_id', sessionId);
        
        fetch('/api/chat', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            chatHistory.removeChild(loadingElement);
            if (data.success) {
                addMessageToChat('bot', data.response);
            } else {
                addMessageToChat('bot', `Error: ${data.error || 'Unknown error'}`);
            }
        })
        .catch(error => {
            chatHistory.removeChild(loadingElement);
            addMessageToChat('bot', 'Network error. Please try again.');
            console.error('Error:', error);
        });
    }
    
    function addMessageToChat(type, content) {
        const messageElement = document.createElement('div');
        messageElement.className = `message ${type}-message`;
        messageElement.textContent = content;
        chatHistory.appendChild(messageElement);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }
    
    function loadChatHistory(sessionId) {
        fetch(`/api/chat-history/${sessionId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success && data.history.length > 0) {
                chatHistory.innerHTML = '';
                data.history.forEach(item => {
                    addMessageToChat('user', item.user_message);
                    addMessageToChat('bot', item.bot_response);
                });
            } else {
                chatHistory.innerHTML = '<p>No previous messages</p>';
            }
        })
        .catch(error => console.error('Error loading chat history:', error));
    }
}

function initializeImageAnalyzer() {
    const dropZone = document.getElementById('image-drop-zone');
    const fileInput = document.getElementById('image-file');
    const previewContainer = document.getElementById('image-preview');
    const analyzeButton = document.getElementById('analyze-button');
    const promptInput = document.getElementById('prompt-input');
    const resultsContainer = document.getElementById('analysis-results');
    const loadingIndicator = document.getElementById('loading-indicator');
    
    if (dropZone) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, preventDefaults, false);
        });
        
        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }
        
        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => dropZone.classList.add('highlight'), false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => dropZone.classList.remove('highlight'), false);
        });
        
        dropZone.addEventListener('drop', (e) => {
            const files = e.dataTransfer.files;
            if (files.length) {
                fileInput.files = files;
                updateImagePreview(files[0]);
            }
        }, false);
        
        dropZone.addEventListener('click', () => fileInput.click());
    }
    
    if (fileInput) {
        fileInput.addEventListener('change', () => {
            if (fileInput.files.length) updateImagePreview(fileInput.files[0]);
        });
    }
    
    function updateImagePreview(file) {
        if (!file.type.match('image.*')) {
            alert('Please select an image file');
            return;
        }
        
        const reader = new FileReader();
        reader.onload = (e) => {
            previewContainer.innerHTML = `<img src="${e.target.result}" alt="Preview">`;
            analyzeButton.disabled = false;
        };
        reader.readAsDataURL(file);
    }
    
    if (analyzeButton) {
        analyzeButton.addEventListener('click', () => {
            if (!fileInput.files.length) {
                alert('Please select an image first');
                return;
            }
            
            loadingIndicator.classList.remove('hidden');
            resultsContainer.innerHTML = '';
            
            const formData = new FormData();
            formData.append('file', fileInput.files[0]);
            formData.append('prompt', promptInput.value || 'Analyze this image in detail');
            
            fetch('/api/analyze-image', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                loadingIndicator.classList.add('hidden');
                resultsContainer.innerHTML = `
                    <div class="card">
                        <h3 class="card-title">${data.success ? 'Analysis Results' : 'Error'}</h3>
                        <p class="card-text">${data.success ? data.result : `Failed to analyze image: ${data.error}`}</p>
                    </div>
                `;
                loadImageHistory(); // Refresh history after new analysis
            })
            .catch(error => {
                loadingIndicator.classList.add('hidden');
                resultsContainer.innerHTML = `
                    <div class="card">
                        <h3 class="card-title">Error</h3>
                        <p class="card-text">Network error: ${error.message}</p>
                    </div>
                `;
                console.error('Error:', error);
            });
        });
    }
    
    loadImageHistory();
    
    function loadImageHistory() {
        const historyContainer = document.getElementById('image-history');
        if (!historyContainer) return;
        
        fetch('/api/image-history')
        .then(response => response.json())
        .then(data => {
            historyContainer.innerHTML = data.success && data.history.length > 0
                ? '<h3>Previous Analyses</h3>'
                : '<p>No previous analysis found</p>';
                
            if (data.success && data.history.length > 0) {
                data.history.forEach(item => {
                    const historyItem = document.createElement('div');
                    historyItem.className = 'history-item card';
                    historyItem.innerHTML = `
                        <p><strong>Date:</strong> ${item.analysis_date}</p>
                        <p><strong>Prompt:</strong> ${item.prompt}</p>
                        <p><strong>Result:</strong> ${item.analysis_result.substring(0, 100)}...</p>
                        <button class="btn btn-outline view-full">View Full Analysis</button>
                    `;
                    historyContainer.appendChild(historyItem);
                    
                    historyItem.querySelector('.view-full').addEventListener('click', () => {
                        resultsContainer.innerHTML = `
                            <div class="card">
                                <h3 class="card-title">Previous Analysis</h3>
                                <p class="card-text">${item.analysis_result}</p>
                            </div>
                        `;
                        resultsContainer.scrollIntoView({behavior: 'smooth'});
                    });
                });
            }
        })
        .catch(error => {
            console.error('Error loading image history:', error);
            historyContainer.innerHTML = '<p>Error loading history</p>';
        });
    }
}

function initializeCodeGenerator() {
    const codeForm = document.getElementById('code-form');
    const queryInput = document.getElementById('query-input');
    const generateButton = document.getElementById('generate-button');
    const resultsContainer = document.getElementById('code-results');
    const loadingIndicator = document.getElementById('loading-indicator');
    
    if (generateButton) {
        generateButton.addEventListener('click', (e) => {
            e.preventDefault();
            generateCode();
        });
    }
    
    if (codeForm) {
        codeForm.addEventListener('submit', (e) => {
            e.preventDefault();
            generateCode();
        });
    }
    
    function generateCode() {
        const query = queryInput.value.trim();
        if (!query) {
            alert('Please enter a query');
            return;
        }
        
        loadingIndicator.classList.remove('hidden');
        resultsContainer.innerHTML = '';
        
        const formData = new FormData();
        formData.append('query', query);
        
        fetch('/api/generate-code', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            loadingIndicator.classList.add('hidden');
            if (data.success) {
                resultsContainer.innerHTML = `
                    <div class="card">
                        <h3 class="card-title">Generated Code</h3>
                        <div class="code-result">${data.code}</div>
                        <button id="copy-button" class="btn mt-3">Copy Code</button>
                    </div>
                `;
                document.getElementById('copy-button').addEventListener('click', () => {
                    navigator.clipboard.writeText(data.code)
                        .then(() => {
                            const copyButton = document.getElementById('copy-button');
                            copyButton.textContent = 'Copied!';
                            setTimeout(() => copyButton.textContent = 'Copy Code', 2000);
                        })
                        .catch(err => {
                            console.error('Failed to copy: ', err);
                            document.getElementById('copy-button').textContent = 'Failed to copy';
                        });
                });
            } else {
                resultsContainer.innerHTML = `
                    <div class="card">
                        <h3 class="card-title">Error</h3>
                        <p class="card-text">Failed to generate code: ${data.error}</p>
                    </div>
                `;
            }
            loadCodeHistory(); // Refresh history after new generation
        })
        .catch(error => {
            loadingIndicator.classList.add('hidden');
            resultsContainer.innerHTML = `
                <div class="card">
                    <h3 class="card-title">Error</h3>
                    <p class="card-text">Network error: ${error.message}</p>
                </div>
            `;
            console.error('Error:', error);
        });
    }
    
    loadCodeHistory();
    
    function loadCodeHistory() {
        const historyContainer = document.getElementById('code-history');
        if (!historyContainer) return;
        
        fetch('/api/code-history')
        .then(response => response.json())
        .then(data => {
            historyContainer.innerHTML = data.success && data.history.length > 0
                ? '<h3>Previous Generations</h3>'
                : '<p>No previous generations found</p>';
                
            if (data.success && data.history.length > 0) {
                data.history.forEach(item => {
                    const historyItem = document.createElement('div');
                    historyItem.className = 'history-item card';
                    historyItem.innerHTML = `
                        <p><strong>Date:</strong> ${item.analysis_date}</p>
                        <p><strong>Query:</strong> ${item.query}</p>
                        <button class="btn btn-outline view-full">View Generated Code</button>
                    `;
                    historyContainer.appendChild(historyItem);
                    
                    historyItem.querySelector('.view-full').addEventListener('click', () => {
                        resultsContainer.innerHTML = `
                            <div class="card">
                                <h3 class="card-title">Previous Code Generation</h3>
                                <div class="code-result">${item.code_result}</div>
                                <button id="copy-history-button" class="btn mt-3">Copy Code</button>
                            </div>
                        `;
                        document.getElementById('copy-history-button').addEventListener('click', () => {
                            navigator.clipboard.writeText(item.code_result)
                                .then(() => {
                                    const copyButton = document.getElementById('copy-history-button');
                                    copyButton.textContent = 'Copied!';
                                    setTimeout(() => copyButton.textContent = 'Copy Code', 2000);
                                })
                                .catch(err => console.error('Failed to copy: ', err));
                        });
                        resultsContainer.scrollIntoView({behavior: 'smooth'});
                    });
                });
            }
        })
        .catch(error => {
            console.error('Error loading code history:', error);
            historyContainer.innerHTML = '<p>Error loading history</p>';
        });
    }
}
            """)
        logger.info(f"Created JS file: {main_js}")
    except Exception as e:
        logger.error(f"Failed to create JS file {main_js}: {e}")
        raise

# Call setup_static_files to create CSS and JS files
try:
    setup_static_files()
    logger.info("Successfully set up all static files")
except Exception as e:
    logger.error(f"Failed to set up static files: {e}")
    raise

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)