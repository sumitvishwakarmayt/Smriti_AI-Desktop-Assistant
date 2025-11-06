import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("SMRITI_GEMINI_API_KEY"))

def ask_gemini(prompt):
    """
    Send a text prompt to Gemini and return its response.
    """
    try:
        print("🤖 Gemini: Thinking...")
        model = genai.GenerativeModel("models/gemini-2.5-flash")

        response = model.generate_content(
            prompt,
            generation_config={"temperature": 0.8, "top_p": 1.0, "max_output_tokens": 800},
            stream=False
        )

        text = response.text.strip() if response and hasattr(response, "text") else "Sorry, I couldn’t think of a reply."
        print(f"💬 Gemini says: {text}")
        return text

    except Exception as e:
        print(f"[Gemini Error]: {e}")
        return "Sorry, I couldn’t connect to my brain network right now."
