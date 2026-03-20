from services.skill_extractor import extract_skills
from services.question_generator import generate_questions
from services.evaluation_engine import evaluate
from services.confidence_engine import calculate_confidence
from utils.helpers import detect_exaggeration


def run_skill_validation(resume, jd):
    # Step 1: Extract skills
    skills = extract_skills(resume, jd)

    final_results = []

    for skill in skills:
        print("\n" + "="*60)
        print(f"🧠 Skill Test: {skill}")
        print("="*60)

        # Step 2: Generate questions
        questions = generate_questions(skill)

        user_answers = []

        # Step 3: Ask user questions
        for i, q in enumerate(questions):
            print(f"\nQ{i+1}: {q['question']}")
            print(f"Difficulty: {q['difficulty']}")

            if q["type"] == "mcq":
                for idx, opt in enumerate(q["options"]):
                    print(f"{chr(65+idx)}. {opt}")

            ans = input("Your Answer: ").strip()
            user_answers.append(ans)

        # Step 4: Evaluate answers
        proficiency, errors, correctness = evaluate(questions, user_answers)

        # Step 5: Confidence
        confidence = calculate_confidence(correctness)

        # Step 6: Weak areas
        weak_areas = list(errors.keys())

        # Step 7: Fraud detection
        claimed = input(f"\nClaimed level for {skill} (beginner/intermediate/expert): ").strip()
        fraud_flag = detect_exaggeration(claimed, proficiency)

        # Final result per skill
        result = {
            "skill": skill,
            "proficiency": round(proficiency, 2),
            "confidence": confidence,
            "weak_areas": weak_areas,
            "exaggeration_flag": fraud_flag
        }

        final_results.append(result)

        print("\n📊 Result:")
        print(result)

    return final_results


# 🚀 ENTRY POINT
if __name__ == "__main__":

    # You can replace this with real input later
    resume = input("Enter Resume:\n")
    jd = input("\nEnter Job Description:\n")

    print("\n🚀 Starting Skill Validation...\n")

    results = run_skill_validation(resume, jd)

    print("\n🏁 FINAL RESULTS:\n")
    for res in results:
        print(res)