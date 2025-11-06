from core.gemini_connector import ask_gemini
from core.voice_response import speak

def process_command(command):
    """
    Process the given command through Gemini and return the response text.
    Also makes Smriti speak the response aloud.
    """
    if not command.strip():
        return "I didn’t catch that, please say it again."

    print(f"🧠 Smriti Brain Received: {command}")
    
    try:
        # Get AI-generated response from Gemini
        response = ask_gemini(command)
        
        # Log and speak
        print(f"💬 Smriti Reply: {response}")
        speak(response)

        return response
    except Exception as e:
        error_msg = f"⚠️ Error processing command: {e}"
        print(error_msg)
        speak("Sorry, I ran into a problem while thinking.")
        return error_msg
