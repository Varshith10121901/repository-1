import tkinter as tk
from tkinter import filedialog, scrolledtext
import base64
import google.generativeai as genai
import os
import io

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

class AudioDescriberGUI:
    def __init__(self, root):
        self.root = root
        root.title("Audio Describer")
        root.geometry("600x400")

        self.audio_file_path = ""

        self.select_button = tk.Button(root, text="Select Audio File", command=self.select_audio_file)
        self.select_button.pack(pady=10)

        self.generate_button = tk.Button(root, text="Generate Description", command=self.generate_description, state=tk.DISABLED)
        self.generate_button.pack(pady=10)

        self.text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=60, height=15)
        self.text_area.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

    def select_audio_file(self):
        self.audio_file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3;*.wav")])
        if self.audio_file_path:
            self.generate_button.config(state=tk.NORMAL)
        else:
            self.generate_button.config(state=tk.DISABLED)

    def generate_description(self):
        if not self.audio_file_path:
            return

        try:
            with open(self.audio_file_path, 'rb') as audio_file:
                audio_bytes = audio_file.read()

            self.text_area.delete("1.0", tk.END)
            self.text_area.insert(tk.END, "Generating description...\n")
            self.root.update()

            response = model.generate_content(
                [
                    "Describe this audio clip",
                    {"mime_type": "audio/mpeg", "data": base64.b64encode(audio_bytes).decode('utf-8')}
                ]
            )

            self.text_area.delete("1.0", tk.END)
            if response.parts:
                self.text_area.insert(tk.END, response.text)
            else:
                self.text_area.insert(tk.END, "No description generated. Please check the audio file or API response.")

        except FileNotFoundError:
            self.text_area.delete("1.0", tk.END)
            self.text_area.insert(tk.END, f"Error: Audio file not found at {self.audio_file_path}")
        except Exception as e:
            self.text_area.delete("1.0", tk.END)
            self.text_area.insert(tk.END, f"An error occurred: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    gui = AudioDescriberGUI(root)
    root.mainloop()