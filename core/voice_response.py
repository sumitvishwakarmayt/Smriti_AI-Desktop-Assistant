import threading
from typing import Optional, Callable
from gtts import gTTS
from io import BytesIO
from pydub import AudioSegment
from pydub.utils import which as which_ffmpeg
import simpleaudio as sa
import time
from tempfile import NamedTemporaryFile
import os


class VoiceResponder:
    def __init__(self):
        try:
            print("🔧 Initializing gTTS responder...")
            self.is_speaking_flag = False
            self.caption_callback: Optional[Callable[[str], None]] = None
            self._current_playback: Optional[sa.PlayObject] = None
            self._current_backend: str = "pydub"  # or "pygame"
            self._pygame_ready: bool = False
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
                    # Prefer pydub+simpleaudio if ffmpeg available
                    if which_ffmpeg("ffmpeg") is None and which_ffmpeg("ffprobe") is None:
                        raise RuntimeError("ffmpeg not found")

                    segment = AudioSegment.from_file(mp3_buf, format="mp3")
                    raw_data = segment.raw_data
                    num_channels = segment.channels
                    bytes_per_sample = segment.sample_width
                    sample_rate = segment.frame_rate

                    # Stop any current playback first
                    if self._current_playback is not None:
                        try:
                            self._current_playback.stop()
                        except Exception:
                            pass

                    # Play audio via simpleaudio
                    self._current_backend = "pydub"
                    self._current_playback = sa.play_buffer(
                        raw_data,
                        num_channels,
                        bytes_per_sample,
                        sample_rate,
                    )
                    self._current_playback.wait_done()
                except Exception as decode_err:
                    # Fallback to pygame to play MP3 directly without ffmpeg
                    try:
                        import pygame
                        if not self._pygame_ready:
                            pygame.mixer.init()
                            self._pygame_ready = True
                        # Write mp3 to temp file for pygame
                        with NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                            tmp.write(mp3_buf.getvalue())
                            tmp_path = tmp.name
                        self._current_backend = "pygame"
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
                    except Exception as pg_err:
                        print(f"❌ Both playback backends failed. pydub error: {decode_err}, pygame error: {pg_err}")
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
            if self._current_backend == "pydub":
                if self._current_playback is not None:
                    try:
                        self._current_playback.stop()
                    except Exception:
                        pass
            elif self._current_backend == "pygame":
                try:
                    import pygame
                    if self._pygame_ready:
                        pygame.mixer.music.stop()
                except Exception:
                    pass
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