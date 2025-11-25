import threading
from typing import Optional, Callable
from gtts import gTTS
from io import BytesIO
import pygame
import time
from tempfile import NamedTemporaryFile
import os


class VoiceResponder:
    def __init__(self):
        try:
            print("🔧 Initializing gTTS responder...")
            self.is_speaking_flag = False
            self.caption_callback: Optional[Callable[[str], None]] = None
            self._pygame_ready: bool = False
            # Initialize pygame mixer
            pygame.mixer.init()
            self._pygame_ready = True
            print("✅ gTTS responder ready")
        except Exception as e:
            print(f"❌ TTS init error: {e}")

    def speak(self, text: str):
        if not text or not text.strip():
            return
            
        def speak_thread():
            try:
                print(f"🔊 Speaking: {text[:60]}...")
                self.is_speaking_flag = True

                # Send caption to UI
                if self.caption_callback:
                    self.caption_callback(text)

                # Generate TTS audio (mp3) in-memory
                tts = gTTS(text=text, lang='en', slow=False)
                mp3_buf = BytesIO()
                tts.write_to_fp(mp3_buf)
                mp3_buf.seek(0)

                try:
                    # Use pygame to play MP3 directly
                    if not self._pygame_ready:
                        pygame.mixer.init()
                        self._pygame_ready = True
                    
                    # Write mp3 to temp file for pygame
                    with NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                        tmp.write(mp3_buf.getvalue())
                        tmp_path = tmp.name
                    
                    pygame.mixer.music.load(tmp_path)
                    pygame.mixer.music.play()
                    # Wait for playback to finish
                    while pygame.mixer.music.get_busy() and self.is_speaking_flag:
                        time.sleep(0.1)
                    # Cleanup
                    try:
                        os.remove(tmp_path)
                    except Exception:
                        pass
                except Exception as play_err:
                    print(f"❌ Audio playback error: {play_err}")
                finally:
                    self.is_speaking_flag = False
                    print("✅ Speech completed")
            except Exception as e:
                print(f"❌ Speech error: {e}")
                self.is_speaking_flag = False

        thread = threading.Thread(target=speak_thread, daemon=True)
        thread.start()

    def stop(self):
        try:
            print("🛑 Stopping current speech...")
            if self._pygame_ready:
                pygame.mixer.music.stop()
            self.is_speaking_flag = False
            print("🔇 Speech stopped successfully")
        except Exception as e:
            print(f"⚠️ Stop error: {e}")

    def is_speaking(self):
        return self.is_speaking_flag

    def set_caption_callback(self, callback):
        self.caption_callback = callback


_responder = VoiceResponder()

def speak(text: str):
    _responder.speak(text)

def stop():
    _responder.stop()

def is_speaking():
    return _responder.is_speaking()

def set_caption_callback(callback):
    _responder.set_caption_callback(callback)