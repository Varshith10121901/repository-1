import os
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox, ttk, Menu, font
import PIL.Image
from PIL import ImageTk
import threading
import mysql.connector
from datetime import datetime
import google.generativeai as genai
import webbrowser


class GeminiApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gemini AI Suite")
        self.root.geometry("900x650")
        self.root.configure(bg="#f5f5f5")
        
        self.api_key = "AIzaSyCvyxvEZcBh2x8VRFUCFDZqeoIMCWjwYzo"
        genai.configure(api_key=self.api_key)
        
        self.selected_image_path = None
        self.chat_history = []
        self.chat_model = genai.GenerativeModel("gemini-2.0-flash")
        self.chat = self.chat_model.start_chat()
        
        self.default_font = font.nametofont("TkDefaultFont")
        self.default_font.configure(size=11)
        self.root.option_add("*Font", self.default_font)
        
        self.setup_database()
        
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.create_menu()
        self.create_image_analyzer_tab()
        self.create_chat_tab()
        
        self.status = tk.StringVar(value="Ready")
        tk.Label(self.root, textvariable=self.status, bd=1, 
                relief=tk.SUNKEN, anchor=tk.W, bg="#f5f5f5",
                fg="#666666", font=("Arial", 9)).pack(side=tk.BOTTOM, fill=tk.X)
    
    def setup_database(self):
        try:
            self.conn = mysql.connector.connect(
                host='localhost', user='root', password='1234', database='tommy'
            )
            cursor = self.conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS image_analyses (
                id INT AUTO_INCREMENT PRIMARY KEY,
                image_path VARCHAR(255) NOT NULL,
                prompt TEXT NOT NULL,
                analysis_result TEXT NOT NULL,
                analysis_date DATETIME NOT NULL
            )
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_message TEXT NOT NULL,
                bot_response TEXT NOT NULL,
                chat_date DATETIME NOT NULL
            )
            """)
            self.conn.commit()
            cursor.close()
            print("Database connected")
        except mysql.connector.Error as err:
            print(f"Database error: {err}")
            messagebox.showerror("Database Error", str(err))

    def create_menu(self):
        menubar = Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Select Image", command=self.select_image)
        file_menu.add_command(label="Save Results", command=self.save_results)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        image_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Image Analysis", menu=image_menu)
        image_menu.add_command(label="Analyze Current Image", command=self.analyze_image)
        image_menu.add_command(label="View Image History", command=self.view_image_history)
        
        prompt_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Prompts", menu=prompt_menu)
        prompt_menu.add_command(label="General Description", 
                               command=lambda: self.set_prompt("General Description"))
        prompt_menu.add_command(label="Detailed Analysis", 
                               command=lambda: self.set_prompt("Detailed Analysis"))
        prompt_menu.add_command(label="Object Detection", 
                               command=lambda: self.set_prompt("Object Detection"))
        prompt_menu.add_command(label="Scene Understanding", 
                               command=lambda: self.set_prompt("Scene Understanding"))
        
        chat_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Chat", menu=chat_menu)
        chat_menu.add_command(label="Clear Chat", command=self.clear_chat)
        chat_menu.add_command(label="Save Chat History", command=self.save_chat)
        chat_menu.add_command(label="View Chat History", command=self.view_chat_history)
        
        view_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Image Analyzer", command=lambda: self.notebook.select(0))
        view_menu.add_command(label="Chat Interface", command=lambda: self.notebook.select(1))
        
        help_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Documentation", command=self.show_documentation)
        help_menu.add_command(label="Open Web Interface", command=lambda: webbrowser.open('aura ultrafinal.html'))

    def create_image_analyzer_tab(self):
        self.image_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.image_tab, text="Image Analyzer")
        
        img_frame = tk.Frame(self.image_tab, pady=5, bg="#f5f5f5")
        img_frame.pack(fill=tk.X)
        
        tk.Button(img_frame, text="Select Image", command=self.select_image).pack(side=tk.LEFT, padx=5)
        self.path_label = tk.Label(img_frame, text="No image selected", bg="#f5f5f5")
        self.path_label.pack(side=tk.LEFT, padx=5)
        
        content_frame = tk.Frame(self.image_tab, bg="#f5f5f5")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        preview_frame = tk.Frame(content_frame, width=400, bg="#f0f0f0")
        preview_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self.image_label = tk.Label(preview_frame, text="Image preview", bg="#f0f0f0")
        self.image_label.pack(pady=10, expand=True)
        
        results_frame = tk.Frame(content_frame, width=400, bg="#f5f5f5")
        results_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        tk.Label(results_frame, text="Analysis Results:", bg="#f5f5f5").pack(anchor=tk.W)
        self.result_text = scrolledtext.ScrolledText(
            results_frame, wrap=tk.WORD, bg="white", fg="#333333", font=("Arial", 11)
        )
        self.result_text.pack(fill=tk.BOTH, expand=True)
        
        prompt_frame = tk.Frame(self.image_tab, pady=5, bg="#f5f5f5")
        prompt_frame.pack(fill=tk.X, padx=10)
        
        self.prompt_type = tk.StringVar(value="General Description")
        prompts = ["General Description", "Detailed Analysis", "Object Detection", 
                  "Scene Understanding", "Custom Prompt"]
        
        tk.Label(prompt_frame, text="Prompt:", bg="#f5f5f5").pack(side=tk.LEFT)
        prompt_combo = ttk.Combobox(prompt_frame, textvariable=self.prompt_type, 
                                    values=prompts, width=20)
        prompt_combo.pack(side=tk.LEFT, padx=5)
        prompt_combo.bind("<<ComboboxSelected>>", self.update_prompt)
        
        self.prompt_entry = tk.Entry(prompt_frame, width=50)
        self.prompt_entry.insert(0, "What is in this image? Provide a detailed description.")
        self.prompt_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        button_frame = tk.Frame(self.image_tab, pady=10, bg="#f5f5f5")
        button_frame.pack(fill=tk.X)
        
        self.analyze_btn = tk.Button(button_frame, text="Analyze Image", 
                                    command=self.analyze_image, state=tk.DISABLED)
        self.analyze_btn.pack(side=tk.LEFT, padx=10)

    def create_chat_tab(self):
        self.chat_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.chat_tab, text="Chat")
        
        header_frame = tk.Frame(self.chat_tab, bg="#f5f5f5")
        header_frame.pack(fill=tk.X, pady=(10, 10))
        
        title_label = tk.Label(header_frame, text="AURA AI", 
                             font=("Arial", 16, "bold"), bg="#f5f5f5", fg="#333333")
        title_label.pack(side=tk.LEFT)
        
        chat_frame = tk.Frame(self.chat_tab, bg="#f5f5f5")
        chat_frame.pack(fill=tk.BOTH, expand=True)
        
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame, state=tk.DISABLED, bg="white", fg="#333333",
            font=("Arial", 11), wrap=tk.WORD, relief=tk.FLAT, borderwidth=1
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        
        self.chat_display.tag_configure("user", foreground="#1a73e8", font=("Arial", 11, "bold"))
        self.chat_display.tag_configure("bot", foreground="#0f9d58", font=("Arial", 11))
        
        input_frame = tk.Frame(self.chat_tab, bg="#f5f5f5")
        input_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.input_text = scrolledtext.ScrolledText(
            input_frame, height=4, bg="white", fg="#333333",
            font=("Arial", 11), wrap=tk.WORD, relief=tk.FLAT, borderwidth=1
        )
        self.input_text.pack(fill=tk.X, side=tk.LEFT, expand=True, padx=(0, 10))
        self.input_text.bind("<Return>", self.handle_return)
        
        button_style = ttk.Style()
        button_style.configure("Send.TButton", font=("Arial", 11))
        
        self.send_button = ttk.Button(
            input_frame, text="Send", command=self.send_message, style="Send.TButton"
        )
        self.send_button.pack(side=tk.RIGHT)
        
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, "Gemini Chatbot: Hello! How can I help you today?\n", "bot")
        self.chat_display.config(state=tk.DISABLED)
        
    def set_prompt(self, prompt_type):
        self.prompt_type.set(prompt_type)
        self.update_prompt()
    
    def update_prompt(self, event=None):
        prompts = {
            "General Description": "What is in this image? Provide a detailed description.",
            "Detailed Analysis": "Analyze this image in detail. Describe elements, colors, and meanings.",
            "Object Detection": "Identify and list all objects visible in this image.",
            "Scene Understanding": "Describe the scene in this image. What's happening?",
            "Custom Prompt": ""
        }
        self.prompt_entry.delete(0, tk.END)
        self.prompt_entry.insert(0, prompts[self.prompt_type.get()])
        
    def select_image(self):
        self.notebook.select(0)
        path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=(("Image files", "*.jpg *.jpeg *.png *.gif"), ("All files", "*.*"))
        )
        if path:
            self.selected_image_path = path
            self.path_label.config(text=os.path.basename(path))
            self.display_image(path)
            self.update_button_state()
            self.status.set(f"Selected: {os.path.basename(path)}")

    def display_image(self, path):
        try:
            img = PIL.Image.open(path)
            width, height = img.size
            max_size = 300
            ratio = min(max_size/width, max_size/height)
            new_size = (int(width*ratio), int(height*ratio))
            img = img.resize(new_size, PIL.Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.image_label.config(image=photo, text="")
            self.image_label.image = photo
        except Exception as e:
            self.image_label.config(text=f"Error: {str(e)}")

    def update_button_state(self):
        if self.api_key and self.selected_image_path:
            self.analyze_btn.config(state=tk.NORMAL)
        else:
            self.analyze_btn.config(state=tk.DISABLED)

    def analyze_image(self):
        if not self.api_key or not self.selected_image_path:
            return
            
        self.status.set("Analyzing...")
        self.analyze_btn.config(state=tk.DISABLED)
        threading.Thread(target=self.run_analysis, daemon=True).start()

    def run_analysis(self):
        prompt = self.prompt_entry.get().strip()
        try:
            client = genai.GenerativeModel("gemini-2.0-flash")
            image = PIL.Image.open(self.selected_image_path)
            response = client.generate_content([prompt, image])
            result = response.text
            self.root.after(0, lambda: self.update_results(result))
            self.root.after(0, lambda: self.status.set("Analysis complete"))
        except Exception as e:
            error = f"Error: {str(e)}"
            self.root.after(0, lambda: self.update_results(error))
            self.root.after(0, lambda: self.status.set("Analysis failed"))
        finally:
            self.root.after(0, lambda: self.analyze_btn.config(state=tk.NORMAL))
    
    def update_results(self, result):
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, result)
        self.save_image_analysis_to_db(result)

    def save_image_analysis_to_db(self, result):
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO image_analyses (image_path, prompt, analysis_result, analysis_date) "
                "VALUES (%s, %s, %s, NOW())",
                (self.selected_image_path, self.prompt_entry.get(), result)
            )
            self.conn.commit()
            cursor.close()
        except mysql.connector.Error as err:
            print(f"Database error: {err}")

    def view_image_history(self):
        self.view_history("image")
    
    def handle_return(self, event):
        if not (event.state & 0x1):
            self.send_message()
            return "break"
    
    def send_message(self):
        message = self.input_text.get("1.0", tk.END).strip()
        if not message:
            return
            
        self.input_text.delete("1.0", tk.END)
        
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"You: {message}\n", "user")
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
        
        self.chat_history.append(f"User: {message}")
        self.status.set("Generating response...")
        self.send_button.config(state=tk.DISABLED)
        
        threading.Thread(target=self.process_chat_response, args=(message,), daemon=True).start()
    
    def process_chat_response(self, message):
        try:
            if message.lower() in ['bye', 'exit', 'quit']:
                response_text = "Goodbye! Feel free to come back anytime."
                self.root.after(500, lambda: self.show_chat_response(response_text))
                return
                
            response = self.chat.send_message(message)
            response_text = response.text
            
            self.chat_history.append(f"Chatbot: {response_text}")
            self.save_chat_to_db(message, response_text)
            self.root.after(0, lambda: self.show_chat_response(response_text))
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.root.after(0, lambda: self.show_chat_response(error_msg))
    
    def show_chat_response(self, response_text):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"Gemini: {response_text}\n\n", "bot")
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
        
        self.status.set("Ready")
        self.send_button.config(state=tk.NORMAL)
        self.input_text.focus()
    
    def save_chat_to_db(self, user_message, bot_response):
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO chat_history (user_message, bot_response, chat_date) "
                "VALUES (%s, %s, NOW())",
                (user_message, bot_response)
            )
            self.conn.commit()
            cursor.close()
        except mysql.connector.Error as err:
            print(f"Database error: {err}")
    
    def clear_chat(self):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete(1.0, tk.END)
        self.chat_display.insert(tk.END, "Gemini Chatbot: Chat history cleared. How can I help you today?\n", "bot")
        self.chat_display.config(state=tk.DISABLED)
        self.chat_history = []
    
    def view_chat_history(self):
        self.view_history("chat")
    
    def save_results(self):
        current_tab = self.notebook.index(self.notebook.select())
        
        if current_tab == 0:
            content = self.result_text.get(1.0, tk.END).strip()
            file_type = "Analysis Results"
        else:
            content = self.chat_display.get(1.0, tk.END).strip()
            file_type = "Chat History"
            
        if not content:
            messagebox.showinfo("Info", f"No {file_type.lower()} to save")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, "w") as file:
                    file.write(content)
                messagebox.showinfo("Success", f"{file_type} saved successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {str(e)}")
    
    def save_chat(self):
        self.notebook.select(1)
        self.save_results()
    
    def view_history(self, history_type):
        try:
            view = tk.Toplevel(self.root)
            if history_type == "image":
                view.title("Image Analysis History")
                cols = ("ID", "Image", "Date", "Prompt")
                query = "SELECT * FROM image_analyses ORDER BY analysis_date DESC"
            else:
                view.title("Chat History")
                cols = ("ID", "User Message", "Date")
                query = "SELECT * FROM chat_history ORDER BY chat_date DESC"
                
            view.geometry("700x500")
            
            tree = ttk.Treeview(view, columns=cols, show="headings")
            for col in cols:
                tree.heading(col, text=col)
            
            if history_type == "image":
                tree.column("ID", width=50)
                tree.column("Image", width=150)
                tree.column("Date", width=150)
                tree.column("Prompt", width=300)
            else:
                tree.column("ID", width=50)
                tree.column("User Message", width=300)
                tree.column("Date", width=150)
            
            scroll = ttk.Scrollbar(view, orient=tk.VERTICAL, command=tree.yview)
            tree.configure(yscroll=scroll.set)
            
            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scroll.pack(side=tk.RIGHT, fill=tk.Y)
            
            result_frame = tk.Frame(view, padx=10, pady=10)
            result_frame.pack(fill=tk.BOTH, expand=True)
            
            result_box = scrolledtext.ScrolledText(result_frame, wrap=tk.WORD)
            result_box.pack(fill=tk.BOTH, expand=True)
            
            cursor = self.conn.cursor()
            cursor.execute(query)
            
            if history_type == "image":
                for (id, path, prompt, result, date) in cursor.fetchall():
                    tree.insert("", tk.END, values=(
                        id, os.path.basename(path), date, prompt
                    ), tags=(str(id), result))
            else:
                for (id, user_msg, bot_response, date) in cursor.fetchall():
                    tree.insert("", tk.END, values=(
                        id, user_msg[:50] + "..." if len(user_msg) > 50 else user_msg, date
                    ), tags=(str(id), f"User: {user_msg}\n\nGemini: {bot_response}"))
            
            cursor.close()
            
            def on_select(event):
                for item in tree.selection():
                    result_box.delete(1.0, tk.END)
                    result_box.insert(tk.END, tree.item(item, "tags")[1])
            
            tree.bind("<<TreeviewSelect>>", on_select)
            
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err))
    
    def show_about(self):
        about_text = """Gemini AI Suite
Version 1.0

This application combines image analysis and chat functionality
using Google's Gemini AI technology.

Image Analyzer:
Analyze and understand images with AI assistance.

Chat Interface:
Have conversations with the Gemini AI model.

© 2025
        """
        messagebox.showinfo("About", about_text)
        
    def show_documentation(self):
        doc_window = tk.Toplevel(self.root)
        doc_window.title("Documentation")
        doc_window.geometry("600x400")
        
        doc_text = scrolledtext.ScrolledText(doc_window, wrap=tk.WORD)
        doc_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        help_content = """# Gemini AI Suite Documentation

## Image Analyzer

### Getting Started
1. Select an image using the File menu or the Select Image button
2. Choose a prompt type from the Prompts menu
3. Click "Analyze Image" to process the image with Gemini AI

### Prompt Types
- General Description: Basic information about the image
- Detailed Analysis: In-depth analysis of elements and context
- Object Detection: Identifies objects in the image
- Scene Understanding: Explains what's happening in the scene

### History
View previous analyses using the "View Image History" option.

## Chat Interface

### Getting Started
1. Type your message in the input box
2. Press Enter or click the Send button
3. View the AI response in the chat window

### Commands
- Type 'bye', 'exit', or 'quit' to end the conversation
- Use Shift+Enter to add a new line without sending

### History
View previous chat conversations using the "View Chat History" option.

## General Features
- Save results to text files
- View analysis and chat history
- Switch between tabs using the View menu
        """
        
        doc_text.insert(tk.END, help_content)
        doc_text.config(state=tk.DISABLED)

    def __del__(self):
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = GeminiApp(root)
    root.mainloop()