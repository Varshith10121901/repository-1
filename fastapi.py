import os
import mysql.connector
from datetime import datetime
import google.generativeai as genai
import uvicorn
from fastapi import FastAPI, UploadFile, Form, File, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import shutil
from pathlib import Path
import base64
import io
from PIL import Image
from dotenv import load_dotenv
import threading

# Initialize FastAPI application
app = FastAPI(title="Gemini AI Suite API", 
             description="API for Gemini AI Image Analysis, Chat, and Code Generation",
             version="1.0.0")

# Create upload directory if it doesn't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Setup Jinja2 templates for the web frontend
templates = Jinja2Templates(directory="templates")

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

class GeminiAISuite:
    def _init_(self):
        # Load environment variables and configure API
        load_dotenv()
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
        else:
            print("Warning: GEMINI_API_KEY not found in environment variables.")
        
        # Initialize variables
        self.chat_model = genai.GenerativeModel("gemini-2.0-flash")
        self.vision_model = genai.GenerativeModel("gemini-pro-vision")
        self.code_model = genai.GenerativeModel("gemini-2.0-pro")
        
        # Initialize chat
        self.chat_history = {}
        
        # Setup database
        self.setup_database()
    
    def setup_database(self):
        """Initialize database connection and create tables if needed"""
        try:
            self.conn = mysql.connector.connect(
                host='localhost', 
                user='root', 
                password='1234', 
                database='tommy'
            )
            cursor = self.conn.cursor()
            
            # Create tables if they don't exist
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
            
            self.conn.commit()
            cursor.close()
            print("Database connected and tables verified")
        except mysql.connector.Error as err:
            print(f"Database error: {err}")
            self.conn = None
    
    def analyze_image(self, image_path, prompt):
        """Analyze an image using Gemini AI Vision"""
        if not self.api_key:
            return {"error": "API key not found. Please set GEMINI_API_KEY in your environment."}
        
        try:
            # Load the image
            img = Image.open(image_path)
            
            # Generate content using Gemini Vision model
            response = self.vision_model.generate_content([prompt, img])
            analysis_result = response.text
            
            # Save to database if connection exists
            if self.conn:
                cursor = self.conn.cursor()
                query = """
                    INSERT INTO image_table 
                    (image_path, prompt, analysis_result, analysis_date) 
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(query, (
                    str(image_path), 
                    prompt, 
                    analysis_result, 
                    datetime.now()
                ))
                self.conn.commit()
                cursor.close()
            
            return {
                "success": True,
                "result": analysis_result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_image_history(self, limit=50):
        """Retrieve image analysis history from database"""
        if not self.conn:
            return {"error": "Database not connected"}
        
        try:
            cursor = self.conn.cursor(dictionary=True)
            query = """
                SELECT id, image_path, prompt, analysis_result, analysis_date
                FROM image_table
                ORDER BY analysis_date DESC
                LIMIT %s
            """
            cursor.execute(query, (limit,))
            history = cursor.fetchall()
            cursor.close()
            
            return {
                "success": True,
                "history": history
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def process_chat_message(self, message, session_id="default"):
        """Process a chat message and get a response"""
        if not self.api_key:
            return {"error": "API key not found"}
        
        try:
            # Initialize session chat if not exists
            if session_id not in self.chat_history:
                self.chat_history[session_id] = self.chat_model.start_chat()
            
            # Get response
            response = self.chat_history[session_id].send_message(message)
            bot_response = response.text
            
            # Save to database if connection exists
            if self.conn:
                cursor = self.conn.cursor()
                query = """
                    INSERT INTO chatbot_table 
                    (session_id, user_message, bot_response, chat_date) 
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(query, (
                    session_id,
                    message, 
                    bot_response, 
                    datetime.now()
                ))
                self.conn.commit()
                cursor.close()
            
            return {
                "success": True,
                "response": bot_response
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_chat_history(self, session_id="default", limit=50):
        """Retrieve chat history for a session"""
        if not self.conn:
            return {"error": "Database not connected"}
        
        try:
            cursor = self.conn.cursor(dictionary=True)
            query = """
                SELECT id, user_message, bot_response, chat_date
                FROM chatbot_table
                WHERE session_id = %s
                ORDER BY chat_date ASC
                LIMIT %s
            """
            cursor.execute(query, (session_id, limit))
            history = cursor.fetchall()
            cursor.close()
            
            return {
                "success": True,
                "history": history
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def run_code_analysis(self, query):
        """Generate code based on the query"""
        if not self.api_key:
            return {"error": "API key not found"}
        
        try:
            # Enhance the prompt for better code generation
            enhanced_query = f"""
            Please generate code for the following request:
            
            {query}
            
            Provide only the code without any additional explanations. If the language is not specified, use Python.
            """
            
            # Generate code
            response = self.code_model.generate_content(enhanced_query)
            code_result = response.text
            
            # Clean up the response to extract just the code
            if "" in code_result:
                # Extract code from markdown code blocks
                code_parts = code_result.split("")
                if len(code_parts) >= 3:
                    # Get content between the first set of ```
                    language_and_code = code_parts[1].strip()
                    if language_and_code.startswith("python") or language_and_code.startswith("javascript") or language_and_code.startswith("html"):
                        # Remove language identifier from first line
                        lines = language_and_code.split("\n")
                        code_result = "\n".join(lines[1:])
                    else:
                        code_result = language_and_code
            
            # Save to database if connection exists
            if self.conn:
                cursor = self.conn.cursor()
                query_sql = """
                    INSERT INTO coding_table 
                    (query, code_result, execution_result, analysis_date) 
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(query_sql, (
                    query, 
                    code_result, 
                    None,  # No execution result for now
                    datetime.now()
                ))
                self.conn.commit()
                cursor.close()
            
            return {
                "success": True,
                "code": code_result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_code_history(self, limit=20):
        """Retrieve code generation history"""
        if not self.conn:
            return {"error": "Database not connected"}
        
        try:
            cursor = self.conn.cursor(dictionary=True)
            query = """
                SELECT id, query, code_result, execution_result, analysis_date
                FROM coding_table
                ORDER BY analysis_date DESC
                LIMIT %s
            """
            cursor.execute(query, (limit,))
            history = cursor.fetchall()
            cursor.close()
            
            return {
                "success": True,
                "history": history
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

# Create global instance of the Gemini AI Suite
gemini_suite = GeminiAISuite()

# API Routes
@app.get("/", response_class=HTMLResponse)
async def get_home(request: Request):
    """Render the home page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/image-analyzer", response_class=HTMLResponse)
async def get_image_analyzer(request: Request):
    """Render the image analyzer page"""
    return templates.TemplateResponse("image_analyzer.html", {"request": request})

@app.get("/chat", response_class=HTMLResponse)
async def get_chat(request: Request):
    """Render the chat interface page"""
    return templates.TemplateResponse("chat.html", {"request": request})

@app.get("/code-generator", response_class=HTMLResponse)
async def get_code_generator(request: Request):
    """Render the code generator page"""
    return templates.TemplateResponse("code_generator.html", {"request": request})

# API Endpoints
@app.post("/api/analyze-image")
async def api_analyze_image(
    file: UploadFile = File(...),
    prompt: str = Form("What is in this image? Provide a detailed description.")
):
    """API endpoint to analyze an image"""
    # Save uploaded file
    file_path = UPLOAD_DIR / file.filename
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Analyze the image
    result = gemini_suite.analyze_image(file_path, prompt)
    
    return JSONResponse(content=result)

@app.post("/api/chat")
async def api_chat(
    message: str = Form(...),
    session_id: str = Form("default")
):
    """API endpoint for chat functionality"""
    result = gemini_suite.process_chat_message(message, session_id)
    return JSONResponse(content=result)

@app.get("/api/chat-history/{session_id}")
async def api_chat_history(session_id: str = "default"):
    """API endpoint to get chat history"""
    result = gemini_suite.get_chat_history(session_id)
    return JSONResponse(content=result)

@app.post("/api/generate-code")
async def api_generate_code(query: str = Form(...)):
    """API endpoint to generate code"""
    result = gemini_suite.run_code_analysis(query)
    return JSONResponse(content=result)

@app.get("/api/image-history")
async def api_image_history():
    """API endpoint to get image analysis history"""
    result = gemini_suite.get_image_history()
    return JSONResponse(content=result)

@app.get("/api/code-history")
async def api_code_history():
    """API endpoint to get code generation history"""
    result = gemini_suite.get_code_history()
    return JSONResponse(content=result)

# Run the application
if _name_ == "_main_":
    # Create basic template files if they don't exist
    templates_dir = Path("templates")
    templates_dir.mkdir(exist_ok=True)
    
    # Create static directory for css/js files
    static_dir = Path("static")
    static_dir.mkdir(exist_ok=True)
    
    # Example of creating a basic template file if it doesn't exist
    index_template = templates_dir / "index.html"
    if not index_template.exists():
        with open(index_template, "w") as f:
            f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gemini AI Suite</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <div class="container">
        <h1>Welcome to Gemini AI Suite</h1>
        <div class="menu">
            <a href="/image-analyzer" class="card">
                <h2>Image Analyzer</h2>
                <p>Analyze images using Google's Gemini AI</p>
            </a>
            <a href="/chat" class="card">
                <h2>AI Chat</h2>
                <p>Talk with Gemini AI Assistant</p>
            </a>
            <a href="/code-generator" class="card">
                <h2>Code Generator</h2>
                <p>Generate code with AI assistance</p>
            </a>
        </div>
    </div>
    <script src="/static/main.js"></script>
</body>
</html>""")
    
    # Create a basic CSS file
    css_file = static_dir / "style.css"
    if not css_file.exists():
        with open(css_file, "w") as f:
            f.write("""
* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    background: #E6F3FF;
    color: #333;
}

.container {
    width: 90%;
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

h1 {
    text-align: center;
    margin: 30px 0;
    color: #2E5090;
}

.menu {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    margin-top: 30px;
}

.card {
    background: white;
    border-radius: 8px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    padding: 20px;
    margin: 15px 0;
    width: 30%;
    min-width: 300px;
    text-decoration: none;
    color: #333;
    transition: transform 0.3s ease;
}

.card:hover {
    transform: translateY(-5px);
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
}

h2 {
    color: #4F9BE8;
    margin-bottom: 10px;
}

p {
    color: #666;
}

/* Responsive adjustments */
@media (max-width: 992px) {
    .menu {
        justify-content: center;
    }
    .card {
        width: 45%;
    }
}

@media (max-width: 768px) {
    .card {
        width: 100%;
    }
}
            """)
    
    # Run the FastAPI application
    print("Starting Gemini AI Suite Web Application...")
    uvicorn.run(app, host="0.0.0.0", port=8000)