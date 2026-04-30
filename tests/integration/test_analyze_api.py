"""Analyze API integration tests."""


def test_analyze_skills_json_endpoint(api_client, sample_skill_frequencies):
    response = api_client.post(
        "/api/v1/analyze/skills",
        json={"session_id": "session-1", "target_role": "ml_engineer", "skills": ["Python", "PyTorch"]},
    )
    assert response.status_code == 200
    assert "gap_score" in response.json()


def test_gap_score_in_valid_range(api_client, sample_skill_frequencies):
    response = api_client.post(
        "/api/v1/analyze/skills",
        json={"session_id": "session-2", "target_role": "ml_engineer", "skills": ["Python"]},
    )
    assert 0 <= response.json()["gap_score"] <= 100


def test_generate_roadmap_from_analysis_id(api_client, sample_skill_frequencies):
    analysis = api_client.post(
        "/api/v1/analyze/skills",
        json={"session_id": "session-3", "target_role": "ml_engineer", "skills": ["Python"]},
    ).json()
    response = api_client.post(f"/api/v1/roadmap/{analysis['analysis_id']}?total_weeks=8")
    assert response.status_code == 200
    assert "phases" in response.json()


def test_subscribe_creates_subscription(api_client, sample_skill_frequencies):
    response = api_client.post("/api/v1/notifications/subscribe", json={"email": "test@example.com", "role_filter": "all"})
    assert response.status_code == 201


def test_duplicate_subscribe_returns_409(api_client, sample_skill_frequencies):
    api_client.post("/api/v1/notifications/subscribe", json={"email": "dupe@example.com", "role_filter": "all"})
    response = api_client.post("/api/v1/notifications/subscribe", json={"email": "dupe@example.com", "role_filter": "all"})
    assert response.status_code == 409
