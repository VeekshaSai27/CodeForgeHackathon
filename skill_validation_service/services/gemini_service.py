import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key
API_KEY = os.getenv("GEMINI_API_KEY")


if not API_KEY:
    raise ValueError("❌ GEMINI_API_KEY not found. Check your .env file")

# Configure Gemini
genai.configure(api_key=API_KEY)

# ✅ Use gemini-2.5-flash-lite
model = genai.GenerativeModel("gemini-2.5-flash-lite")


def generate_response(prompt: str) -> str:
    try:
        response = model.generate_content(prompt)
        
        if not response.text:
            raise ValueError("Empty response from Gemini")

        return response.text.strip()

    except Exception as e:
        print("❌ Gemini Error:", e)
        return ""