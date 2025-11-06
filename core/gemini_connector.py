import os
import google.generativeai as genai
from dotenv import load_dotenv

# 🧩 Load environment variables (API key from .env)
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# ⚙️ Configure Gemini API
genai.configure(api_key=api_key)


def ask_gemini(prompt: str) -> str:
    """
    Sends user input to Gemini API and returns the response.
    Smriti-style processing with identity protection.
    """
    try:
        print(f"🧠 Smriti sending prompt to Gemini: {prompt}")

        # ✅ Use the flash model (faster and cheaper)
        model = genai.GenerativeModel("gemini-1.5-flash")

        # 🌀 Generate response
        response = model.generate_content(prompt)
        full_text = ""

        # Handle response safely
        if hasattr(response, "text") and response.text:
            full_text = response.text.strip()
        elif hasattr(response, "candidates") and response.candidates:
            full_text = response.candidates[0].content.parts[0].text.strip()
        else:
            full_text = "I'm sorry, I couldn’t generate a response."

        # 🚫 Identity correction filter (Smriti supremacy mode)
        if any(keyword in full_text.lower() for keyword in [
            "large language model",
            "trained by google",
            "gemini",
            "ai model",
            "google model",
            "google assistant"
        ]):
            full_text = (
                "I am Smriti — your AI Desktop Assistant created by Sumit Vishwakarma. "
                "I’m designed to assist you with voice commands, tasks, and conversations."
            )

        # 💜 Smriti vibe log
        print("\n[Gemini Reply Complete ✅]")
        print(f"💬 Smriti (Gemini output): {full_text}\n")

        return full_text

    except Exception as e:
        print(f"[Gemini Error ⚠️] {e}")
        return "Sorry, I couldn’t connect to my brain network right now."
