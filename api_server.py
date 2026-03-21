"""
api_server.py — Unified backend for the Skill Intelligence Platform.

Endpoints (match frontend/src/lib/api.ts exactly):
  POST /analyze-profile
  POST /generate-test
  POST /evaluate-test
  POST /compute-path
  POST /chat
"""

import os
import sys
import uuid
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from skill_intelligence_service import build_skill_dna
from skill_graph_engine import run_engine
from skill_validation_service.services.question_generator import generate_questions
from skill_validation_service.services.evaluation_engine import evaluate
from skill_validation_service.services.confidence_engine import calculate_confidence
from shared.gemini_pool import generate_with_retry
from db import get_conn, persist_analysis, persist_assessment, persist_skill_scores, persist_learning_path

# ---------------------------------------------------------------------------
# App + rate limiter
# ---------------------------------------------------------------------------

app = Flask(__name__)
CORS(app, origins=os.getenv("CORS_ORIGINS", "*"))

limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["60/minute"],
    storage_uri="memory://",
)

# ---------------------------------------------------------------------------
# Session store — keyed by session token, thread-safe
# ---------------------------------------------------------------------------

_sessions: dict[str, dict] = {}
_sessions_lock = threading.Lock()

SESSION_HEADER = "X-Session-Token"


def _get_session() -> tuple[str, dict]:
    token = request.headers.get(SESSION_HEADER) or str(uuid.uuid4())
    with _sessions_lock:
        if token not in _sessions:
            _sessions[token] = {}
        return token, _sessions[token]


def _session_response(token: str, data: dict) -> dict:
    return {SESSION_HEADER: token, **data}


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.post("/analyze-profile")
@limiter.limit("20/minute")
def analyze_profile():
    token, session = _get_session()
    body = request.get_json(force=True)
    resume: str = body.get("resume", "")
    jd: str = body.get("jd", "")

    skill_dna = build_skill_dna(resume=resume, jd=jd)
    session["skill_dna"] = skill_dna
    session["proficiency"] = {}

    try:
        with get_conn() as conn:
            user_id = persist_analysis(conn, skill_dna, token)
            session["user_id"] = user_id
    except Exception as e:
        app.logger.warning(f"DB persist_analysis failed: {e}")

    return jsonify(_session_response(token, {
        "skills": skill_dna.skills,
        "importance_scores": skill_dna.importance,
        "user_confidence": skill_dna.confidence,
    }))


@app.post("/generate-test")
@limiter.limit("20/minute")
def generate_test():
    token, session = _get_session()
    body = request.get_json(force=True)
    skills: list[str] = body.get("skills", [])

    if not skills:
        skill_dna = session.get("skill_dna")
        skills = skill_dna.skills if skill_dna else []

    if not skills:
        return jsonify({"error": "No skills provided and no active session found."}), 400

    skill_questions: dict[str, list] = {}
    with ThreadPoolExecutor(max_workers=min(len(skills), 5)) as pool:
        futures = {pool.submit(generate_questions, skill): skill for skill in skills}
        for future in as_completed(futures):
            skill = futures[future]
            try:
                skill_questions[skill] = future.result() or []
            except Exception as e:
                app.logger.warning(f"Question generation failed for {skill}: {e}")
                skill_questions[skill] = []

    session["skill_questions"] = skill_questions

    flat: list[dict] = []
    for skill, qs in skill_questions.items():
        for i, q in enumerate(qs):
            q_type = q.get("type", "mcq")
            entry = {
                "id": f"{skill}__{i}",
                "skill": skill,
                "question": q.get("question", ""),
                "options": q.get("options", []),
                "correct_answer": q.get("answer", ""),
                "type": q.get("type", "mcq"),
                "difficulty": q.get("difficulty", "medium"),
                "concept": q.get("concept", skill),
            }
            if q_type == "coding":
                entry["starterCode"] = q.get("starterCode", "")
                entry["language"] = q.get("language", "javascript")
            flat.append(entry)

    return jsonify(_session_response(token, {"questions": flat}))


@app.post("/evaluate-test")
@limiter.limit("20/minute")
def evaluate_test():
    token, session = _get_session()
    body = request.get_json(force=True)
    raw_answers: dict[str, str] = body.get("answers", {})

    skill_questions: dict[str, list] = session.get("skill_questions", {})
    if not skill_questions:
        return jsonify({"error": "No active test session. Call /generate-test first."}), 400

    skill_answers: dict[str, list] = {}
    for key, chosen in raw_answers.items():
        skill, idx = key.rsplit("__", 1)
        n = len(skill_questions.get(skill, []))
        skill_answers.setdefault(skill, [None] * n)
        skill_answers[skill][int(idx)] = chosen

    proficiency_map: dict[str, float] = {}
    weak_areas: list[str] = []
    assessment_rows: list[dict] = []

    for skill, qs in skill_questions.items():
        answers = skill_answers.get(skill, [])
        proficiency, errors, correctness = evaluate(qs, answers)
        confidence = calculate_confidence(correctness)
        proficiency_map[skill] = round(proficiency, 2)
        weak_areas.extend(errors.keys())
        assessment_rows.append({
            "skill": skill,
            "score": round(proficiency, 2),
            "confidence": confidence,
        })

    session["proficiency"] = proficiency_map

    try:
        user_id = session.get("user_id")
        if user_id:
            # Annotate questions with user answers + correctness for persistence
            annotated: dict[str, list] = {}
            for skill, qs in skill_questions.items():
                skill_ans = skill_answers.get(skill, [])
                annotated_qs = []
                for i, q in enumerate(qs):
                    user_ans = skill_ans[i] if i < len(skill_ans) else None
                    annotated_qs.append({
                        **q,
                        "user_answer": user_ans,
                        "is_correct": user_ans == q.get("answer") if user_ans else False,
                    })
                annotated[skill] = annotated_qs
            with get_conn() as conn:
                persist_assessment(conn, user_id, assessment_rows, annotated)
    except Exception as e:
        app.logger.warning(f"DB persist_assessment failed: {e}")

    return jsonify(_session_response(token, {
        "proficiency": proficiency_map,
        "weak_areas": list(set(weak_areas)),
    }))


@app.post("/compute-path")
@limiter.limit("20/minute")
def compute_path():
    token, session = _get_session()
    body = request.get_json(force=True)

    skill_dna = session.get("skill_dna")
    if skill_dna is None:
        return jsonify({"error": "No skill profile found. Call /analyze-profile first."}), 400

    proficiency: dict[str, float] = (
        body.get("proficiency")
        or session.get("proficiency")
        or {}
    )

    result = run_engine(skill_dna=skill_dna, proficiency=proficiency)
    learning_path = result.learning_path
    G = result.graph
    scores = result.scores
    weights = result.weights

    next_set = set(learning_path.next_skills)
    path_items: list[dict] = []

    for item in learning_path.roadmap:
        if item.skill in next_set:
            status = "current"
        elif proficiency.get(item.skill, 0.0) >= 0.4:
            status = "completed"
        else:
            status = "locked"

        path_items.append({
            "skill": item.skill,
            "status": status,
            "priority_score": item.score,
            "reasoning": item.reason,
            "prerequisites": item.prerequisites,
            "resources": [],
        })

    try:
        user_id = session.get("user_id")
        if user_id:
            with get_conn() as conn:
                persist_skill_scores(conn, user_id, G, scores)
                persist_learning_path(conn, user_id, path_items, weights)
    except Exception as e:
        app.logger.warning(f"DB persist_learning_path failed: {e}")

    return jsonify(_session_response(token, {"learning_path": path_items}))


@app.post("/chat")
@limiter.limit("30/minute")
def chat():
    token, session = _get_session()
    body = request.get_json(force=True)
    message: str = body.get("message", "")
    context = body.get("context", {})

    skill_dna = session.get("skill_dna")
    skills_ctx = skill_dna.skills if skill_dna else []
    proficiency = session.get("proficiency", {})

    prompt = f"""You are an AI learning mentor for a personalized skill development platform.
User's skill profile: {skills_ctx}
User's proficiency scores: {proficiency}
Additional context: {context}

User message: {message}

Reply concisely (2-4 sentences). Be encouraging and specific to their actual skills."""

    response_text = generate_with_retry(
        prompt,
        temperature=0.7,
        response_mime_type="text/plain",
    )
    return jsonify(_session_response(token, {"response": response_text}))


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    port = int(os.getenv("API_PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
