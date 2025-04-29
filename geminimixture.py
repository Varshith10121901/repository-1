import os
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox, ttk, Menu, font
from PIL import Image, ImageTk
import threading
import mysql.connector
from datetime import datetime
import google.generativeai as genai
import webbrowser
from dotenv import load_dotenv


class GeminiAISuite:
    def __init__(self, root):
        self.root = root
        self.root.title("Gemini AI Suite")
        self.root.geometry("900x650")
        
        # Load environment variables and configure API
        load_dotenv()
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
        else:
            messagebox.showwarning("Warning", "GEMINI_API_KEY not found in environment variables.")
        
        # Initialize variables
        self.selected_image_path = None
        self.chat_model = genai.GenerativeModel("gemini-2.0-flash")
        self.chat = self.chat_model.start_chat()
        self.chat_history = []
        
        # Configure UI
        self.setup_ui()
        self.setup_database()
    
    def setup_ui(self):
        """Configure the user interface"""
        # Set theme and styles
        self.root.configure(bg="#E6F3FF")  # Light blue background
        self.setup_fonts()
        self.setup_styles()
        
        # Create main notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create menu and tabs
        self.create_menu()
        self.create_image_analyzer_tab()
        self.create_chat_tab()
        self.create_code_analyzer_tab()
        
        # Create status bar
        self.status = tk.StringVar(value="Ready")
        tk.Label(self.root, textvariable=self.status, bd=1, 
                 relief=tk.SUNKEN, anchor=tk.W, bg="#E6F3FF",
                 fg="#333333", font=("Segoe UI", 9)).pack(side=tk.BOTTOM, fill=tk.X)
    
    def setup_fonts(self):
        """Configure default fonts"""
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(family="Segoe UI", size=10)
        self.root.option_add("*Font", default_font)
        
        # Create named fonts for consistent use
        self.title_font = font.Font(family="Segoe UI", size=12, weight="bold")
        self.header_font = font.Font(family="Segoe UI", size=11, weight="bold")
        self.text_font = font.Font(family="Segoe UI", size=10)
    
    def setup_styles(self):
        """Configure ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Define colors
        bg_color = "#E6F3FF"  # Light blue
        accent_color = "#4F9BE8"  # Medium blue
        hover_color = "#3D7AB6"  # Dark blue
        
        # Configure widget styles
        style.configure('TNotebook', background=bg_color)
        style.configure('TNotebook.Tab', background=bg_color, padding=[10, 2])
        style.map('TNotebook.Tab', background=[('selected', accent_color), 
                                              ('active', hover_color)])
        
        style.configure('TFrame', background=bg_color)
        style.configure('TButton', background=accent_color, foreground='white')
        style.map('TButton', background=[('active', hover_color)])
        style.configure('TLabel', background=bg_color)
        style.configure('TCombobox', fieldbackground='white', background=accent_color)
    
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
            messagebox.showerror("Database Error", 
                               f"Could not connect to database: {err}\n\n"
                               "Application will continue without saving history.")
            self.conn = None
    
    def create_menu(self):
        """Create application menu bar"""
        menubar = Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Select Image", command=self.select_image)
        file_menu.add_command(label="Save Results", command=self.save_results)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Create specific module menus
        module_menus = {
            "Image Analysis": [
                ("Analyze Current Image", self.analyze_image),
                ("View Image History", lambda: self.view_history("image"))
            ],
            "Code Analysis": [
                ("Run Code Analysis", self.run_code_analysis),
                ("View Code History", lambda: self.view_history("code"))
            ],
            "Chat": [
                ("Clear Chat", self.clear_chat),
                ("Save Chat History", self.save_chat),
                ("View Chat History", lambda: self.view_history("chat"))
            ]
        }
        
        for menu_name, commands in module_menus.items():
            module_menu = Menu(menubar, tearoff=0)
            menubar.add_cascade(label=menu_name, menu=module_menu)
            for label, command in commands:
                module_menu.add_command(label=label, command=command)
        
        # Prompt menu
        prompt_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Prompts", menu=prompt_menu)
        prompts = {
            "General Description": "What is in this image? Provide a detailed description.",
            "Detailed Analysis": "Analyze this image in detail. Describe elements, colors, and meanings.",
            "Object Detection": "Identify and list all objects visible in this image.",
            "Scene Understanding": "Describe the scene in this image. What's happening?"
        }
        
        for prompt_name, prompt_text in prompts.items():
            prompt_menu.add_command(
                label=prompt_name, 
                command=lambda p=prompt_name, t=prompt_text: self.set_prompt(p, t)
            )
        
        # View menu for navigating tabs
        view_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Image Analyzer", command=lambda: self.notebook.select(0))
        view_menu.add_command(label="Chat Interface", command=lambda: self.notebook.select(1))
        view_menu.add_command(label="Code Analyzer", command=lambda: self.notebook.select(2))
        
        # Help menu
        help_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Documentation", command=self.show_documentation)
        help_menu.add_command(label="Web Interface", 
                             command=lambda: webbrowser.open('aura3.html'))
    
    def create_image_analyzer_tab(self):
        """Create the Image Analyzer tab"""
        self.image_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.image_tab, text="Image Analyzer")
        
        # Top frame for image selection
        top_frame = ttk.Frame(self.image_tab)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(top_frame, text="Select Image", command=self.select_image).pack(side=tk.LEFT, padx=5)
        self.path_label = ttk.Label(top_frame, text="No image selected")
        self.path_label.pack(side=tk.LEFT, padx=5)
        
        # Main content frame
        content_frame = ttk.Frame(self.image_tab)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Left panel: Image preview
        preview_frame = ttk.Frame(content_frame, width=400)
        preview_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        preview_label = ttk.Label(preview_frame, text="Image Preview", font=self.header_font)
        preview_label.pack(pady=(0, 5))
        
        self.image_preview = ttk.Label(preview_frame, text="Select an image to preview")
        self.image_preview.pack(pady=10, expand=True)
        
        # Right panel: Analysis results
        results_frame = ttk.Frame(content_frame, width=400)
        results_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        results_label = ttk.Label(results_frame, text="Analysis Results", font=self.header_font)
        results_label.pack(anchor=tk.W)
        
        self.result_text = scrolledtext.ScrolledText(
            results_frame, wrap=tk.WORD, font=self.text_font, height=15
        )
        self.result_text.pack(fill=tk.BOTH, expand=True)
        
        # Bottom frame: Prompt selection and analyze button
        bottom_frame = ttk.Frame(self.image_tab)
        bottom_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(bottom_frame, text="Prompt:").pack(side=tk.LEFT)
        
        self.prompt_type = tk.StringVar(value="General Description")
        prompts = ["General Description", "Detailed Analysis", "Object Detection", 
                  "Scene Understanding", "Custom Prompt"]
        
        self.prompt_combo = ttk.Combobox(bottom_frame, textvariable=self.prompt_type, 
                                        values=prompts, width=20)
        self.prompt_combo.pack(side=tk.LEFT, padx=5)
        self.prompt_combo.bind("<<ComboboxSelected>>", self.update_prompt)
        
        self.prompt_entry = ttk.Entry(bottom_frame, width=50)
        self.prompt_entry.insert(0, "What is in this image? Provide a detailed description.")
        self.prompt_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.analyze_btn = ttk.Button(bottom_frame, text="Analyze Image", 
                                     command=self.analyze_image, state=tk.DISABLED)
        self.analyze_btn.pack(side=tk.LEFT, padx=5, pady=5)
    
    def create_chat_tab(self):
        """Create the Chat tab"""
        self.chat_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.chat_tab, text="Chat")
        
        # Header with app title
        header_frame = ttk.Frame(self.chat_tab)
        header_frame.pack(fill=tk.X, pady=(10, 5))
        
        ttk.Label(header_frame, text="AURA AI Chat", 
                 font=self.title_font).pack(side=tk.LEFT, padx=10)
        
        # Chat display area
        chat_frame = ttk.Frame(self.chat_tab)
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame, wrap=tk.WORD, font=self.text_font, 
            background="#f0f7ff", relief=tk.FLAT, borderwidth=1
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        
        # Configure text tags for different message types
        self.chat_display.tag_configure("user", foreground="#1a73e8", font=("Segoe UI", 10, "bold"))
        self.chat_display.tag_configure("bot", foreground="#0f9d58", font=("Segoe UI", 10))
        self.chat_display.tag_configure("system", foreground="#5f6368", font=("Segoe UI", 9, "italic"))
        
        # Message input area
        input_frame = ttk.Frame(self.chat_tab)
        input_frame.pack(fill=tk.X, padx=10, pady=(5, 10))
        
        self.chat_input = scrolledtext.ScrolledText(
            input_frame, height=3, font=self.text_font, 
            relief=tk.FLAT, borderwidth=1
        )
        self.chat_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.chat_input.bind("<Return>", self.handle_return)
        
        self.send_button = ttk.Button(
            input_frame, text="Send", command=self.send_message
        )
        self.send_button.pack(side=tk.RIGHT)
        
        # Initial welcome message
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, "AURA AI: Welcome! How can I help you today?\n\n", "bot")
        self.chat_display.config(state=tk.DISABLED)
    
    def create_code_analyzer_tab(self):
        """Create the Code Analyzer tab"""
        self.code_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.code_tab, text="Code Analyzer")
        
        # Query input section
        query_frame = ttk.Frame(self.code_tab)
        query_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(query_frame, text="Code Query:", font=self.header_font).pack(anchor=tk.W)
        
        self.code_query = scrolledtext.ScrolledText(
            query_frame, height=4, font=self.text_font, wrap=tk.WORD
        )
        self.code_query.insert(tk.END, "Generate a Python code to create a simple calculator.")
        self.code_query.pack(fill=tk.X, pady=5)
        
        # Buttons frame
        btn_frame = ttk.Frame(self.code_tab)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(btn_frame, text="Generate Code", 
                  command=self.run_code_analysis).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Clear Results", 
                  command=self.clear_code_results).pack(side=tk.LEFT)
        
        # Results section
        results_label = ttk.Label(self.code_tab, text="Results:", font=self.header_font)
        results_label.pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        self.code_results = scrolledtext.ScrolledText(
            self.code_tab, height=20, wrap=tk.WORD, font=("Consolas", 10)
        )
        self.code_results.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    def set_prompt(self, prompt_type, prompt_text):
        """Set the prompt type and text"""
        self.prompt_type.set(prompt_type)
        self.prompt_entry.delete(0, tk.END)
        self.prompt_entry.insert(0, prompt_text)
    
    def update_prompt(self, event=None):
        """Update prompt text based on selected prompt type"""
        prompt_templates = {
            "General Description": "What is in this image? Provide a detailed description.",
            "Detailed Analysis": "Analyze this image in detail. Describe elements, colors, and meanings.",
            "Object Detection": "Identify and list all objects visible in this image.",
            "Scene Understanding": "Describe the scene in this image. What's happening?",
            "Custom Prompt": ""
        }
        
        selected = self.prompt_type.get()
        if selected in prompt_templates:
            self.prompt_entry.delete(0, tk.END)
            self.prompt_entry.insert(0, prompt_templates[selected])
    
    def select_image(self):
        """Open file dialog to select an image"""
        self.notebook.select(0)  # Switch to image tab
        
        filetypes = (
            ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp"),
            ("All files", "*.*")
        )
        
        path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=filetypes
        )
        
        if path:
            self.selected_image_path = path
            self.path_label.config(text=os.path.basename(path))
            self.display_image(path)
            self.update_analyze_button()
            self.status.set(f"Image selected: {os.path.basename(path)}")
    
    def display_image(self, path):
        """Display the selected image in the preview area"""
        try:
            # Open and resize image
            img = Image.open(path)
            width, height = img.size
            
            # Calculate size to fit in preview area (max 300px)
            max_size = 300
            ratio = min(max_size/width, max_size/height)
            new_size = (int(width*ratio), int(height*ratio))
            
            # Resize and display
            img = img.resize(new_size, Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            
            self.image_preview.config(image=photo, text="")
            self.image_preview.image = photo  # Keep a reference
        except Exception as e:
            self.image_preview.config(text=f"Error loading image:\n{str(e)}")
            self.status.set("Error loading image")
    
    def update_analyze_button(self):
        """Enable/disable analyze button based on selection and API key"""
        if self.api_key and self.selected_image_path:
            self.analyze_btn.config(state=tk.NORMAL)
        else:
            self.analyze_btn.config(state=tk.DISABLED)
    
    def analyze_image(self):
        """Analyze the selected image using Gemini AI"""
        if not self.api_key:
            messagebox.showerror("Error", "API key not found. Please set GEMINI_API_KEY in your environment.")
            return
            
        if not self.selected_image_path:
            messagebox.showerror("Error", "No image selected.")
            return
        
        # Disable button during analysis
        self.analyze_btn.config(state=tk.DISABLED)
        self.status.set("Analyzing image...")
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "Processing...\n")
        
        # Run analysis in a separate thread
        threading.Thread(target=self.process_image_analysis, daemon=True).start()
    
    def process_image_analysis(self):
        """Process image analysis in a background thread"""
        prompt = self.prompt_entry.get().strip()
        
        try:
            # Initialize the model
            vision_model = genai.GenerativeModel("gemini-2.0-flash")
            
            # Open the image and generate content
            image = Image.open(self.selected_image_path)
            response = vision_model.generate_content([prompt, image])
            result = response.text
            
            # Update UI from the main thread
            self.root.after(0, lambda: self.update_analysis_results(result))
            self.root.after(0, lambda: self.status.set("Analysis complete"))
            
            # Save to database if connected
            if self.conn:
                self.save_to_database("image", prompt=prompt, result=result)
                
        except Exception as e:
            error_message = f"Error during analysis: {str(e)}"
            self.root.after(0, lambda: self.update_analysis_results(error_message))
            self.root.after(0, lambda: self.status.set("Analysis failed"))
        
        # Re-enable the analyze button
        self.root.after(0, lambda: self.analyze_btn.config(state=tk.NORMAL))
    
    def update_analysis_results(self, result):
        """Update the results text area with the analysis"""
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, result)
    
    def handle_return(self, event):
        """Handle the Return key in the chat input"""
        if not (event.state & 0x1):  # Not Shift+Enter
            self.send_message()
            return "break"  # Prevent default behavior
        return None  # Allow Shift+Enter for new line
    
    def send_message(self):
        """Send user message to the chatbot"""
        message = self.chat_input.get("1.0", tk.END).strip()
        if not message:
            return
        
        # Clear input
        self.chat_input.delete("1.0", tk.END)
        
        # Display user message
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"You: {message}\n", "user")
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
        
        # Update status and disable send button
        self.status.set("Getting response...")
        self.send_button.config(state=tk.DISABLED)
        
        # Process in background thread
        threading.Thread(target=self.process_chat_message, args=(message,), daemon=True).start()
    
    def process_chat_message(self, message):
        """Process chat message in a background thread"""
        try:
            # Special commands
            if message.lower() in ['bye', 'exit', 'quit']:
                response = "Goodbye! Feel free to come back anytime."
            elif message.lower() in ['who are you', 'what are you', 'tell about yourself']:
                response = "I am Aura AI, a virtual assistant powered by Google's Gemini model and trained by the Aurafied group."
            else:
                # Get response from Gemini
                api_response = self.chat.send_message(message)
                response = api_response.text
            
            # Add to chat history and save to database
            self.chat_history.append({"user": message, "bot": response})
            if self.conn:
                self.save_to_database("chat", user_message=message, bot_response=response)
            
            # Update UI from main thread
            self.root.after(0, lambda: self.display_bot_response(response))
            
        except Exception as e:
            error_msg = f"Sorry, I encountered an error: {str(e)}"
            self.root.after(0, lambda: self.display_bot_response(error_msg))
    
    def display_bot_response(self, response):
        """Display the bot's response in the chat window"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"AURA AI: {response}\n\n", "bot")
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
        
        # Reset status and enable send button
        self.status.set("Ready")
        self.send_button.config(state=tk.NORMAL)
        self.chat_input.focus_set()
    
    def clear_chat(self):
        """Clear the chat display and reset history"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete(1.0, tk.END)
        self.chat_display.insert(tk.END, "AURA AI: Chat history cleared. How can I help you today?\n\n", "bot")
        self.chat_display.config(state=tk.DISABLED)
        self.chat_history = []
        self.chat = self.chat_model.start_chat()  # Reset chat session
    
    def run_code_analysis(self):
        """Generate code based on user query"""
        if not self.api_key:
            messagebox.showerror("Error", "API key not found. Please set GEMINI_API_KEY in your environment.")
            return
        
        query = self.code_query.get("1.0", tk.END).strip()
        if not query:
            messagebox.showerror("Error", "Please enter a code query.")
            return
        
        # Update UI
        self.status.set("Generating code...")
        self.code_results.delete(1.0, tk.END)
        self.code_results.insert(tk.END, "Processing your request...\n")
        
        # Process in background thread
        threading.Thread(target=self.process_code_query, args=(query,), daemon=True).start()
    
    def process_code_query(self, query):
        """Process code query in a background thread"""
        try:
            # Call Gemini API
            model = genai.GenerativeModel('gemini-2.0-flash')
            response = model.generate_content(query)
            result = response.text
            
            # Update UI from main thread
            self.root.after(0, lambda: self.update_code_results(result))
            self.root.after(0, lambda: self.status.set("Code generation complete"))
            
            # Save to database if connected
            if self.conn:
                self.save_to_database("code", query=query, result=result)
                
        except Exception as e:
            error_message = f"Error generating code: {str(e)}"
            self.root.after(0, lambda: self.update_code_results(error_message))
            self.root.after(0, lambda: self.status.set("Code generation failed"))
    
    def update_code_results(self, result):
        """Update the code results area"""
        self.code_results.delete(1.0, tk.END)
        self.code_results.insert(tk.END, result)
    
    def clear_code_results(self):
        """Clear the code results area"""
        self.code_results.delete(1.0, tk.END)
    
    def save_to_database(self, record_type, **data):
        """Save data to the appropriate database table"""
        if not self.conn:
            return
            
        try:
            cursor = self.conn.cursor()
            
            if record_type == "image":
                cursor.execute(
                    "INSERT INTO image_table (image_path, prompt, analysis_result, analysis_date) "
                    "VALUES (%s, %s, %s, NOW())",
                    (self.selected_image_path, data['prompt'], data['result'])
                )
            elif record_type == "chat":
                cursor.execute(
                    "INSERT INTO chatbot_table (user_message, bot_response, chat_date) "
                    "VALUES (%s, %s, NOW())",
                    (data['user_message'], data['bot_response'])
                )
            elif record_type == "code":
                cursor.execute(
                    "INSERT INTO coding_table (query, code_result, execution_result, analysis_date) "
                    "VALUES (%s, %s, %s, NOW())",
                    (data['query'], data['result'], None)
                )
                
            self.conn.commit()
            cursor.close()
            
        except mysql.connector.Error as err:
            print(f"Database error: {err}")
    
    def save_results(self):
        """Save results from the current tab to a file"""
        current_tab = self.notebook.index(self.notebook.select())
        
        # Get content based on the selected tab
        if current_tab == 0:  # Image analyzer
            content = self.result_text.get(1.0, tk.END).strip()
            file_type = "Image Analysis Results"
        elif current_tab == 1:  # Chat
            content = self.chat_display.get(1.0, tk.END).strip()
            file_type = "Chat History"
        else:  # Code analyzer
            content = self.code_results.get(1.0, tk.END).strip()
            file_type = "Code Analysis Results"
        
        if not content:
            messagebox.showinfo("Info", f"No {file_type.lower()} to save.")
            return
        
        # Ask for save location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(content)
                messagebox.showinfo("Success", f"{file_type} saved successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {str(e)}")
    
    def save_chat(self):
        """Save chat history (shortcut method)"""
        self.notebook.select(1)  # Switch to chat tab
        self.save_results()
    
    def view_history(self, history_type):
        """View history of specified type in a popup window"""
        if not self.conn:
            messagebox.showerror("Error", "Database connection not available.")
        
        return
        
        history_window = tk.Toplevel(self.root)
        history_window.title(f"{history_type.title()} History")
        history_window.geometry("800x600")
        
        # Create a treeview for the history entries
        columns = {
            "image": ["id", "date", "image", "prompt", "result"],
            "chat": ["id", "date", "message", "response"],
            "code": ["id", "date", "query", "result"]
        }
        
        tree_frame = ttk.Frame(history_window)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns_for_type = columns.get(history_type, ["id"])
        tree = ttk.Treeview(tree_frame, columns=columns_for_type, show="headings")
        
        # Configure headings
        headings = {
            "id": "#",
            "date": "Date & Time",
            "image": "Image Path",
            "prompt": "Prompt",
            "result": "Result",
            "message": "User Message",
            "response": "Bot Response",
            "query": "Code Query"
        }
        
        for col in columns_for_type:
            tree.heading(col, text=headings.get(col, col))
            tree.column(col, width=100)
        
        # Adjust column widths
        if history_type == "image":
            tree.column("id", width=40)
            tree.column("date", width=150)
            tree.column("image", width=200)
            tree.column("prompt", width=150)
            tree.column("result", width=200)
        elif history_type == "chat":
            tree.column("id", width=40)
            tree.column("date", width=150)
            tree.column("message", width=250)
            tree.column("response", width=300)
        elif history_type == "code":
            tree.column("id", width=40)
            tree.column("date", width=150)
            tree.column("query", width=250)
            tree.column("result", width=300)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Load data from database
        try:
            cursor = self.conn.cursor()
            
            if history_type == "image":
                cursor.execute(
                    "SELECT id, analysis_date, image_path, prompt, analysis_result "
                    "FROM image_table ORDER BY analysis_date DESC"
                )
            elif history_type == "chat":
                cursor.execute(
                    "SELECT id, chat_date, user_message, bot_response "
                    "FROM chatbot_table ORDER BY chat_date DESC"
                )
            elif history_type == "code":
                cursor.execute(
                    "SELECT id, analysis_date, query, code_result "
                    "FROM coding_table ORDER BY analysis_date DESC"
                )
            
            for row in cursor.fetchall():
                # Format the data for display
                display_row = []
                for i, item in enumerate(row):
                    # Truncate long text for display
                    if isinstance(item, str) and len(item) > 50:
                        display_row.append(f"{item[:50]}...")
                    else:
                        display_row.append(item)
                        
                tree.insert("", tk.END, values=display_row)
            
            cursor.close()
            
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Could not retrieve history: {err}")
        
        # Add detail view for selected item
        detail_frame = ttk.LabelFrame(history_window, text="Details")
        detail_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        detail_text = scrolledtext.ScrolledText(detail_frame, height=10, wrap=tk.WORD)
        detail_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Function to show details when item selected
        def on_item_select(event):
            selected_items = tree.selection()
            if not selected_items:
                return
                
            item_id = tree.item(selected_items[0], "values")[0]
            
            try:
                cursor = self.conn.cursor()
                
                if history_type == "image":
                    cursor.execute(
                        "SELECT image_path, prompt, analysis_result, analysis_date "
                        "FROM image_table WHERE id = %s",
                        (item_id,)
                    )
                    row = cursor.fetchone()
                    if row:
                        detail_text.delete(1.0, tk.END)
                        detail_text.insert(tk.END, f"Date: {row[3]}\n\n")
                        detail_text.insert(tk.END, f"Image: {row[0]}\n\n")
                        detail_text.insert(tk.END, f"Prompt: {row[1]}\n\n")
                        detail_text.insert(tk.END, f"Analysis Result:\n{row[2]}")
                        
                elif history_type == "chat":
                    cursor.execute(
                        "SELECT user_message, bot_response, chat_date "
                        "FROM chatbot_table WHERE id = %s",
                        (item_id,)
                    )
                    row = cursor.fetchone()
                    if row:
                        detail_text.delete(1.0, tk.END)
                        detail_text.insert(tk.END, f"Date: {row[2]}\n\n")
                        detail_text.insert(tk.END, f"User: {row[0]}\n\n")
                        detail_text.insert(tk.END, f"AURA AI: {row[1]}")
                        
                elif history_type == "code":
                    cursor.execute(
                        "SELECT query, code_result, execution_result, analysis_date "
                        "FROM coding_table WHERE id = %s",
                        (item_id,)
                    )
                    row = cursor.fetchone()
                    if row:
                        detail_text.delete(1.0, tk.END)
                        detail_text.insert(tk.END, f"Date: {row[3]}\n\n")
                        detail_text.insert(tk.END, f"Query: {row[0]}\n\n")
                        detail_text.insert(tk.END, f"Code Result:\n{row[1]}\n\n")
                        if row[2]:
                            detail_text.insert(tk.END, f"Execution Result:\n{row[2]}")
                
                cursor.close()
                
            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Could not retrieve details: {err}")
        
        tree.bind("<<TreeviewSelect>>", on_item_select)
        
        # Add buttons for actions
        button_frame = ttk.Frame(history_window)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(
            button_frame, text="Export Selected", 
            command=lambda: self.export_history_item(tree, history_type)
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame, text="Delete Selected", 
            command=lambda: self.delete_history_item(tree, history_type)
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame, text="Refresh", 
            command=lambda: self.view_history(history_type)
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame, text="Close", 
            command=history_window.destroy
        ).pack(side=tk.RIGHT, padx=5)
    
    def export_history_item(self, tree, history_type):
        """Export selected history item to a file"""
        selected_items = tree.selection()
        if not selected_items:
            messagebox.showinfo("Info", "No item selected.")
            return
            
        item_id = tree.item(selected_items[0], "values")[0]
        
        try:
            cursor = self.conn.cursor()
            
            if history_type == "image":
                cursor.execute(
                    "SELECT image_path, prompt, analysis_result, analysis_date "
                    "FROM image_table WHERE id = %s",
                    (item_id,)
                )
                row = cursor.fetchone()
                if row:
                    content = f"Date: {row[3]}\n\nImage: {row[0]}\n\nPrompt: {row[1]}\n\nAnalysis Result:\n{row[2]}"
                    default_filename = f"image_analysis_{item_id}.txt"
                    
            elif history_type == "chat":
                cursor.execute(
                    "SELECT user_message, bot_response, chat_date "
                    "FROM chatbot_table WHERE id = %s",
                    (item_id,)
                )
                row = cursor.fetchone()
                if row:
                    content = f"Date: {row[2]}\n\nUser: {row[0]}\n\nAURA AI: {row[1]}"
                    default_filename = f"chat_{item_id}.txt"
                    
            elif history_type == "code":
                cursor.execute(
                    "SELECT query, code_result, execution_result, analysis_date "
                    "FROM coding_table WHERE id = %s",
                    (item_id,)
                )
                row = cursor.fetchone()
                if row:
                    content = f"Date: {row[3]}\n\nQuery: {row[0]}\n\nCode Result:\n{row[1]}"
                    if row[2]:
                        content += f"\n\nExecution Result:\n{row[2]}"
                    default_filename = f"code_analysis_{item_id}.txt"
            
            cursor.close()
            
            # Save to file
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                initialfile=default_filename
            )
            
            if file_path:
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(content)
                messagebox.showinfo("Success", "Item exported successfully.")
                
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Could not export item: {err}")
    
    def delete_history_item(self, tree, history_type):
        """Delete selected history item from database"""
        selected_items = tree.selection()
        if not selected_items:
            messagebox.showinfo("Info", "No item selected.")
            return
            
        item_id = tree.item(selected_items[0], "values")[0]
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm", "Are you sure you want to delete this item?"):
            return
            
        try:
            cursor = self.conn.cursor()
            
            if history_type == "image":
                cursor.execute("DELETE FROM image_table WHERE id = %s", (item_id,))
            elif history_type == "chat":
                cursor.execute("DELETE FROM chatbot_table WHERE id = %s", (item_id,))
            elif history_type == "code":
                cursor.execute("DELETE FROM coding_table WHERE id = %s", (item_id,))
            
            self.conn.commit()
            cursor.close()
            
            # Remove from tree
            tree.delete(selected_items[0])
            messagebox.showinfo("Success", "Item deleted successfully.")
            
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Could not delete item: {err}")
    
    def show_about(self):
        """Show about dialog with application info"""
        about_text = """
        Gemini AI Suite

        Version: 1.0.0
        
        A powerful application that integrates Google's 
        Gemini AI for image analysis, natural language 
        chatting, and code generation.
        
        Developed by: Aurafied Group
        """
        
        about_window = tk.Toplevel(self.root)
        about_window.title("About Gemini AI Suite")
        about_window.geometry("400x300")
        about_window.resizable(False, False)
        
        # Create a frame with a light blue background
        frame = ttk.Frame(about_window)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Add logo or icon (placeholder)
        logo_label = ttk.Label(frame, text="AURA AI", font=("Segoe UI", 24, "bold"))
        logo_label.pack(pady=(0, 20))
        
        # Add about text
        ttk.Label(
            frame, text=about_text, 
            justify=tk.CENTER, font=self.text_font
        ).pack(pady=10)
        
        # Add OK button
        ttk.Button(
            frame, text="OK", command=about_window.destroy, width=10
        ).pack(pady=10)
    
    def show_documentation(self):
        """Show documentation or open documentation in browser"""
        # Option 1: Open help in browser
        try:
            webbrowser.open('https://gemini.google.com/app')
        except Exception as e:
            messagebox.showerror("Error", f"Could not open documentation: {str(e)}")
            
        # Option 2: Display help in application
        # help_text = """
        # # Gemini AI Suite Documentation
        # 
        # ## Image Analyzer
        # 1. Select an image using the "Select Image" button
        # 2. Choose a prompt type or enter a custom prompt
        # 3. Click "Analyze Image" to get AI-powered image analysis
        # 
        # ## Chat Interface
        # Simply type your message in the input area and press Enter or 
        # click Send to chat with the AI assistant.
        # 
        # ## Code Analyzer
        # Enter your code query or request and click "Generate Code" to
        # get AI-generated code samples and explanations.
        # """
        # 
        # help_window = tk.Toplevel(self.root)
        # help_window.title("Documentation")
        # help_window.geometry("700x500")
        # 
        # help_display = scrolledtext.ScrolledText(
        #     help_window, wrap=tk.WORD, font=self.text_font
        # )
        # help_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        # help_display.insert(tk.END, help_text)
        # help_display.config(state=tk.DISABLED)


def main():
    """Main application entry point"""
    root = tk.Tk()
    app = GeminiAISuite(root)
    root.mainloop()
    
    # Close database connection when app closes
    if hasattr(app, 'conn') and app.conn:
        app.conn.close()


if __name__ == "__main__":
    main()
