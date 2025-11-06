from core.gemini_connector import ask_gemini
from core.voice_response import speak

def process_command(command: str):
    command = command.lower().strip()
    print(f"🧠 Smriti Brain Received: {command}")

    # ✨ Identity rules — she remembers who she is, period.
    if any(keyword in command for keyword in [
        "who are you", "what is your name", "who created you",
        "who made you", "tell me about yourself", "your creator", "developer"
    ]):
        reply = (
            "I am Smriti — your AI Desktop Assistant, created by Sumit Vishwakarma. "
            "I'm designed to assist you, talk with you, and handle your desktop tasks smartly."
        )
        print(f"💜 Smriti Identity: {reply}")
        speak(reply)
        return reply

    # 🗣 Greeting handling
    if any(word in command for word in ["hello", "hi", "hey", "namaste", "good morning", "good evening"]):
        reply = "Hello sir! I am Smriti here — an AI Desktop Assistant made by Sumit Vishwakarma"
        speak(reply)
        return reply

    # 💤 Stop / Exit handling
    if any(word in command for word in ["stop", "exit", "bye", "shut up", "band kar", "stop listening"]):
        reply = "Alright Sumit, I’ll stop listening now. Just say 'Hey Smriti' when you need me again!"
        speak(reply)
        return "stopped"

    # 🧩 Default: use Gemini (but filter identity)
    print("🤖 Smriti: Thinking...")
    response = ask_gemini(command)

    # 🚫 Filter out Gemini’s LLM self-identity replies
    if any(bad_phrase in response.lower() for bad_phrase in [
        "large language model",
        "trained by google",
        "i’m an ai model",
        "i am an ai",
        "i am gemini",
        "i was created by google"
    ]):
        response = "I am Smriti — your AI Desktop Assistant, created by Sumit Vishwakarma."

    print(f"🧩 Smriti Reply: {response}")
    speak(response)
    return response
