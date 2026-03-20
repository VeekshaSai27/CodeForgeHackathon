# Skill Intelligence Service

An AI-driven service that builds a **Skill DNA** profile by analyzing a user's resume against a job description.

Given raw resume and JD text, it:
- Extracts technical and soft skills (via inference, not just keyword matching)
- Normalizes skill names to canonical forms (e.g. `ReactJS` → `React`)
- Assigns an **importance score** (0–1) based on JD signals
- Estimates a **confidence score** (0–1) from resume signals

Powered by **Gemini 1.5 Flash**.

## Output

```json
{
  "skills": ["React", "TypeScript", "Node.js", "AWS"],
  "importance": {"React": 0.95, "TypeScript": 0.9, "Node.js": 0.8, "AWS": 0.7},
  "confidence": {"React": 0.75, "TypeScript": 0.7, "Node.js": 0.65, "AWS": 0.5}
}
```

## Project Structure

```
skill_intelligence_service/
├── __init__.py     # public API
├── models.py       # SkillDNA pydantic model
├── prompts.py      # LLM prompt template
└── service.py      # Gemini inference + validation
main.py             # entrypoint with sample data
requirements.txt
```

## Setup

1. Clone the repo and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and add your Gemini API key:
   ```bash
   cp .env.example .env
   ```
   ```
   GEMINI_API_KEY=your_key_here
   ```
   Get a key at [Google AI Studio](https://aistudio.google.com/app/apikey).

3. Run:
   ```bash
   python main.py
   ```
