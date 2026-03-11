import tkinter as tk
from tkinter import scrolledtext, messagebox
import json
import os
import threading
try:
    from google import genai
    from google.genai import types
except ImportError:
    messagebox.showerror("Error", "Google GenerativeAI library not found. Please install it with: pip install google-generativeai")
    exit(1)

class GeminiApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gemini API Calculator")
        self.root.geometry("700x500")
        
        # Config file for storing API key
        self.config_file = "gemini_config.json"
        self.api_key = self.load_api_key()
        
        # Create UI elements
        self.create_widgets()
        
    def load_api_key(self):
        """Load API key from config file or return None if not found"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    return config.get('api_key', '')
            except Exception as e:
                print(f"Error loading config: {e}")
        return ""
        
    def save_api_key(self, api_key):
        """Save API key to config file"""
        with open(self.config_file, 'w') as f:
            json.dump({'api_key': api_key}, f)
            
    def create_widgets(self):
        # API Key frame
        api_frame = tk.Frame(self.root, pady=10)
        api_frame.pack(fill=tk.X, padx=10)
        
        tk.Label(api_frame, text="Gemini API Key:").pack(side=tk.LEFT)
        
        self.api_key_var = tk.StringVar(value=self.api_key)
        self.api_key_entry = tk.Entry(api_frame, textvariable=self.api_key_var, width=40, show="*")
        self.api_key_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Button(api_frame, text="Save Key", command=self.on_save_key).pack(side=tk.LEFT, padx=5)
        self.show_key_var = tk.BooleanVar(value=False)
        tk.Checkbutton(api_frame, text="Show Key", variable=self.show_key_var, 
                      command=self.toggle_show_key).pack(side=tk.LEFT)
        
        # Query frame
        query_frame = tk.Frame(self.root, pady=10)
        query_frame.pack(fill=tk.X, padx=10)
        
        tk.Label(query_frame, text="Query:").pack(side=tk.LEFT)
        
        self.query_var = tk.StringVar(value="What is the sum of the first 50 prime numbers? Generate and run code for the calculation.")
        self.query_entry = tk.Entry(query_frame, textvariable=self.query_var, width=70)
        self.query_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Buttons frame
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(btn_frame, text="Calculate", command=self.run_query).pack(side=tk.LEFT)
        tk.Button(btn_frame, text="Clear Results", command=self.clear_results).pack(side=tk.LEFT, padx=5)
        
        # Results area
        tk.Label(self.root, text="Results:").pack(anchor=tk.W, padx=10)
        
        self.results_text = scrolledtext.ScrolledText(self.root, height=15, wrap=tk.WORD)
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def toggle_show_key(self):
        """Toggle showing or hiding the API key"""
        if self.show_key_var.get():
            self.api_key_entry.config(show="")
        else:
            self.api_key_entry.config(show="*")
    
    def on_save_key(self):
        """Save API key to config file"""
        api_key = self.api_key_var.get().strip()
        if api_key:
            self.save_api_key(api_key)
            self.api_key = api_key
            self.status_var.set("API key saved successfully")
        else:
            messagebox.showerror("Error", "Please enter a valid API key")
    
    def clear_results(self):
        """Clear the results text area"""
        self.results_text.delete(1.0, tk.END)
        
    def run_query(self):
        """Run the query using the Gemini API"""
        # Check if API key is set
        api_key = self.api_key_var.get().strip()
        if not api_key:
            messagebox.showerror("Error", "Please enter your Gemini API key and save it")
            return
            
        query = self.query_var.get().strip()
        if not query:
            messagebox.showerror("Error", "Please enter a query")
            return
            
        # Update status
        self.status_var.set("Processing query...")
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, "Sending request to Gemini API...\n\n")
        self.root.update()
        
        # Run query in a separate thread to avoid freezing UI
        threading.Thread(target=self.process_query, args=(api_key, query), daemon=True).start()
    
    def process_query(self, api_key, query):
        """Process the query using Gemini API (run in separate thread)"""
        try:
            # Initialize Gemini client
            client = genai.Client(api_key=api_key)
            
            # Configure tool for code execution
            tools = [types.Tool(code_execution=types.ToolCodeExecution)]
            
            # Call the API
            response = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=query,
                config=types.GenerateContentConfig(tools=tools)
            )
            
            # Add response to results
            self.root.after(0, lambda: self.update_results(str(response.text)))
            self.root.after(0, lambda: self.status_var.set("Query completed"))
            
        except Exception as e:
            self.root.after(0, lambda: self.update_results(f"Error: {str(e)}"))
            self.root.after(0, lambda: self.status_var.set("Error occurred"))
    
    def update_results(self, text):
        """Update the results text area (called from main thread)"""
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, text)
            
def main():
    root = tk.Tk()
    app = GeminiApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()