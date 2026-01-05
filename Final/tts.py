import os
import threading
import queue
import time
import sounddevice as sd
import soundfile as sf
import subprocess
import io

# Queue to hold text-to-speak tasks
tts_queue = queue.Queue()
stop_event = threading.Event()

# Get VB-Cable device index
def get_vb_cable_output_device():
    devices = sd.query_devices()
    for idx, device in enumerate(devices):
        if "CABLE Input" in device['name']:
            return idx
    raise RuntimeError("VB-Cable device not found.")

# Background worker for TTS
def tts_worker():
    try:
        vb_device = get_vb_cable_output_device()
    except RuntimeError as e:
        print(e)
        return

    while not stop_event.is_set():
        try:
            text, voice = tts_queue.get(timeout=1)
        except queue.Empty:
            continue

        # Generate in-memory audio data
        try:
            # Run edge-tts and capture the audio output from stdout
            #command = ['edge-tts', '--rate=+15%', '--pitch=+30Hz', '--voice', voice, '--text', text]
            command = ['edge-tts', '--rate=+15%', '--pitch=+30Hz', '--voice', voice, '--text', text]
            result = subprocess.run(command, capture_output=True, check=True)
            audio_bytes = result.stdout
        except Exception as e:
            print(f"[TTS] Error generating speech: {e}")
            tts_queue.task_done()
            continue

        try:
            # Read audio data from the in-memory bytes buffer
            audio_buffer = io.BytesIO(audio_bytes)
            data, samplerate = sf.read(audio_buffer)
            sd.play(data, samplerate=samplerate, device=vb_device)

            # Wait until playback is finished or interrupted by a new task
          #  while sd.get_stream().active:
          #      if not tts_queue.empty():
          #          sd.stop()
          #          break
          #      time.sleep(0.5)

            sd.wait()  # Wait for playback to finish
        except Exception as e:
            print(f"[TTS] Error playing speech: {e}")
        finally:
            sd.stop()
            tts_queue.task_done()

# Start background thread
tts_thread = threading.Thread(target=tts_worker, daemon=True)
tts_thread.start()

# Public method to add speech to the queue
def speak(text, voice="en-US-AvaMultilingualNeural"):
#def speak(text, voice="th-TH-PremwadeeNeural"):
    tts_queue.put((text, voice))
