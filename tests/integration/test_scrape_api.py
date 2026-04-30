"""Scrape API integration tests."""


def test_trigger_scrape_returns_202(api_client, sample_skill_frequencies):
    response = api_client.post("/api/v1/scrape/trigger", json={"role": "ml engineer", "location": "india", "max_results": 2})
    assert response.status_code == 202


def test_scrape_status_returns_counts(api_client, sample_skill_frequencies):
    response = api_client.get("/api/v1/scrape/status")
    assert response.status_code == 200
    assert "posting_counts" in response.json()
