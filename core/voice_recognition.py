import speech_recognition as sr
import time

recognizer = sr.Recognizer()
# Make recognition more responsive to short phrases and small gaps
recognizer.dynamic_energy_threshold = True
recognizer.energy_threshold = 250  # starting point; dynamic will adapt
recognizer.pause_threshold = 0.5   # end of phrase detected quicker
recognizer.phrase_threshold = 0.2  # require less speech before considering a phrase
recognizer.non_speaking_duration = 0.2  # shorter required silence before/after speech
recognizer.operation_timeout = 3  # network operations timeout

def listen_command(timeout=4, phrase_time_limit=4):
    """Listen for a voice command with enhanced timing and stop speaking when user talks"""
    try:
        with sr.Microphone() as source:
            print("🎧 Smriti is listening... (Speak now)")
            
            # Adjust for ambient noise quickly (shorter calibration)
            recognizer.adjust_for_ambient_noise(source, duration=0.3)
            print("✅ Ambient noise adjusted")
            
            # Listen with tighter timeout and phrase limit for snappier UX
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            
    except sr.WaitTimeoutError:
        print("⏰ Listening timeout - no speech detected")
        return ""
    except OSError as e:
        print(f"🚫 Microphone not available: {e}")
        return ""
    except Exception as e:
        print(f"🎤 Microphone error: {e}")
        return ""

    try:
        command = recognizer.recognize_google(audio, language='en-IN')
        print(f"🗣️ You said: {command}")
        return command.lower()
    except sr.UnknownValueError:
        print("😕 Smriti didn't catch that clearly.")
        return ""
    except sr.RequestError as e:
        print(f"🚫 Voice recognition service error: {e}")
        return ""