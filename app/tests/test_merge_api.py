from __future__ import annotations


def struggling_payload() -> dict:
    return {
        "schema_version": "1.0",
        "student_id": "student_1042",
        "session_id": "sess_linear_001",
        "chapter_id": "grade8_linear_equations",
        "timestamp": "2026-03-31T10:30:00Z",
        "session_status": "exited_midway",
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
                "subtopic_id": "grade8_linear_equations__solving_one_step_equations",
                "questions_attempted": 4,
                "correct_answers": 2,
                "wrong_answers": 2,
                "hints_used": 1,
                "retry_count": 1,
                "time_spent_seconds": 300,
            },
            {
                "subtopic_id": "grade8_linear_equations__solving_multi_step_equations",
                "questions_attempted": 6,
                "correct_answers": 2,
                "wrong_answers": 4,
                "hints_used": 3,
                "retry_count": 2,
                "time_spent_seconds": 700,
            },
        ],
    }


def strong_payload() -> dict:
    return {
        "schema_version": "1.0",
        "student_id": "student_1042",
        "session_id": "sess_linear_002",
        "chapter_id": "grade8_linear_equations",
        "timestamp": "2026-03-31T11:15:00Z",
        "session_status": "completed",
        "correct_answers": 10,
        "wrong_answers": 0,
        "questions_attempted": 10,
        "total_questions": 10,
        "hints_used": 0,
        "total_hints_embedded": 4,
        "retry_count": 0,
        "time_spent_seconds": 900,
        "topic_completion_ratio": 1.0,
    }


def test_get_chapters_returns_seeded_metadata(client):
    response = client.get("/merge/chapters")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 4
    assert body[0]["chapter_id"] == "grade6_fractions"
    assert body[3]["chapter_id"] == "grade8_linear_equations"
    assert body[3]["subtopics"][1]["subtopic_id"].endswith("multi_step_equations")


def test_demo_courses_are_listed(client):
    response = client.get("/demo/courses")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 4
    assert body[0]["chapter_id"] == "grade6_fractions"
    assert body[3]["chapter_id"] == "grade8_linear_equations"


def test_root_returns_demo_page(client):
    response = client.get("/")

    assert response.status_code == 200
    assert "Student chapter experience + team API call + Merge System recommendation" in response.text
    assert "/demo/session/complete" in response.text
    assert "/demo/session/exit" in response.text
    assert "Best Demo Guide" in response.text
    assert "Open Engine Explainer" in response.text


def test_demo_course_detail_returns_questions(client):
    response = client.get("/demo/courses/grade8_linear_equations")

    assert response.status_code == 200
    body = response.json()
    assert body["chapter_id"] == "grade8_linear_equations"
    assert len(body["questions"]) == 5
    assert body["questions"][0]["prompt"]


def test_post_interaction_is_idempotent(client):
    first_response = client.post("/merge/interactions", json=struggling_payload())
    second_response = client.post("/merge/interactions", json=struggling_payload())

    assert first_response.status_code == 201
    assert first_response.json()["status"] == "created"
    assert second_response.status_code == 200
    assert second_response.json()["status"] == "updated"


def test_next_chapter_starts_from_first_dummy_chapter_when_no_history(client):
    response = client.get("/merge/next-chapter/student_fresh")

    assert response.status_code == 200
    body = response.json()
    assert body["decision_type"] == "start_path"
    assert body["predicted_next_chapter_id"] == "grade6_fractions"


def test_post_interaction_rejects_invalid_counts(client):
    payload = struggling_payload()
    payload["correct_answers"] = 8
    payload["wrong_answers"] = 7
    payload["total_questions"] = 12

    response = client.post("/merge/interactions", json=payload)

    assert response.status_code == 422
    assert response.json()["detail"] == "Payload validation failed"


def test_recommendations_return_prerequisites_and_weak_subtopics(client):
    client.post("/merge/interactions", json=struggling_payload())

    response = client.get("/merge/recommendations/student_1042")

    assert response.status_code == 200
    body = response.json()
    assert body["needs_support"] is True
    assert body["recommendations"] == [
        "grade7_algebraic_expressions",
        "grade7_ratio_and_proportion",
    ]
    assert "Solving Multi-Step Equations" in body["weak_subtopics"]


def test_recommendations_are_empty_for_strong_performance(client):
    client.post("/merge/interactions", json=strong_payload())

    response = client.get(
        "/merge/recommendations/student_1042",
        params={"chapter_id": "grade8_linear_equations"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["needs_support"] is False
    assert body["recommendations"] == []


def test_next_chapter_advances_for_strong_performance(client):
    client.post("/merge/interactions", json=strong_payload())

    response = client.get("/merge/next-chapter/student_1042")

    assert response.status_code == 200
    body = response.json()
    assert body["decision_type"] == "complete_path"
    assert body["predicted_next_chapter_id"] is None


def test_next_chapter_routes_to_remediation_for_low_performance(client):
    client.post("/merge/interactions", json=struggling_payload())

    response = client.get("/merge/next-chapter/student_1042")

    assert response.status_code == 200
    body = response.json()
    assert body["decision_type"] == "remediation"
    assert body["predicted_next_chapter_id"] == "grade7_algebraic_expressions"


def test_demo_submit_delivers_admin_ready_summary(client):
    response = client.post(
        "/demo/submit",
        json={
            "student_id": "student_demo_simple",
            "chapter_id": "grade8_linear_equations",
            "correct_answers": 1,
            "wrong_answers": 2,
            "hints_used": 2,
            "retry_count": 2,
            "time_spent_seconds": 1500,
            "topic_completion_ratio": 0.52,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["submitted_chapter_id"] == "grade8_linear_equations"
    assert body["admin_delivery"]["decision_type"] == "remediation"
    assert body["admin_delivery"]["next_chapter_id"] == "grade7_algebraic_expressions"


def test_demo_admin_view_returns_latest_summary(client):
    client.post(
        "/demo/submit",
        json={
            "student_id": "student_admin_view",
            "chapter_id": "grade7_algebraic_expressions",
            "correct_answers": 3,
            "wrong_answers": 0,
            "hints_used": 1,
            "retry_count": 1,
            "time_spent_seconds": 700,
            "topic_completion_ratio": 1.0,
        },
    )

    response = client.get("/demo/admin/student_admin_view")

    assert response.status_code == 200
    body = response.json()
    assert body["decision_type"] == "advance"
    assert body["next_chapter_id"] == "grade8_linear_equations"


def test_student_session_submission_returns_team_payload_and_recommendation(client):
    response = client.post(
        "/demo/student-session",
        json={
            "student_id": "student_player",
            "chapter_id": "grade8_linear_equations",
            "time_spent_seconds": 1500,
            "confidence_level": 1,
            "focus_level": 2,
            "study_mode": "guided",
            "ended_early": True,
            "answers": [
                {
                    "question_id": "g8l_q1",
                    "selected_option_index": 0,
                    "attempts": 1,
                    "hint_opened": True
                },
                {
                    "question_id": "g8l_q2",
                    "selected_option_index": 0,
                    "attempts": 2,
                    "hint_opened": True
                },
                {
                    "question_id": "g8l_q3",
                    "selected_option_index": 1,
                    "attempts": 2,
                    "hint_opened": True
                }
            ]
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["team_api_submission"]["endpoint"] == "/merge/interactions"
    assert body["team_api_submission"]["payload"]["correct_answers"] == 0
    assert body["team_api_submission"]["payload"]["session_status"] == "exited_midway"
    assert body["admin_summary"]["decision_type"] == "remediation"
    assert body["next_chapter_id"] == "grade7_algebraic_expressions"
    assert body["performance_band"] == "intensive_support"
    assert body["normalized_score_explanation"]["weights_sum"] == 1.0
    assert body["recommendation_parameters"]["struggle_index"] is not None
    assert body["recommendation_parameters"]["readiness_index"] is not None
    assert "low_confidence" in body["observed_patterns"]
    assert body["learner_signals"]["ended_early"] is True


def test_engine_explanation_returns_step_by_step_breakdown(client):
    client.post(
        "/demo/student-session",
        json={
            "student_id": "student_explainer",
            "chapter_id": "grade8_linear_equations",
            "time_spent_seconds": 1500,
            "confidence_level": 2,
            "focus_level": 2,
            "study_mode": "revision",
            "ended_early": True,
            "answers": [
                {
                    "question_id": "g8l_q1",
                    "selected_option_index": 0,
                    "attempts": 1,
                    "hint_opened": True
                },
                {
                    "question_id": "g8l_q2",
                    "selected_option_index": 0,
                    "attempts": 2,
                    "hint_opened": True
                },
                {
                    "question_id": "g8l_q3",
                    "selected_option_index": 1,
                    "attempts": 2,
                    "hint_opened": True
                }
            ]
        },
    )

    response = client.get("/demo/engine-explanation/student_explainer")

    assert response.status_code == 200
    body = response.json()
    assert body["payload"]["session_status"] == "exited_midway"
    assert body["score_steps"][0]["name"] == "accuracy"
    assert body["decision_type"] == "remediation"
    assert body["next_chapter_id"] == "grade7_algebraic_expressions"
    assert body["validation_checks"][0]["passed"] is True
    assert body["recommendation_parameters"]["struggle_index"] is not None
    assert "renormalizing the remaining weights" in body["normalized_score_summary"]


def test_session_exit_allows_zero_attempt_payload_and_uses_exit_endpoint(client):
    response = client.post(
        "/demo/session/exit",
        json={
            "student_id": "student_auto_exit",
            "session_id": "play_student_auto_exit_grade7_ratio_and_proportion_deadbeef",
            "chapter_id": "grade7_ratio_and_proportion",
            "session_started_at": "2026-03-31T11:00:00Z",
            "time_spent_seconds": 0,
            "confidence_level": 2,
            "focus_level": 2,
            "study_mode": "guided",
            "ended_early": True,
            "answers": [
                {
                    "question_id": "g7r_q1",
                    "selected_option_index": None,
                    "attempts": 0,
                    "hint_opened": False
                },
                {
                    "question_id": "g7r_q2",
                    "selected_option_index": None,
                    "attempts": 0,
                    "hint_opened": False
                },
                {
                    "question_id": "g7r_q3",
                    "selected_option_index": None,
                    "attempts": 0,
                    "hint_opened": False
                },
                {
                    "question_id": "g7r_q4",
                    "selected_option_index": None,
                    "attempts": 0,
                    "hint_opened": False
                },
                {
                    "question_id": "g7r_q5",
                    "selected_option_index": None,
                    "attempts": 0,
                    "hint_opened": False
                }
            ]
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["performance_score"] == 0.0
    assert body["team_api_submission"]["payload"]["session_status"] == "exited_midway"
    assert body["team_api_submission"]["payload"]["questions_attempted"] == 0
    assert body["team_api_submission"]["payload"]["time_spent_seconds"] > 0
