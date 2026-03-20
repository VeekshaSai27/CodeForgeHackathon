import json
from services.gemini_service import generate_response


def safe_json_parse(text):
    try:
        return json.loads(text)
    except:
        start = text.find("[")
        end = text.rfind("]") + 1
        return json.loads(text[start:end])


def extract_skills(resume, jd):
    prompt = f"""
    Extract ONLY common technical skills from resume and job description.

    Return STRICT JSON list.

    Resume:
    {resume}

    Job Description:
    {jd}
    """

    response = generate_response(prompt)
    return safe_json_parse(response)