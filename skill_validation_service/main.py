from flask import Flask, request, jsonify

from services.skill_extractor import extract_skills
from services.question_generator import generate_questions
from services.evaluation_engine import evaluate
from services.confidence_engine import calculate_confidence
from utils.helpers import detect_exaggeration

app = Flask(__name__)

# 🔹 Store questions temporarily (simple memory storage)
session_data = {}


# ✅ API 1: Generate Test
@app.route('/generate-test', methods=['POST'])
def generate_test():
    data = request.json

    resume = data.get("resume")
    jd = data.get("jd")

    skills = extract_skills(resume, jd)

    all_questions = {}

    for skill in skills:
        questions = generate_questions(skill)
        all_questions[skill] = questions

    # Save for evaluation later
    session_data["questions"] = all_questions

    return jsonify({
        "skills": skills,
        "questions": all_questions
    })


# ✅ API 2: Evaluate Test
@app.route('/evaluate-test', methods=['POST'])
def evaluate_test():
    data = request.json

    user_answers = data.get("answers")  
    claimed_levels = data.get("claimed_levels")

    questions = session_data.get("questions", {})

    final_results = []

    for skill in questions:
        q_list = questions[skill]
        answers = user_answers.get(skill, [])

        proficiency, errors, correctness = evaluate(q_list, answers)
        confidence = calculate_confidence(correctness)

        weak_areas = list(errors.keys())

        claimed = claimed_levels.get(skill, "beginner")
        fraud_flag = detect_exaggeration(claimed, proficiency)

        result = {
            "skill": skill,
            "proficiency": round(proficiency, 2),
            "confidence": confidence,
            "weak_areas": weak_areas,
            "exaggeration_flag": fraud_flag
        }

        final_results.append(result)

    return jsonify({
        "results": final_results
    })


if __name__ == '__main__':
    app.run(debug=True)