import google.generativeai as genai
from api_key import key
from prompt import prompt, prompt2, prompt3
from PIL import Image
from tts import speak

# Configure Gemini API with your API key
genai.configure(api_key=key)

# Initialize the model
model = genai.GenerativeModel(
    model_name="models/gemini-1.5-flash",
    generation_config={
        "max_output_tokens": 1200,
        "temperature": 0.5,
        "top_p": 1.0,
        "top_k": 40,
    },
    system_instruction=prompt2
)

# Start a chat session
chat = model.start_chat()


def img2text(image_file="screenshot.png"):
    input_text = "What do you think about this image?"
    img = Image.open(image_file)
    response = model.generate_content([input_text, img], stream=True)
    response.resolve()
    speak(response.text.strip())
    return response.text.strip()