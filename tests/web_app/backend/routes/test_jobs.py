from unittest.mock import patch


class TestJobsRoutes:
    """Test job-related API endpoints."""

    @patch("web_app.backend.routes.jobs.get_offers_")
    def test_get_offers(self, mock_get_offers, test_client):
        """Test getting job offers."""
        mock_get_offers.return_value = [
            {"reference": "1", "name": "Test Job", "company_name": "Test Company"}
        ]

        response = test_client.get("/offers")
        assert response.status_code == 200
        result = response.json()
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["reference"] == "1"
        assert result[0]["name"] == "Test Job"
        mock_get_offers.assert_called_once()

    @patch("web_app.backend.routes.jobs.get_offers_")
    def test_get_offers_with_query(self, mock_get_offers, test_client):
        """Test getting job offers with search query."""
        mock_get_offers.return_value = [
            {"id": "1", "title": "Python Developer", "company": "TechCorp"},
            {"id": "2", "title": "Data Scientist", "company": "DataCorp"},
        ]

        response = test_client.get("/offers?query=python")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @patch("web_app.backend.routes.jobs.get_likes_")
    def test_get_likes(self, mock_get_likes, test_client):
        """Test getting user likes."""
        mock_get_likes.return_value = {"liked": ["1", "2"], "disliked": ["3"]}

        response = test_client.get("/likes")
        assert response.status_code == 200
        assert "liked" in response.json()
        assert "disliked" in response.json()
        mock_get_likes.assert_called_once()

    @patch("web_app.backend.routes.jobs.get_relevance_")
    def test_get_relevance(self, mock_get_relevance, test_client):
        """Test getting job relevance scores."""
        mock_get_relevance.return_value = {"1": 0.95, "2": 0.80}

        response = test_client.get("/relevance")
        assert response.status_code == 200
        assert response.json() == {"1": 0.95, "2": 0.80}
        mock_get_relevance.assert_called_once()

    @patch("web_app.backend.routes.jobs.update_like")
    def test_like_job(self, mock_update_like, test_client):
        """Test liking a job."""
        job_id = "123"
        feedback = "like"

        response = test_client.post(f"/likes/{job_id}?feedback={feedback}")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
        mock_update_like.assert_called_once_with(job_id, feedback)

    @patch("web_app.backend.routes.jobs.update_like")
    def test_dislike_job(self, mock_update_like, test_client):
        """Test disliking a job."""
        job_id = "456"
        feedback = "dislike"

        response = test_client.post(f"/likes/{job_id}?feedback={feedback}")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
        mock_update_like.assert_called_once_with(job_id, feedback)
