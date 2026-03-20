from skill_intelligence_service import build_skill_dna

sample_resume = """
John Doe — Software Engineer
- 3 years building web apps with React and TypeScript
- Developed REST APIs using Node.js and Express
- Deployed services on AWS (EC2, S3, Lambda)
- Familiar with PostgreSQL and basic ML concepts
- Led a team of 3 engineers (Agile/Scrum)
"""

sample_jd = """
We are looking for a Senior Full-Stack Engineer.
Requirements:
- Strong proficiency in React and TypeScript (4+ years)
- Backend experience with Node.js or Python
- Cloud experience (AWS preferred)
- Experience with CI/CD pipelines (GitHub Actions, Jenkins)
- Machine Learning experience is a plus
- Excellent communication and leadership skills
"""

if __name__ == "__main__":
    result = build_skill_dna(resume=sample_resume, jd=sample_jd)
    print(result.model_dump_json(indent=2))
