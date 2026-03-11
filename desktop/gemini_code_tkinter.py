import google.generativeai as genai
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import scrolledtext
import io
import threading

class GeminiCodeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gemini Code Execution")
        self.setup_ui()
        
    def setup_ui(self):
        # API Key Section
        self.api_frame = tk.Frame(self.root)
        self.api_frame.pack(pady=10)
        
        tk.Label(self.api_frame, text="API Key:").pack(side=tk.LEFT)
        self.api_entry = tk.Entry(self.api_frame, width=50, show="*")
        self.api_entry.pack(side=tk.LEFT, padx=5)
        
        # Prompt Section
        self.prompt_frame = tk.Frame(self.root)
        self.prompt_frame.pack(pady=10, fill=tk.X)
        
        tk.Label(self.prompt_frame, text="Prompt:").pack(anchor=tk.W)
        self.prompt_text = scrolledtext.ScrolledText(self.prompt_frame, height=10)
        self.prompt_text.pack(fill=tk.X)
        self.prompt_text.insert(tk.END, "What is the sum of the first 50 prime numbers? Generate and run code for the calculation.")
        
        # Output Section
        self.output_frame = tk.Frame(self.root)
        self.output_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        
        self.output_text = scrolledtext.ScrolledText(self.output_frame)
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
        # Button
        self.run_button = tk.Button(self.root, text="Run", command=self.run_query)
        self.run_button.pack(pady=10)
        
    def run_query(self):
        api_key = self.api_entry.get()
        prompt = self.prompt_text.get("1.0", tk.END)
        
        if not api_key:
            self.output_text.insert(tk.END, "Please enter an API key\n")
            return
            
        self.run_button.config(state=tk.DISABLED)
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "Processing...\n")
        
        threading.Thread(target=self.execute_query, args=(api_key, prompt)).start()
        
    def execute_query(self, api_key, prompt):
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-pro')
            
            response = model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.9,
                    "top_p": 1,
                    "top_k": 1,
                    "max_output_tokens": 2048,
                }
            )
            
            self.root.after(0, self.display_response, response)
        except Exception as e:
            self.root.after(0, self.output_text.insert, tk.END, f"Error: {str(e)}\n")
        finally:
            self.root.after(0, self.run_button.config, {'state': tk.NORMAL})
            
    def display_response(self, response):
        self.output_text.delete(1.0, tk.END)
        
        if response.text:
            self.output_text.insert(tk.END, response.text + "\n\n")
        
        if hasattr(response, 'candidates'):
            for candidate in response.candidates:
                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                    for part in candidate.content.parts:
                        if hasattr(part, 'text'):
                            self.output_text.insert(tk.END, part.text + "\n")
                        if hasattr(part, 'executable_code'):
                            self.output_text.insert(tk.END, f"\nGenerated code:\n{part.executable_code.code}\n")
                        if hasattr(part, 'code_execution_result'):
                            self.output_text.insert(tk.END, f"\nExecution result:\n{part.code_execution_result.output}\n")
                        if hasattr(part, 'inline_data'):
                            try:
                                img = Image.open(io.BytesIO(part.inline_data.data))
                                img.show()  # This will open the image in the default viewer
                            except Exception as e:
                                self.output_text.insert(tk.END, f"\nCould not display image: {str(e)}\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = GeminiCodeApp(root)
    root.mainloop()