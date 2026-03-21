import os
import re
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
#genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
genai.configure(api_key="AIzaSyDSZO7ZXCHzrZ32NNYjPrNqSlKzVVGCfSo")
model = genai.GenerativeModel("gemini-2.5-flash-lite")


def safe_parse_list(text):
    match = re.search(r"\[.*\]", text, re.DOTALL)
    if match:
        try:
            return eval(match.group())
        except:
            return []
    return []


def extract_skills_from_text(text, mode="jd"):

    if mode == "jd":
        prompt = f"""
        Extract ONLY technical skills from the following JOB DESCRIPTION.

        Return ONLY a Python list.
        No explanation.

        Text:
        {text}
        """
    else:
        prompt = f"""
        Extract ONLY technical skills from the following RESUME.

        Return ONLY a Python list.
        No explanation.

        Text:
        {text}
        """

    response = model.generate_content(prompt)
    skills_text = response.text.strip()

    skills = safe_parse_list(skills_text)

    return [s.lower() for s in skills]