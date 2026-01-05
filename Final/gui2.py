import tkinter as tk
from tkinter import scrolledtext
import requests
import urllib.parse
import threading
from tkinter import filedialog
from PIL import ImageGrab  # For screen capture
#from chatbot_llm import img2text
from chatbot_llm_NOanimation import img2text
import keyboard

# GUI Chat Client for Gemini Chatbot

FLASK_URL = "http://localhost:11223/ผู้สร้าง%20say:"  # your Flask server

def send_message():
    user_input = user_entry.get()
    if not user_input.strip():
        return

    # Insert the user's message with "You:" in bold
    chat_area.insert(tk.END, "You: ", "bold")  # Apply the "bold" tag to "You:"
    chat_area.insert(tk.END, f"{user_input}\n")  # Regular text for the user's input
    user_entry.delete(0, tk.END)

    # Start a new thread to handle the network request
    threading.Thread(target=handle_network_request, args=(user_input,), daemon=True).start()

def handle_network_request(user_input):
    try:
        encoded_query = urllib.parse.quote(user_input)
        response = requests.Session()
        response = response.get(FLASK_URL + encoded_query)
        bot_reply = response.text.strip()
    except Exception as e:
        bot_reply = f"Error: {str(e)}"

    # Use the `after` method to safely update the GUI from the main thread
    window.after(0, lambda: insert_bot_message(bot_reply))

def insert_bot_message(bot_reply):
    # Insert the bot's message with "Bot:" in bold
    chat_area.insert(tk.END, "Bot: ", "bold")  # Apply the "bold" tag to "Bot:"
    chat_area.insert(tk.END, f"{bot_reply}\n")  # Regular text for the bot's reply
    chat_area.see(tk.END)

def send_image():
    # Open a file dialog to select an image
    file_path = filedialog.askopenfilename(
        title="Select an Image",
        filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
    )
    
    if file_path:
        # Display a message in the chat area indicating an image was sent
        chat_area.insert(tk.END, "You: ", "bold")
        chat_area.insert(tk.END, f"[Image sent: {file_path}]\n")
        
        # Start a new thread to handle the image sending process
        threading.Thread(target=handle_image_upload, args=(file_path,), daemon=True).start()

def handle_image_upload(file_path):
    try:
        # Call the img2text function directly with the selected image file
        result = img2text(file_path)
        bot_reply = result
    except Exception as e:
        bot_reply = f"Error: {str(e)}"

    # Use the `after` method to safely update the GUI from the main thread
    window.after(0, lambda: insert_bot_message(bot_reply))

def capture_screen():
    # Capture a portion of the screen
    try:
        chat_area.insert(tk.END, "You: ", "bold")
        chat_area.insert(tk.END, "[Capturing screen...]\n")
        chat_area.see(tk.END)

        # Use ImageGrab to capture the screen
        screen_capture = ImageGrab.grab()
        file_path = "captured_screen.png"
        screen_capture.save(file_path)

        # Display a message in the chat area indicating a screen capture was sent
        chat_area.insert(tk.END, "You: ", "bold")
        chat_area.insert(tk.END, f"[Screen captured and sent: {file_path}]\n")

        # Start a new thread to handle the screen capture upload
        threading.Thread(target=handle_image_upload, args=(file_path,), daemon=True).start()
    except Exception as e:
        chat_area.insert(tk.END, f"Error capturing screen: {str(e)}\n")

# Function to listen for global key press
def listen_key():
    keyboard.add_hotkey("Insert", capture_screen)  # Bind globally
    keyboard.wait()  # Keep the listener running

# GUI setup
window = tk.Tk()
window.title("Gemini Chatbot GUI")

# Create the ScrolledText widget
chat_area = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=60, height=20, font=("Arial", 12))
chat_area.pack(padx=10, pady=10)

# Configure the "bold" tag to use a bold font
chat_area.tag_configure("bold", font=("Arial", 12, "bold"))

user_entry = tk.Entry(window, font=("Arial", 12), width=50)
user_entry.pack(padx=10, pady=(0, 10), side=tk.LEFT)
user_entry.bind("<Return>", lambda event: send_message())

send_button = tk.Button(window, text="Send", font=("Arial", 12), command=send_message)
send_button.pack(padx=(0, 10), pady=(0, 10), side=tk.LEFT)

# Create the image send button
image_button = tk.Button(window, text="Send Image", font=("Arial", 12), command=send_image)
image_button.pack(padx=(0, 10), pady=(0, 10), side=tk.LEFT)

# Create the capture screen button
capture_button = tk.Button(window, text="Capture Screen", font=("Arial", 12), command=capture_screen)
capture_button.pack(padx=(0, 10), pady=(0, 10), side=tk.LEFT)

# Start the global key listener in a separate thread
threading.Thread(target=listen_key, daemon=True).start()

window.mainloop()