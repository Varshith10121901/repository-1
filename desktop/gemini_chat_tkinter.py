import tkinter as tk
from tkinter import scrolledtext, ttk, font
import google.generativeai as ai
import threading



class GeminiChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gemini Chatbot")
        self.root.geometry("800x600")
        self.root.configure(bg="#f5f5f5")
        
        # Configure API
        self.API_KEY = 'AIzaSyCvyxvEZcBh2x8VRFUCFDZqeoIMCWjwYzo'  # Redacted for security
        ai.configure(api_key=self.API_KEY)
        self.model = ai.GenerativeModel("gemini-2.0-flash")
        self.chat = self.model.start_chat()
        self.history = []
        
        # Configure fonts
        self.default_font = font.nametofont("TkDefaultFont")
        self.default_font.configure(size=11)
        self.root.option_add("*Font", self.default_font)
        
        # Create main frame
        self.main_frame = tk.Frame(self.root, bg="#f5f5f5")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create and configure widgets
        self.setup_ui()
        
        # Welcome message
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, "AURA ai: Hello! How can I help you today?\n", "bot")
        self.chat_display.config(state=tk.DISABLED)
        
    def setup_ui(self):
        # Create header
        header_frame = tk.Frame(self.main_frame, bg="#f5f5f5")
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = tk.Label(header_frame, text="Gemini 2.0 Chatbot", font=("Arial", 16, "bold"), bg="#f5f5f5", fg="#333333")
        title_label.pack(side=tk.LEFT)
        
        # Create chat display
        chat_frame = tk.Frame(self.main_frame, bg="#f5f5f5")
        chat_frame.pack(fill=tk.BOTH, expand=True)
        
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame, 
            state=tk.DISABLED, 
            bg="white", 
            fg="#333333",
            font=("Arial", 11),
            wrap=tk.WORD,
            relief=tk.FLAT,
            borderwidth=1
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        
        # Configure tags for text styling
        self.chat_display.tag_configure("user", foreground="#1a73e8", font=("Arial", 11, "bold"))
        self.chat_display.tag_configure("bot", foreground="#0f9d58", font=("Arial", 11))
        
        # Create input area
        input_frame = tk.Frame(self.main_frame, bg="#f5f5f5")
        input_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.input_text = scrolledtext.ScrolledText(
            input_frame,
            height=4,
            bg="white",
            fg="#333333",
            font=("Arial", 11),
            wrap=tk.WORD,
            relief=tk.FLAT,
            borderwidth=1
        )
        self.input_text.pack(fill=tk.X, side=tk.LEFT, expand=True, padx=(0, 10))
        self.input_text.bind("<Return>", self.handle_return)
        
        button_style = ttk.Style()
        button_style.configure("Send.TButton", font=("Arial", 11))
        
        self.send_button = ttk.Button(
            input_frame,
            text="Send",
            command=self.send_message,
            style="Send.TButton"
        )
        self.send_button.pack(side=tk.RIGHT)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = tk.Label(
            self.main_frame, 
            textvariable=self.status_var, 
            bd=1, 
            relief=tk.FLAT, 
            anchor=tk.W,
            bg="#f5f5f5",
            fg="#666666",
            font=("Arial", 9)
        )
        status_bar.pack(fill=tk.X, pady=(5, 0))
    
    def handle_return(self, event):
        # Send message on Enter key, but allow Shift+Enter for new line
        if not (event.state & 0x1):  # Check if Shift key is not pressed
            self.send_message()
            return "break"  # Prevent default behavior (new line)
    
    def send_message(self):
        message = self.input_text.get("1.0", tk.END).strip()
        if not message:
            return
            
        self.input_text.delete("1.0", tk.END)
        
        # Display user message
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"You: {message}\n", "user")
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
        
        # Add to history
        self.history.append(f"User: {message}")
        
        # Update status
        self.status_var.set("Generating response...")
        self.send_button.config(state=tk.DISABLED)
        
        # Process in a separate thread to keep UI responsive
        threading.Thread(target=self.process_response, args=(message,), daemon=True).start()
    
    def process_response(self, message):
        try:
            # Check for exit command
            if message.lower() in ['bye', 'exit', 'quit']:
                response_text = "Goodbye! Feel free to come back anytime."
                self.root.after(500, lambda: self.show_response(response_text))
                return
                
            # Get response from Gemini
            response = self.chat.send_message('\n'.join(self.history))
            response_text = response.text
            
            # Add to history
            self.history.append(f"Chatbot: {response_text}")
            
            # Update UI from main thread
            self.root.after(0, lambda: self.show_response(response_text))
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.root.after(0, lambda: self.show_response(error_msg))
    
    def show_response(self, response_text):
        # Display bot message
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"Gemini: {response_text}\n\n", "bot")
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
        
        # Reset status
        self.status_var.set("Ready")
        self.send_button.config(state=tk.NORMAL)
        self.input_text.focus()

def main():
    root = tk.Tk()
    app = GeminiChatApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()









