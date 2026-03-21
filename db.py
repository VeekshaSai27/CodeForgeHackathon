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
    """Build DSN at call time so Docker-injected env vars are always read."""
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
# Upsert helpers
# ---------------------------------------------------------------------------

def _upsert_skill(cur, name: str) -> str:
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


# ---------------------------------------------------------------------------
# Public persist functions (best-effort — caller catches exceptions)
# ---------------------------------------------------------------------------

def persist_analysis(conn, skill_dna: SkillDNA) -> None:
    with conn.cursor() as cur:
        for skill in skill_dna.skills:
            _upsert_skill(cur, skill)

        cur.execute(
            """
            INSERT INTO system_logs (service_name, event_type, payload)
            VALUES (%s, %s, %s)
            """,
            (
                "skill_intelligence_service",
                "analyze_profile",
                psycopg2.extras.Json({
                    "skills": skill_dna.skills,
                    "importance": skill_dna.importance,
                    "confidence": skill_dna.confidence,
                }),
            ),
        )


def persist_assessment(conn, rows: list[dict]) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO system_logs (service_name, event_type, payload)
            VALUES (%s, %s, %s)
            """,
            (
                "skill_validation_service",
                "evaluate_test",
                psycopg2.extras.Json({"results": rows}),
            ),
        )


def persist_learning_path(conn, path_items: list[dict]) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO system_logs (service_name, event_type, payload)
            VALUES (%s, %s, %s)
            """,
            (
                "skill_graph_engine",
                "compute_path",
                psycopg2.extras.Json({"learning_path": path_items}),
            ),
        )
