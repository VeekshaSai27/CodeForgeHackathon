"""
db.py — PostgreSQL persistence layer.

Uses psycopg2. All functions accept an open connection so the caller
controls transaction boundaries. get_conn() returns a context-managed
connection that auto-commits on exit.
"""

import os
from contextlib import contextmanager

import psycopg2
import psycopg2.extras

from skill_intelligence_service.models import SkillDNA


def _build_dsn() -> str:
    return (
        f"host={os.getenv('POSTGRES_HOST', 'localhost')} "
        f"port={os.getenv('POSTGRES_PORT', '5432')} "
        f"dbname={os.getenv('POSTGRES_DB', 'skill_platform')} "
        f"user={os.getenv('POSTGRES_USER', 'skill_user')} "
        f"password={os.getenv('POSTGRES_PASSWORD', 'changeme')}"
    )


@contextmanager
def get_conn():
    conn = psycopg2.connect(_build_dsn())
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _upsert_user(cur, session_token: str) -> str:
    """Upsert an anonymous user keyed by session token. Returns user_id."""
    cur.execute(
        """
        INSERT INTO users (name, email)
        VALUES (%s, %s)
        ON CONFLICT (email) DO UPDATE SET name = EXCLUDED.name
        RETURNING id
        """,
        (f"user_{session_token[:8]}", f"{session_token}@session.local"),
    )
    return cur.fetchone()[0]


def _upsert_skill(cur, name: str) -> str:
    """Upsert a skill by name. Returns skill_id."""
    cur.execute(
        """
        INSERT INTO skills (name)
        VALUES (%s)
        ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name
        RETURNING id
        """,
        (name,),
    )
    return cur.fetchone()[0]


def _get_skill_id(cur, name: str) -> str | None:
    cur.execute("SELECT id FROM skills WHERE name = %s", (name,))
    row = cur.fetchone()
    return row[0] if row else None


def _log(cur, service: str, event: str, payload: dict) -> None:
    cur.execute(
        """
        INSERT INTO system_logs (service_name, event_type, payload)
        VALUES (%s, %s, %s)
        """,
        (service, event, psycopg2.extras.Json(payload)),
    )


# ---------------------------------------------------------------------------
# Public persist functions
# ---------------------------------------------------------------------------

def persist_analysis(conn, skill_dna: SkillDNA, session_token: str) -> str:
    """
    Persists:
      - users (upsert by session token)
      - user_profiles (resume placeholder)
      - skills (upsert each skill)
      - user_skills (confidence per skill)
      - job_roles + job_role_skills (importance per skill)
      - system_logs

    Returns user_id for use in subsequent calls.
    """
    with conn.cursor() as cur:
        user_id = _upsert_user(cur, session_token)

        # user_profiles — upsert
        cur.execute(
            """
            INSERT INTO user_profiles (user_id, preferences)
            VALUES (%s, %s)
            ON CONFLICT (user_id) DO NOTHING
            """,
            (user_id, psycopg2.extras.Json({})),
        )

        # Upsert a job role for this session
        cur.execute(
            """
            INSERT INTO job_roles (title, description)
            VALUES (%s, %s)
            RETURNING id
            """,
            (f"session_{session_token[:8]}", "Auto-generated from JD analysis"),
        )
        job_role_id = cur.fetchone()[0]

        for skill in skill_dna.skills:
            skill_id = _upsert_skill(cur, skill)

            # user_skills
            cur.execute(
                """
                INSERT INTO user_skills (user_id, skill_id, confidence_score, source)
                VALUES (%s, %s, %s, 'resume')
                ON CONFLICT (user_id, skill_id)
                DO UPDATE SET confidence_score = EXCLUDED.confidence_score
                """,
                (user_id, skill_id, skill_dna.confidence.get(skill, 0.0)),
            )

            # job_role_skills
            cur.execute(
                """
                INSERT INTO job_role_skills (job_role_id, skill_id, importance_score)
                VALUES (%s, %s, %s)
                ON CONFLICT (job_role_id, skill_id)
                DO UPDATE SET importance_score = EXCLUDED.importance_score
                """,
                (job_role_id, skill_id, skill_dna.importance.get(skill, 0.5)),
            )

        _log(cur, "skill_intelligence_service", "analyze_profile", {
            "user_id": str(user_id),
            "skills": skill_dna.skills,
            "importance": skill_dna.importance,
            "confidence": skill_dna.confidence,
        })

    return str(user_id)


def persist_assessment(conn, user_id: str, rows: list[dict], skill_questions: dict) -> None:
    """
    Persists:
      - assessments (one per skill)
      - assessment_questions (each question + user answer)
      - system_logs
    """
    with conn.cursor() as cur:
        for row in rows:
            skill_name = row["skill"]
            skill_id = _get_skill_id(cur, skill_name)
            if not skill_id:
                skill_id = _upsert_skill(cur, skill_name)

            difficulty = (
                "beginner" if row["score"] < 0.4 else
                "intermediate" if row["score"] < 0.7 else
                "advanced"
            )

            cur.execute(
                """
                INSERT INTO assessments (user_id, skill_id, score, difficulty_level)
                VALUES (%s, %s, %s, %s)
                RETURNING id
                """,
                (user_id, skill_id, row["score"], difficulty),
            )
            assessment_id = cur.fetchone()[0]

            for q in skill_questions.get(skill_name, []):
                cur.execute(
                    """
                    INSERT INTO assessment_questions
                        (assessment_id, question_text, options, correct_answer, user_answer, is_correct)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        assessment_id,
                        q.get("question", ""),
                        psycopg2.extras.Json(q.get("options", [])),
                        q.get("answer", ""),
                        q.get("user_answer"),
                        q.get("is_correct"),
                    ),
                )

        _log(cur, "skill_validation_service", "evaluate_test", {
            "user_id": str(user_id),
            "results": rows,
        })


def persist_skill_scores(conn, user_id: str, G, scores: dict[str, float]) -> None:
    """
    Persists:
      - skill_scores (importance, proficiency, confidence, final_score per skill)
      - skill_graph_nodes
      - skill_graph_edges
    """
    with conn.cursor() as cur:
        skill_id_map: dict[str, str] = {}

        for skill in G.nodes:
            skill_id = _upsert_skill(cur, skill)
            skill_id_map[skill] = skill_id

            attrs = G.nodes[skill]

            # skill_scores
            cur.execute(
                """
                INSERT INTO skill_scores
                    (user_id, skill_id, importance, proficiency, dependency_score, confidence, final_score)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    user_id,
                    skill_id,
                    attrs.get("importance", 0.5),
                    attrs.get("proficiency", 0.0),
                    scores.get(skill, 0.0),
                    attrs.get("confidence", 0.0),
                    scores.get(skill, 0.0),
                ),
            )

            # skill_graph_nodes
            cur.execute(
                """
                INSERT INTO skill_graph_nodes (skill_id, metadata)
                VALUES (%s, %s)
                ON CONFLICT (skill_id)
                DO UPDATE SET metadata = EXCLUDED.metadata
                """,
                (skill_id, psycopg2.extras.Json(dict(attrs))),
            )

        for src, dst in G.edges:
            src_id = skill_id_map.get(src)
            dst_id = skill_id_map.get(dst)
            if src_id and dst_id:
                cur.execute(
                    """
                    INSERT INTO skill_graph_edges (from_skill_id, to_skill_id, created_by)
                    VALUES (%s, %s, 'system')
                    ON CONFLICT (from_skill_id, to_skill_id) DO NOTHING
                    """,
                    (src_id, dst_id),
                )


def persist_learning_path(conn, user_id: str, path_items: list[dict], weights: dict) -> None:
    """
    Persists:
      - learning_paths
      - learning_path_nodes (ordered, with score + reasoning)
      - decision_logs (weights used)
      - system_logs
    """
    with conn.cursor() as cur:
        # Deactivate previous paths for this user
        cur.execute(
            "UPDATE learning_paths SET is_active = FALSE WHERE user_id = %s",
            (user_id,),
        )

        cur.execute(
            """
            INSERT INTO learning_paths (user_id, is_active)
            VALUES (%s, TRUE)
            RETURNING id
            """,
            (user_id,),
        )
        path_id = cur.fetchone()[0]

        for idx, item in enumerate(path_items):
            skill_id = _get_skill_id(cur, item["skill"])
            if not skill_id:
                skill_id = _upsert_skill(cur, item["skill"])

            cur.execute(
                """
                INSERT INTO learning_path_nodes
                    (path_id, skill_id, order_index, score, reasoning, status)
                VALUES (%s, %s, %s, %s, %s, 'active')
                ON CONFLICT (path_id, skill_id) DO NOTHING
                """,
                (path_id, skill_id, idx, item.get("priority_score", 0.0), item.get("reasoning", "")),
            )

        # Log the weights used for this decision
        cur.execute(
            """
            INSERT INTO decision_logs (user_id, input_data, output_data)
            VALUES (%s, %s, %s)
            """,
            (
                user_id,
                psycopg2.extras.Json({"weights": weights}),
                psycopg2.extras.Json({"path_length": len(path_items)}),
            ),
        )

        _log(cur, "skill_graph_engine", "compute_path", {
            "user_id": str(user_id),
            "learning_path": path_items,
        })
