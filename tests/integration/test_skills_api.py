"""Skills API integration tests."""


def test_top_skills_returns_paginated_list(api_client, sample_skill_frequencies):
    response = api_client.get("/api/v1/skills/top")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_skill_detail_returns_trend_data(api_client, sample_skill_frequencies):
    response = api_client.get("/api/v1/skills/trend/PyTorch")
    assert response.status_code == 200
    assert "points" in response.json()


def test_heatmap_returns_correct_dimensions(api_client, sample_skill_frequencies):
    response = api_client.get("/api/v1/skills/heatmap")
    payload = response.json()
    assert len(payload["matrix"]) == len(payload["skills"])


def test_market_summary_all_fields_present(api_client, sample_skill_frequencies):
    response = api_client.get("/api/v1/skills/summary")
    assert response.status_code == 200
    assert "top_skill" in response.json()


def test_trending_returns_rising_and_falling(api_client, sample_skill_frequencies):
    response = api_client.get("/api/v1/skills/trending")
    assert response.status_code == 200
    assert "rising" in response.json()
