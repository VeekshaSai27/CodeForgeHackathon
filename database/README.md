# Database Service

PostgreSQL schema for the AI-driven personalized learning platform.

## Setup

```bash
cp .env.example .env
docker compose up -d
```

Schema is auto-applied on first boot via `docker-entrypoint-initdb.d`.

---

## Domain → Table Map

| Domain | Tables |
|---|---|
| User | `users`, `user_profiles` |
| Skill Intelligence | `skills`, `user_skills`, `job_roles`, `job_role_skills` |
| Skill Validation | `assessments`, `assessment_questions` |
| Skill Graph | `skill_graph_nodes`, `skill_graph_edges` |
| Decision Engine | `skill_scores`, `learning_paths`, `learning_path_nodes` |
| Learning Experience | `resources`, `user_progress` |
| Journey Tracking | `user_journeys`, `journey_events` |
| Observability | `system_logs`, `decision_logs` |

---

## Key Relationships

```
users
 ├── user_profiles          (1:1)
 ├── user_skills            (M:N via skills)
 ├── assessments            (1:N)
 ├── skill_scores           (1:N)
 ├── learning_paths         (1:N)
 │    └── learning_path_nodes (1:N via skills)
 ├── user_progress          (M:N via skills)
 └── user_journeys          (1:N via learning_paths)
      └── journey_events    (1:N)

skills
 ├── skill_graph_nodes      (1:1)
 ├── skill_graph_edges      (M:N self-referential — from/to)
 ├── job_role_skills        (M:N via job_roles)
 └── resources              (1:N)
```

---

## Indexing Strategy

| Index Type | Columns | Reason |
|---|---|---|
| B-Tree | `user_id` on all user-linked tables | Fast per-user lookups across all services |
| B-Tree | `skill_id` on all skill-linked tables | Fast skill graph + scoring queries |
| B-Tree | `job_role_id` on `job_role_skills` | JD-to-skill resolution |
| B-Tree DESC | `created_at`, `computed_at`, `timestamp` | Efficient time-range log queries |
| B-Tree | `from_skill_id`, `to_skill_id` on edges | Graph traversal in both directions |
| GIN | `preferences`, `payload`, `metadata` (JSONB) | Flexible key-based JSONB filtering |

---

## Service Interaction Model

Each service talks to the DB via its own API — no direct cross-service DB coupling.

```
Skill Intelligence  →  skills, user_skills, job_roles, job_role_skills
Skill Validation    →  assessments, assessment_questions
Skill Graph Engine  →  skill_graph_nodes, skill_graph_edges, skill_scores, learning_paths
Learning Experience →  resources, user_progress, user_journeys, journey_events
All services        →  system_logs, decision_logs
```

---

## Scalability Notes

- **Partitioning**: `system_logs`, `journey_events`, and `skill_scores` are high-write tables — partition by `created_at` (monthly) when volume grows.
- **Read replicas**: Attach a read replica for the Decision Engine's scoring queries without impacting writes.
- **JSONB flexibility**: `preferences`, `metadata`, and `payload` columns absorb schema changes without migrations.
- **Soft deletes**: Add `deleted_at TIMESTAMPTZ` to `users` and `learning_paths` if audit retention is required.
- **Connection pooling**: Use PgBouncer in front of PostgreSQL when running multiple service instances.
