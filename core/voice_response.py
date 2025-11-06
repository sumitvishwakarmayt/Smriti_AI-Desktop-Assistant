import asyncio
import threading
import tempfile
import os
import edge_tts
import playsound

# Default female voice for English (India accent)
VOICE = "en-IN-NeerjaNeural"

# if you want Hindi voice instead:
# VOICE = "hi-IN-SwaraNeural"


# Async function to speak text
async def _speak_async(text: str):
    try:
        # Temporary file for audio output
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
            file_path = temp_audio.name

        # Generate speech
        communicate = edge_tts.Communicate(text, VOICE, rate="-1%")  # slower & clear
        await communicate.save(file_path)

        # Play the generated speech
        playsound.playsound(file_path, True)

        # Clean up the temp file
        os.remove(file_path)
    except Exception as e:
        print(f"[Voice Error] {e}")


# Run the async voice in background thread (safe for PyQt)
def speak(text: str):
    """Make Smriti speak asynchronously without blocking UI."""
    def run():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(_speak_async(text))
        loop.close()

    threading.Thread(target=run, daemon=True).start()
