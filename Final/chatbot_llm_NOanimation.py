from flask import Flask
import google.generativeai as genai
#from kokoro_tts import speak
from tts import speak
from api_key import key
from prompt import prompt, prompt2, prompt3, prompt4, event
import logging
import asyncio
import pyvts
from PIL import Image
import cv2
import numpy as np
import pyautogui

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configure Gemini API with your API key
genai.configure(api_key=key)

# Initialize the model
model = genai.GenerativeModel(
    model_name="models/gemini-2.0-flash-lite",
    generation_config={
        "max_output_tokens": 1200,
        "temperature": 1.0,
        "top_p": 0.95,
        "top_k": 32,
    },
    system_instruction=f'{prompt3}\n{event}'
)

# Start a chat session
chat = model.start_chat(history=[])

app = Flask(__name__)

# Test when empty prompt
@app.route('/')
def hello_world():
    return "hello chat"

# Ignore favicon.ico
@app.route('/favicon.ico')
def favicon():
    return '', 204
'''
# Image processing
def img2text(image_file):
    input_text = "What do you think about this image?"
    img = Image.open(image_file)
    response = chat.send_message([input_text, img], stream=True)
    response.resolve()
    speak(response.text.strip())
    return response.text.strip()
'''
# Screen Share
def screenshare():
    # Capture the entire screen
    screenshot = pyautogui.screenshot()
    # Convert the screenshot to a NumPy array
    screenshot_array = np.array(screenshot)
    # Convert the NumPy array to an OpenCV image
    screenshot_image = cv2.cvtColor(screenshot_array, cv2.COLOR_RGB2BGR)
    cv2.imwrite("RT_S.jpg", screenshot_image)
    img = Image.open("RT_S.jpg")
    return img

# User Prompt
@app.route("/<query>")
def query(query):
    # Log the user's query
    logging.info(f"User Query: {query}")
    img = screenshare()
    # Chatbot Gemini
    try:
        response = chat.send_message([query, img], stream=True)  
        response.resolve()  # Wait for the response to be fully generated
        reply = response.text.strip()

        #Translate the reply to Thai
        ##asyncio.run(translate_text(reply))

        # Log the bot's reply
        logging.info(f"Bot Reply: {reply}")
        
        
        # Speak the reply using TTS
        speak(reply)

        # Wait for the TTS to finish before triggering emotes
        asyncio.run(asyncio.sleep(1))  # Adjust the sleep duration as needed


        return reply
    
    except Exception as e:
        # Log any errors that occur during processing
        logging.error(f"Error processing query: {e}")
        return "An error occurred while processing your request.", 500

# Server
if __name__ == '__main__':
    app.run(port=11223, host="192.168.1.108", debug=True)