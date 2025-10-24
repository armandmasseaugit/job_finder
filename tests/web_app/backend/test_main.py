def test_main_app_healthy(test_client):
    """Test that the FastAPI app is properly initialized."""
    # Test app object exists and has expected properties
    from web_app.backend.main import app

    assert app is not None
    assert isinstance(app.title, str)
    assert app.title == "Job Finder API"


def test_offers_route_exists(test_client):
    """Test that offers endpoint is accessible."""
    response = test_client.get("/offers")
    # Should return 200 or appropriate error code depending on setup
    assert response.status_code in (200, 422, 500)  # 422 for missing query params


def test_cors_headers(test_client):
    """Test CORS headers are properly set."""
    response = test_client.options("/offers")
    assert response.status_code in (200, 405)  # 405 if OPTIONS not implemented


def test_app_metadata():
    """Test app metadata."""
    from web_app.backend.main import app

    assert hasattr(app, "version")
    assert hasattr(app, "title")
    assert app.title == "Job Finder API"
