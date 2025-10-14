import os
from unittest.mock import patch

from fastapi.testclient import TestClient

with patch.dict(
    os.environ,
    {
        "AWS_ACCESS_KEY_ID": "fake-access-key",
        "AWS_SECRET_ACCESS_KEY": "fake-secret-key",
        "AWS_BUCKET_NAME": "fake-bucket",
        "AWS_REGION": "fake-region",
    },
):
    from web_app.backend.main import app

client = TestClient(app)


@patch("web_app.backend.routes.jobs.get_offers_")
def test_get_offers(mock_get_offers):
    mock_get_offers.return_value = [{"id": "1", "title": "Test Job"}]

    response = client.get("/offers")
    assert response.status_code == 200
    assert response.json() == [{"id": "1", "title": "Test Job"}]
    mock_get_offers.assert_called_once()


@patch("web_app.backend.routes.jobs.get_likes_")
def test_get_likes(mock_get_likes):
    mock_get_likes.return_value = {"liked": ["1", "2"], "disliked": ["3"]}

    response = client.get("/likes")
    assert response.status_code == 200
    assert "liked" in response.json()
    assert "disliked" in response.json()
    mock_get_likes.assert_called_once()


@patch("web_app.backend.routes.jobs.get_relevance_")
def test_get_relevance(mock_get_relevance):
    mock_get_relevance.return_value = {"1": 0.95, "2": 0.80}

    response = client.get("/relevance")
    assert response.status_code == 200
    assert response.json() == {"1": 0.95, "2": 0.80}
    mock_get_relevance.assert_called_once()


@patch("web_app.backend.routes.jobs.update_like")
def test_like_job(mock_update_like):
    job_id = "123"
    feedback = "like"

    response = client.post(f"/likes/{job_id}?feedback={feedback}")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    mock_update_like.assert_called_once_with(job_id, feedback)
