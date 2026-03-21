def compute_features(resume_skills, jd_skills):
    data = []

    all_skills = list(set(jd_skills + resume_skills))

    dependency_dict = {
        "python": 0.3,
        "sql": 0.2,
        "machine learning": 0.8,
        "deep learning": 1.0,
        "pandas": 0.5
    }

    for skill in all_skills:

        # Importance
        importance = 1 if skill in jd_skills else 0.2

        # Confidence
        confidence = 1 if skill in resume_skills else 0

        # Gap
        gap = 1 - confidence

        # Dependency
        dependency = dependency_dict.get(skill, 0.4)

        label = 1 if importance > 0.6 and gap > 0.5 else 0

        data.append({
            "skill": skill,
            "importance": importance,
            "gap": gap,
            "dependency": dependency,
            "confidence": confidence,
            "label": label
        })

    return data