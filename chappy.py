import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
import subprocess
import sys
import os
from chatgpt import chat_gpt

def send_message(event=None):
    user_input = user_entry.get()
    user_entry.delete(0, tk.END)
    if user_input.strip():
        # Display user message
        chat_history.config(state="normal")
        chat_history.insert(tk.END, "You: " + user_input + '\n\n')
        chat_history.yview(tk.END)
        chat_history.config(state="disabled")

        # Interact with your CLI
        response = chat_gpt(user_input.strip())

        # Display the API's response
        chat_history.config(state="normal")
        chat_history.insert(tk.END, "Assistant: " + response + '\n\n')
        chat_history.yview(tk.END)
        chat_history.config(state="disabled")

    # Clear input field


# Create main window
root = tk.Tk()
root.title("Chappy")
root.geometry("600x800")

# Create chat history display
chat_history = scrolledtext.ScrolledText(root, wrap=tk.WORD, state="disabled")
chat_history.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Create user input and send button
user_input_frame = ttk.Frame(root)
user_input_frame.pack(side=tk.BOTTOM, padx=5, pady=5, fill=tk.X, expand=False)


user_entry = ttk.Entry(user_input_frame)
user_entry.bind("<Return>", send_message)
user_entry.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)

send_button = ttk.Button(user_input_frame, text="Send", command=send_message)
send_button.pack(side=tk.RIGHT, padx=5, pady=5, fill=tk.NONE, expand=False)

root.mainloop()