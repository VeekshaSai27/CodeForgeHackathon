SKILL_EXTRACTION_PROMPT = """
You are a Skill Intelligence engine. Given a resume and a job description (JD), produce a structured skill profile.

## Instructions
1. **Extract** all relevant technical and soft skills from both the resume and JD. Infer skills from context — do not just keyword match (e.g., "built REST APIs" → infer "REST API Design").
2. **Normalize** skill names to canonical forms (e.g., "ReactJS" → "React", "Postgres" → "PostgreSQL", "ML" → "Machine Learning").
3. **Importance score** (0–1): How critical is this skill for the JD? (1.0 = explicitly required core skill, 0.0 = barely relevant)
4. **Confidence score** (0–1): How confident is the user in this skill based on resume signals? (years of experience, project depth, certifications, recency)
   - If a skill appears only in JD but NOT in resume → confidence = 0.0
   - If vague or implied → use 0.1–0.3
   - If clearly demonstrated with projects/experience → 0.6–1.0

## Handling missing/vague data
- If resume is empty or vague, set all confidence scores to 0.0
- If JD is empty or vague, assign uniform importance of 0.5 to all extracted skills
- Always return valid scores even with partial data

## Output
Return ONLY a valid JSON object with this exact structure — no explanation, no markdown:
{{
  "skills": ["Skill1", "Skill2"],
  "importance": {{"Skill1": 0.9, "Skill2": 0.6}},
  "confidence": {{"Skill1": 0.7, "Skill2": 0.2}}
}}

---
## Resume
{resume}

## Job Description
{jd}
"""
