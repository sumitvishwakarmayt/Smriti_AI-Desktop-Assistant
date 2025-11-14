# brain.py
import threading
from core.voice_response import speak, stop
from core.gemini_connector import ask_gemini
from core.app_launcher import open_application, open_website, close_application  # Add this import

# 🌸 Smriti's personality and identity
SMRITI_IDENTITY = (
    "I am Smriti, an AI Desktop Assistant created by Sumit Vishwakarma. "
    "I am here to assist, chat, and help you with your tasks naturally."
)


def process_command(command: str, speak_out: bool = True):
    """
    Handles user voice/text commands and routes them to Gemini or custom logic.
    """
    if not command or not command.strip():
        return "I didn't catch that, please repeat."

    command = command.strip().lower()
    print(f"🧠 Smriti Brain Received: {command}")

    # 🛑 Stop commands
    stop_keywords = ["stop", "ruko", "exit", "chup", "mute", "shut up", "bas"]
    if any(word in command for word in stop_keywords):
        stop()
        response = "Okay, I stopped speaking."
        print("🔇 [Voice stopped]")
        if speak_out:
            _async_speak(response)
        return response

    # 🤖 Identity commands
    identity_keywords = ["who are you", "what is your name", "introduce yourself", "tum kaun ho"]
    if any(word in command for word in identity_keywords):
        response = SMRITI_IDENTITY
        if speak_out:
            _async_speak(response)
        return response

    # 🚀 Application and Website Launcher Commands
    app_keywords = ["open", "launch", "start", "run", "kholo", "chalu"]
    website_keywords = ["website", "site", "web", "browser", "internet"]
    
    if any(word in command for word in app_keywords):
        response = handle_app_launch(command)
        if speak_out:
            _async_speak(response)
        return response

    # ❌ Close application commands
    close_keywords = ["close", "band", "band karo", "band ho", "quit", "stop app", "shutdown app", "exit app"]
    if any(word in command for word in close_keywords):
        response = handle_app_close(command)
        if speak_out:
            _async_speak(response)
        return response

    # 💬 General commands → handled by Gemini
    try:
        print("🧩 Smriti: Thinking (sending to Gemini)...")
        response = ask_gemini(command)
        if not response:
            response = "Sorry, I couldn't connect to my neural network right now."

        # Inject Smriti's personality
        if "google" in response.lower() or "language model" in response.lower():
            response = (
                "I am Smriti, your personal AI desktop assistant made by Sumit Vishwakarma. "
                "Not a generic Google model. 💜"
            )

        print(f"🤖 Gemini replied: {response}")
        
        # Return response - speech will be handled in main_window
        return response

    except Exception as e:
        error_msg = f"Brain error: {e}"
        print(f"[⚠️] {error_msg}")
        fallback = "My circuits glitched for a moment, please repeat."
        return fallback


def handle_app_launch(command):
    """Handle application and website launch commands"""
    try:
        print(f"🚀 Handling app launch command: {command}")
        
        # Website commands
        if any(word in command for word in ["youtube", "facebook", "instagram", "twitter", "github"]):
            for site in ["youtube", "facebook", "instagram", "twitter", "github", "google", "gmail"]:
                if site in command:
                    return open_website(site)
        
        # Browser commands
        if any(word in command for word in ["chrome", "browser", "web browser", "internet"]):
            return open_application("chrome")
        elif "firefox" in command:
            return open_application("firefox")
        elif "edge" in command:
            return open_application("edge")
        
        # Application commands
        elif "notepad" in command:
            return open_application("notepad")
        elif "calculator" in command:
            return open_application("calculator")
        elif "file explorer" in command or "explorer" in command:
            return open_application("file explorer")
        elif "command" in command or "terminal" in command or "cmd" in command:
            return open_application("command prompt")
        elif "vs code" in command or "code" in command:
            return open_application("vs code")
        
        # Generic open command - let Gemini handle it
        else:
            # Extract what to open from command
            if "open" in command:
                app_to_open = command.split("open")[-1].strip()
                return f"I'll try to open {app_to_open}. " + open_application(app_to_open)
            else:
                return "What would you like me to open?"
                
    except Exception as e:
        return f"Sorry, I couldn't open that application: {str(e)}"


def handle_app_close(command):
    """Handle application close/terminate commands"""
    try:
        print(f"🛑 Handling app close command: {command}")

        # Direct mapping
        if "notepad" in command:
            return close_application("notepad")
        if "calculator" in command or "calc" in command:
            return close_application("calculator")
        if "chrome" in command:
            return close_application("chrome")
        if "firefox" in command:
            return close_application("firefox")
        if "edge" in command or "microsoft edge" in command:
            return close_application("edge")
        if "vs code" in command or "code" in command:
            return close_application("vs code")
        if "command" in command or "terminal" in command or "cmd" in command:
            return close_application("terminal")

        # Generic pattern: close <app>
        if "close" in command:
            target = command.split("close", 1)[1].strip()
            if target:
                return close_application(target)
        if "band" in command:
            # handle hindi variants like "band notepad"
            parts = command.split("band", 1)
            if len(parts) > 1:
                target = parts[1].strip()
                if target:
                    return close_application(target)

        return "Which application should I close?"
    except Exception as e:
        return f"Sorry, I couldn't close that application: {str(e)}"


def _async_speak(text):
    """Speaks text asynchronously without blocking"""
    print(f"🔊 Brain requesting speech: {text[:50]}...")
    thread = threading.Thread(target=lambda: speak(text), daemon=True)
    thread.start()