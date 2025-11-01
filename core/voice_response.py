import pyttsx3

engine = pyttsx3.init()
engine.setProperty('rate', 135)
engine.setProperty('volume', 1.0)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)  # change [0] or [1] depending on male/female voice

def speak(text):
    engine.say(text)
    engine.runAndWait()

