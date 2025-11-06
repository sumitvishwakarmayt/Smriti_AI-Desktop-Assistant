import speech_recognition as sr

recognizer = sr.Recognizer()

def listen_command():
    """Listen for a voice command and return recognized text."""
    with sr.Microphone() as source:
        print("🎧 Smriti is listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        command = recognizer.recognize_google(audio, language='en-IN')
        print(f"🗣️ You said: {command}")
        return command.lower()
    except sr.UnknownValueError:
        print("😕 Smriti didn’t catch that.")
        return ""
    except sr.RequestError:
        print("🚫 Voice recognition service error.")
        return ""
