from dotenv import load_dotenv

load_dotenv()

from shared.gemini_pool import generate_with_retry


def generate_response(prompt: str) -> str:
    try:
        return generate_with_retry(
            prompt,
            temperature=0.2,
            response_mime_type="text/plain",
        )
    except Exception as e:
        print("❌ Gemini Error:", e)
        return ""
