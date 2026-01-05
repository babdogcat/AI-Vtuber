import speech_recognition as sr
import requests
import threading
import keyboard

def send_to_chatbot(text):
    try:
        with requests.Session() as session:
            response = session.get(f"http://127.0.0.1:11223//ผู้สร้าง%20say:%20{text}")
            if response.status_code == 200:
                None
            else:
                print("Error communicating with chatbot:", response.status_code)
    except requests.exceptions.RequestException as e:
        print(f"Error sending request to chatbot: {e}")

def speech_to_text():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        #recognizer.adjust_for_ambient_noise(source, duration=0.5)  # Adjust for ambient noise
        while True:
            try:
                #keyboard.add_hotkey('`', speech_to_text)  # Set the ` key as a global hotkey
                keyboard.wait('`')  # Wait for the ` key to be pressed
                audio = recognizer.listen(source)  # Listen continuously

                text = recognizer.recognize_google(audio, language="th-TH")
                print("You said:", text)

                # Send the recognized text to the chatbot in a separate thread
                threading.Thread(target=send_to_chatbot, args=(text,)).start()

            except sr.UnknownValueError:
                None
            except sr.RequestError as e:
                print(f"Could not request results; {e}")

if __name__ == "__main__":
    speech_to_text()