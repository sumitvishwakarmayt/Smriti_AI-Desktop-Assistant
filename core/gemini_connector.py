import os
import google.generativeai as genai
from dotenv import load_dotenv

# 🧩 Load environment variables (API key from .env)
load_dotenv()
api_key = os.getenv("SMRITI_GEMINI_API_KEY")

# ⚙️ Configure Gemini API (guard missing/invalid key)
if not api_key:
    print("[Gemini Error ⚠️] Missing SMRITI_GEMINI_API_KEY in environment/.env")
else:
    try:
        genai.configure(api_key=api_key)
        print("✅ Gemini API configured successfully")
    except Exception as e:
        print(f"[Gemini Config Error ⚠️] {e}")


def ask_gemini(prompt: str) -> str:
    """
    Sends user input to Gemini API and returns the response.
    Smriti-style processing with identity protection.
    """
    try:
        if not api_key:
            return "Gemini API key is not configured. Please set SMRITI_GEMINI_API_KEY."
        print(f"🧠 Smriti sending prompt to Gemini: {prompt}")

        # ✅ Use the correct model name
        model = genai.GenerativeModel("gemini-2.5-flash")

        # 🌀 Generate response (ask for concise output)
        concise_prefix = (
            "Answer concisely in at most one short paragraph (max 3 sentences). "
            "Avoid long lists unless explicitly requested.\n\nUser: "
        )
        response = model.generate_content(concise_prefix + prompt)
        full_text = ""

        # Handle response safely
        if hasattr(response, "text") and response.text:
            full_text = response.text.strip()
        elif hasattr(response, "candidates") and response.candidates:
            full_text = response.candidates[0].content.parts[0].text.strip()
        else:
            full_text = "I'm sorry, I couldn't generate a response."

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
                "I'm designed to assist you with voice commands, tasks, and conversations."
            )

        # Final safety: trim to one paragraph ~80-120 words
        def _trim_to_paragraph(text: str, max_words: int = 120) -> str:
            # Take up to the first blank-line paragraph
            paras = [p.strip() for p in text.split("\n\n") if p.strip()]
            first = paras[0] if paras else text.strip()
            words = first.split()
            if len(words) <= max_words:
                return first
            return " ".join(words[:max_words]) + "…"

        trimmed = _trim_to_paragraph(full_text)
        print(f"💬 Smriti (Gemini output): {trimmed}")
        return trimmed

    except Exception as e:
        print(f"[Gemini Error ⚠️] {e}")
        return "Sorry, I couldn't connect to my brain network right now."