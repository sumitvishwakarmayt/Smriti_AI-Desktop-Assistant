import asyncio
import threading
import tempfile
import os
import edge_tts
import playsound
import time

VOICE = "en-IN-NeerjaNeural"  # Clean female English voice
stop_signal = False
is_speaking = False
lock = threading.Lock()


async def _speak_async(text: str):
    global stop_signal, is_speaking
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
            file_path = temp_audio.name

        # Generate speech
        communicate = edge_tts.Communicate(text, VOICE, rate="-5%")
        await communicate.save(file_path)

        if not stop_signal:
            is_speaking = True
            playsound.playsound(file_path, True)
            is_speaking = False

        os.remove(file_path)

    except Exception as e:
        print(f"[Voice Error] {e}")
        is_speaking = False


def speak(text: str):
    """Prevent overlapping voices and speak instantly."""
    global stop_signal, is_speaking

    with lock:  # thread-safe block
        # Stop any current speech
        stop_signal = True
        time.sleep(0.1)  # give a split second to stop previous voice
        stop_signal = False

        if is_speaking:
            print("[Voice Info] Smriti is already speaking, skipping new voice to avoid echo.")
            return

        def run():
            asyncio.run(_speak_async(text))

        threading.Thread(target=run, daemon=True).start()


def stop_speaking():
    """Immediately stop Smriti’s voice output."""
    global stop_signal, is_speaking
    stop_signal = True
    is_speaking = False

    # Kill any lingering audio player
    os.system("taskkill /IM wmplayer.exe /F >nul 2>&1")
    os.system("taskkill /IM vlc.exe /F >nul 2>&1")

    print("[🔇 Smriti stopped speaking instantly]")
