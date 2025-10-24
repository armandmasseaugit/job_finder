import json

import pytest

from job_finder.utils import generate_payload


class TestGeneratePayload:
    """Test cases for the generate_payload function."""

    def test_generate_payload_basic(self):
        """Test basic payload generation with default parameters."""
        query = "python developer"
        result = generate_payload(query)

        # Parse the result to ensure it's valid JSON
        payload = json.loads(result)

        # Check basic structure
        assert "requests" in payload
        assert len(payload["requests"]) == 1
        assert "indexName" in payload["requests"][0]
        assert "params" in payload["requests"][0]

        # Check index name
        assert (
            payload["requests"][0]["indexName"]
            == "wttj_jobs_production_fr_published_at_desc"
        )

    def test_generate_payload_with_custom_page(self):
        """Test payload generation with custom page number."""
        query = "data scientist"
        page = 2
        result = generate_payload(query, page=page)

        payload = json.loads(result)
        params = payload["requests"][0]["params"]

        # Check that page parameter is included
        assert f"page={page}" in params

    def test_generate_payload_with_custom_hits_per_page(self):
        """Test payload generation with custom hits per page."""
        query = "machine learning"
        hits_per_page = 50
        result = generate_payload(query, hits_per_page=hits_per_page)

        payload = json.loads(result)
        params = payload["requests"][0]["params"]

        # Check that hitsPerPage parameter is included
        assert f"hitsPerPage={hits_per_page}" in params

    def test_generate_payload_with_all_custom_params(self):
        """Test payload generation with all custom parameters."""
        query = "devops engineer"
        page = 3
        hits_per_page = 25
        result = generate_payload(query, page=page, hits_per_page=hits_per_page)

        payload = json.loads(result)
        params = payload["requests"][0]["params"]

        # Check all parameters
        assert f"page={page}" in params
        assert f"hitsPerPage={hits_per_page}" in params
        # URL encoded spaces become %20, not +
        assert f"query={query.replace(' ', '%20')}" in params

    def test_generate_payload_query_encoding(self):
        """Test that special characters in query are properly encoded."""
        query = "python & javascript"
        result = generate_payload(query)

        payload = json.loads(result)
        params = payload["requests"][0]["params"]

        # Check that query is properly encoded
        assert "query=" in params
        # The & should be URL encoded
        assert "javascript" in params

    def test_generate_payload_filters_present(self):
        """Test that required filters are present in the payload."""
        query = "frontend developer"
        result = generate_payload(query)

        payload = json.loads(result)
        params = payload["requests"][0]["params"]

        # Check that filters are present
        assert "filters=" in params
        assert "offices.country_code" in params
        assert "FR" in params
        assert "contract_type" in params
        assert "full_time" in params

    def test_generate_payload_required_fields(self):
        """Test that all required fields are present in the payload."""
        query = "backend developer"
        result = generate_payload(query)

        payload = json.loads(result)
        params = payload["requests"][0]["params"]

        # Check that essential parameters are present
        required_params = [
            "attributesToRetrieve",
            "responseFields",
            "facets",
            "clickAnalytics",
            "analytics",
            "userToken",
        ]

        for param in required_params:
            assert f"{param}=" in params

    @pytest.mark.parametrize(
        "query,page,hits_per_page",
        [
            ("python", 0, 30),
            ("data scientist", 1, 20),
            ("devops", 5, 50),
            ("", 0, 10),  # Empty query
        ],
    )
    def test_generate_payload_parametrized(self, query, page, hits_per_page):
        """Test payload generation with various parameter combinations."""
        result = generate_payload(query, page=page, hits_per_page=hits_per_page)

        # Should always return valid JSON
        payload = json.loads(result)
        assert "requests" in payload
        assert len(payload["requests"]) == 1

    def test_generate_payload_return_type(self):
        """Test that the function returns a string."""
        query = "test query"
        result = generate_payload(query)

        assert isinstance(result, str)
        # Should be valid JSON string
        json.loads(result)  # Should not raise an exception
