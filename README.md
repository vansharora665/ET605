# ET605 Merge System

Central backend for an adaptive Grades 6-8 mathematics platform. The service ingests session-end interaction payloads from independent chapter modules, computes a normalized performance score, recommends prerequisite chapters plus weak subtopics when a learner struggles, and predicts which chapter should come next.

If you want the simplest demo story, open [http://localhost:8000](http://localhost:8000). The root page is now a working browser demo built on top of the `/demo/*` endpoints and shows exactly what the admin platform receives after a chapter submission.

## Why this implementation

This project follows the user requirements and the revised Merge Team integration document. A few enhancements were added to make the demo more realistic and safer in production:

- PostgreSQL-ready configuration with SQLite fallback for local demo and tests
- Idempotent session ingestion using `session_id`
- Null-safe scoring that renormalizes weights when metrics are unavailable
- Optional `subtopic_metrics` support for weak-area recommendations
- Four dummy chapter definitions in [`seed_data/chapter_catalog.json`](/Users/vansharora665/ET605/seed_data/chapter_catalog.json)
- Three dummy external module examples under [`dummy_modules`](/Users/vansharora665/ET605/dummy_modules)
- Presentation explainer in [`docs/MERGE_SYSTEM_EXPLANATION.md`](/Users/vansharora665/ET605/docs/MERGE_SYSTEM_EXPLANATION.md)

## Tech stack

- FastAPI
- SQLAlchemy
- PostgreSQL or SQLite
- Pytest
- Docker / Render ready

## Quick share options

If you need to show this to a mentor quickly, there are now two deployment-friendly paths in the repo:

- `Dockerfile` for any container host
- `render.yaml` for one-click deployment on Render
- `Procfile` for simple platform process managers

Recommended demo hosting:

1. Push this repo to GitHub
2. Import it into Render
3. Render will detect [`render.yaml`](/Users/vansharora665/ET605/render.yaml)
4. The service will start with the same FastAPI app and expose `/`, `/docs`, and `/engine-explainer`

## Project structure

```text
app/
  api/routes/merge.py
  core/
  db/
  models/
  schemas/
  services/
  tests/
seed_data/seed.py
dummy_modules/
```

## Database schema

Core tables implemented:

1. `chapters`
2. `subtopics`
3. `student_sessions`
4. `interactions`

Enhancement:

- `interactions.subtopic_metrics` stores the optional subtopic-level extension from the revised integration spec.
- `student_sessions.performance_score` and `student_sessions.needs_recommendation` cache the derived recommendation state for fast lookups.
- Chapter progression stays manually editable in [`seed_data/chapter_catalog.json`](/Users/vansharora665/ET605/seed_data/chapter_catalog.json) through the `next_chapter_id` field.

## API endpoints

### Simple demo flow

These are the easiest endpoints to present:

1. `GET /demo/courses`
2. `POST /demo/submit`
3. `GET /demo/admin/{student_id}`

The 4 dummy courses are defined in [`seed_data/chapter_catalog.json`](/Users/vansharora665/ET605/seed_data/chapter_catalog.json), so you can manually edit them without touching the scoring code.

Example simple submission:

```json
{
  "student_id": "student_demo_simple",
  "chapter_id": "grade8_linear_equations",
  "correct_answers": 4,
  "wrong_answers": 6,
  "hints_used": 4,
  "retry_count": 3,
  "time_spent_seconds": 1500,
  "topic_completion_ratio": 0.52
}
```

Example admin delivery:

```json
{
  "student_id": "student_demo_simple",
  "submitted_chapter_id": "grade8_linear_equations",
  "submitted_chapter_name": "Linear Equations",
  "submitted_factors": {
    "correct_answers": 4,
    "wrong_answers": 6,
    "hints_used": 4,
    "retry_count": 3,
    "time_spent_seconds": 1500,
    "topic_completion_ratio": 0.52
  },
  "admin_delivery": {
    "session_id": "demo_student_demo_simple_grade8_linear_equations_xxxx",
    "delivered_at": "2026-03-31T10:30:00Z",
    "performance_score": 0.532,
    "needs_support": true,
    "prerequisite_recommendations": [
      "grade7_algebraic_expressions",
      "grade7_ratio_and_proportion"
    ],
    "weak_subtopics": [],
    "next_chapter_id": "grade7_algebraic_expressions",
    "next_chapter_name": "Algebraic Expressions",
    "decision_type": "remediation",
    "rationale": "Performance fell below the threshold, so the learner is routed to prerequisite revision before advancing."
  }
}
```

### `GET /merge/chapters`

Returns all chapter metadata with prerequisite links and subtopics.

### `POST /merge/interactions`

Accepts one session-end payload from a module team.

Important behavior:

- missing metrics are stored as `NULL`
- duplicate `session_id` updates the same session safely
- mismatched duplicate `session_id` across student/chapter pairs returns `409`
- random unknown fields are rejected

Example request:

```json
{
  "schema_version": "1.0",
  "student_id": "student_1042",
  "session_id": "sess_linear_001",
  "chapter_id": "grade8_linear_equations",
  "timestamp": "2026-03-31T10:30:00Z",
  "session_status": "abandoned",
  "correct_answers": 4,
  "wrong_answers": 6,
  "questions_attempted": 10,
  "total_questions": 12,
  "hints_used": 4,
  "total_hints_embedded": 8,
  "retry_count": 3,
  "time_spent_seconds": 1500,
  "topic_completion_ratio": 0.52,
  "subtopic_metrics": [
    {
      "subtopic_id": "grade8_linear_equations__solving_multi_step_equations",
      "questions_attempted": 6,
      "correct_answers": 2,
      "wrong_answers": 4,
      "hints_used": 3,
      "retry_count": 2,
      "time_spent_seconds": 700
    }
  ]
}
```

Example response:

```json
{
  "session_id": "sess_linear_001",
  "status": "created",
  "performance_score": 0.482,
  "needs_recommendation": true,
  "message": "Interaction ingested successfully"
}
```

### `GET /merge/recommendations/{student_id}`

Returns recommendation output for the student’s latest processed session. Optional query parameter: `chapter_id`.

Example response:

```json
{
  "student_id": "student_1042",
  "chapter_id": "grade8_linear_equations",
  "session_id": "sess_linear_001",
  "performance_score": 0.482,
  "needs_support": true,
  "threshold": 0.6,
  "based_on_timestamp": "2026-03-31T10:30:00Z",
  "recommendations": [
    "grade7_algebraic_expressions",
    "grade6_fractions"
  ],
  "weak_subtopics": [
    "Solving Multi-Step Equations"
  ]
}
```

### `GET /merge/next-chapter/{student_id}`

Returns the chapter the learner should see next based on their latest session.

Decision logic in the demo:

- no prior session: start at the first foundation chapter
- score below threshold: send learner to a prerequisite chapter
- incomplete or abandoned chapter: keep learner on the same chapter
- strong completed performance: advance to the `next_chapter_id` from the editable catalog

Example response:

```json
{
  "student_id": "student_1042",
  "current_chapter_id": "grade8_linear_equations",
  "current_chapter_name": "Linear Equations",
  "performance_score": 0.532,
  "decision_type": "remediation",
  "predicted_next_chapter_id": "grade7_algebraic_expressions",
  "predicted_next_chapter_name": "Algebraic Expressions",
  "threshold": 0.6,
  "support_recommendations": [
    "grade7_algebraic_expressions",
    "grade7_ratio_and_proportion"
  ],
  "weak_subtopics": [
    "Solving Multi-Step Equations"
  ],
  "rationale": "Performance fell below the threshold, so the learner is routed to prerequisite revision before advancing.",
  "based_on_timestamp": "2026-03-31T10:30:00Z"
}
```

## Scoring engine

The service supports two scoring profiles:

- `revised_spec` (default): follows the attached Merge Team document and includes completion ratio when available
- `assignment_core`: matches the original simplified formula from the assignment prompt

Default `revised_spec` formula:

```text
mastery_ratio = correct_answers / total_questions
attempt_coverage = questions_attempted / total_questions
hint_independence = 1 - (hints_used / total_hints_embedded)
retry_resilience = 1 - (retry_count / questions_attempted)
time_efficiency = expected_completion_time / time_spent_seconds
completion_ratio = topic_completion_ratio
difficulty_progress = attempt_coverage x (1 - 0.5 x difficulty_factor)
prerequisite_readiness = completion_ratio x (1 - 0.5 x prerequisite_factor)

score =
0.30 * mastery_ratio +
0.20 * attempt_coverage +
0.10 * hint_independence +
0.10 * retry_resilience +
0.10 * time_efficiency +
0.10 * completion_ratio +
0.05 * difficulty_progress +
0.05 * prerequisite_readiness
```

When a metric is missing, that component is excluded and the remaining weights are renormalized to sum to `1.0`.

## Validation rules covered

- `correct_answers + wrong_answers <= total_questions`
- `correct_answers + wrong_answers <= questions_attempted`
- `questions_attempted <= total_questions`
- `completion_ratio` stays in `0..1`
- `hints_used <= total_hints_embedded`
- non-negative numeric counts only
- unknown JSON keys rejected

## Setup

### 1. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Seed demo chapter data

```bash
python -m seed_data.seed
```

The easiest place to manually edit the demo path is [`seed_data/chapter_catalog.json`](/Users/vansharora665/ET605/seed_data/chapter_catalog.json). You can change:

- chapter names
- prerequisites
- difficulty
- expected completion times
- `next_chapter_id` progression links

### 4. Run the API

```bash
uvicorn app.main:app --reload
```

Open [http://localhost:8000](http://localhost:8000) for the interactive demo page.
Open [http://localhost:8000/docs](http://localhost:8000/docs) for Swagger.

## Tests

Run:

```bash
pytest
```

Tests cover:

- metadata retrieval
- demo course listing
- simple demo submission to admin delivery
- admin-side summary retrieval
- next chapter prediction for a new learner
- invalid payload rejection
- idempotent ingestion
- recommendation generation for low performance
- empty recommendation response for strong performance
- next chapter remediation and end-of-path outcomes

## Notes

- For a real deployment, set `DATABASE_URL` to PostgreSQL as shown in [`.env.example`](/Users/vansharora665/ET605/.env.example).
- The dummy module samples are contract examples only; the Merge System remains the main backend being implemented.
