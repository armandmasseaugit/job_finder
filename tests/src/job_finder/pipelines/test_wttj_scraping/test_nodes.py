import html
import re
from unittest.mock import Mock, patch, MagicMock

import pandas as pd
import pytest
import requests

from job_finder.pipelines.wttj_scraping.nodes import (
    clean_html_description,
    get_job_details,
    wttj_query_and_parsing,
    jobs_filtering,
    s3_uploading,
)


class TestCleanHtmlDescription:
    """Test cases for the clean_html_description function."""

    def test_clean_html_description_empty_string(self):
        """Test with empty string."""
        result = clean_html_description("")
        assert result == ""

    def test_clean_html_description_none(self):
        """Test with None input."""
        result = clean_html_description(None)
        assert result == ""

    def test_clean_html_description_simple_html(self):
        """Test with simple HTML tags."""
        html_text = "<p>This is a <strong>job description</strong> with HTML.</p>"
        result = clean_html_description(html_text)
        assert result == "This is a job description with HTML."

    def test_clean_html_description_html_entities(self):
        """Test with HTML entities."""
        html_text = "&lt;script&gt;alert('test')&lt;/script&gt; &amp; more text"
        result = clean_html_description(html_text)
        # HTML entities are decoded but HTML tags are removed
        assert result == "alert('test') & more text"

    def test_clean_html_description_cdata(self):
        """Test with CDATA sections."""
        html_text = "<![CDATA[This is CDATA content]]>"
        result = clean_html_description(html_text)
        assert result == "This is CDATA content"

    def test_clean_html_description_complex_html(self):
        """Test with complex HTML structure."""
        html_text = """
        <div class="job-description">
            <h2>Job Title</h2>
            <ul>
                <li>Requirement 1</li>
                <li>Requirement 2</li>
            </ul>
            <p>More details about the job.</p>
        </div>
        """
        result = clean_html_description(html_text)
        expected = "Job Title Requirement 1 Requirement 2 More details about the job."
        assert result == expected

    def test_clean_html_description_multiple_spaces(self):
        """Test that multiple spaces and newlines are cleaned."""
        html_text = "<p>Text   with    multiple\n\n\nspaces</p>"
        result = clean_html_description(html_text)
        assert result == "Text with multiple spaces"


class TestGetJobDetails:
    """Test cases for the get_job_details function."""

    @patch("job_finder.pipelines.wttj_scraping.nodes.logger")
    def test_get_job_details_success(self, mock_logger):
        """Test successful job details retrieval."""
        # Mock session and response
        mock_session = Mock(spec=requests.Session)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "job": {
                "description": "<p>Test job description</p>",
                "summary": "Test summary",
                "key_missions": ["Mission 1", "Mission 2"],
                "salary_min": 50000,
                "salary_max": 70000,
                "salary_currency": "EUR",
            }
        }
        mock_session.get.return_value = mock_response

        result = get_job_details(mock_session, "test-company", "test-job")

        assert result["description"] == "Test job description"
        assert result["summary"] == "Test summary"
        assert result["key_missions"] == ["Mission 1", "Mission 2"]
        assert result["salary_min"] == 50000
        assert result["salary_max"] == 70000
        assert result["salary_currency"] == "EUR"

    @patch("job_finder.pipelines.wttj_scraping.nodes.logger")
    def test_get_job_details_http_error(self, mock_logger):
        """Test handling of HTTP errors."""
        mock_session = Mock(spec=requests.Session)
        mock_response = Mock()
        mock_response.status_code = 404
        mock_session.get.return_value = mock_response

        result = get_job_details(mock_session, "test-company", "test-job")

        assert result == {}
        mock_logger.warning.assert_called_once()

    @patch("job_finder.pipelines.wttj_scraping.nodes.logger")
    def test_get_job_details_exception(self, mock_logger):
        """Test handling of exceptions."""
        mock_session = Mock(spec=requests.Session)
        mock_session.get.side_effect = requests.RequestException("Network error")

        result = get_job_details(mock_session, "test-company", "test-job")

        assert result == {}
        mock_logger.error.assert_called_once()

    @patch("job_finder.pipelines.wttj_scraping.nodes.logger")
    def test_get_job_details_missing_job_key(self, mock_logger):
        """Test handling of response without job key."""
        mock_session = Mock(spec=requests.Session)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"no_job_key": "data"}
        mock_session.get.return_value = mock_response

        result = get_job_details(mock_session, "test-company", "test-job")

        # Should return empty values but not crash
        assert result["description"] == ""
        assert result["summary"] == ""


class TestJobsFiltering:
    """Test cases for the jobs_filtering function."""

    def test_jobs_filtering_basic(self):
        """Test basic job filtering functionality."""
        # Create test DataFrame
        test_data = pd.DataFrame(
            {
                "name": [
                    "Python Developer",
                    "Java Engineer",
                    "Data Scientist Python",
                    "Frontend React Developer",
                    "Python Backend Engineer",
                ],
                "reference": ["ref1", "ref2", "ref3", "ref4", "ref5"],
                "company_name": [
                    "Company A",
                    "Company B",
                    "Company C",
                    "Company D",
                    "Company E",
                ],
            }
        )

        queries = ["python", "data"]
        result = jobs_filtering(test_data, queries)

        # Should return jobs containing 'python' or 'data' (case insensitive)
        expected_names = [
            "Python Developer",
            "Data Scientist Python",
            "Python Backend Engineer",
        ]
        assert len(result) == 3
        assert all(name in result["name"].values for name in expected_names)

    def test_jobs_filtering_case_insensitive(self):
        """Test that filtering is case insensitive."""
        test_data = pd.DataFrame(
            {
                "name": ["PYTHON Developer", "python engineer", "PyThOn specialist"],
                "reference": ["ref1", "ref2", "ref3"],
            }
        )

        queries = ["python"]
        result = jobs_filtering(test_data, queries)

        assert len(result) == 3

    def test_jobs_filtering_remove_duplicates(self):
        """Test that duplicate references are removed."""
        test_data = pd.DataFrame(
            {
                "name": ["Python Developer", "Python Developer", "Java Developer"],
                "reference": ["ref1", "ref1", "ref2"],  # Duplicate reference
            }
        )

        queries = ["python"]
        result = jobs_filtering(test_data, queries)

        # Should have only one Python Developer due to duplicate removal
        assert len(result) == 1
        assert result.iloc[0]["name"] == "Python Developer"

    def test_jobs_filtering_no_matches(self):
        """Test filtering when no jobs match the query."""
        test_data = pd.DataFrame(
            {"name": ["Java Developer", "C++ Engineer"], "reference": ["ref1", "ref2"]}
        )

        queries = ["python"]
        result = jobs_filtering(test_data, queries)

        assert len(result) == 0

    def test_jobs_filtering_empty_dataframe(self):
        """Test filtering with empty DataFrame."""
        test_data = pd.DataFrame(columns=["name", "reference"])
        queries = ["python"]
        result = jobs_filtering(test_data, queries)

        assert len(result) == 0


class TestS3Uploading:
    """Test cases for the s3_uploading function."""

    @patch("job_finder.pipelines.wttj_scraping.nodes.datetime")
    def test_s3_uploading_basic(self, mock_datetime):
        """Test basic s3_uploading functionality."""
        # Mock datetime
        mock_datetime.now.return_value.isoformat.return_value = "2023-10-14T10:30:00"

        # Create test DataFrame
        test_data = pd.DataFrame(
            {
                "name": ["Python Developer", "Java Engineer"],
                "company_name": ["Company A", "Company B"],
            }
        )

        result_df, result_metadata = s3_uploading(test_data)

        # Check that provider column is added
        assert "provider" in result_df.columns
        assert all(result_df["provider"] == "Welcome to the jungle")

        # Check metadata
        assert result_metadata["last_scrape"] == "2023-10-14T10:30:00"

    def test_s3_uploading_preserves_original_data(self):
        """Test that original data is preserved."""
        test_data = pd.DataFrame(
            {
                "name": ["Python Developer"],
                "company_name": ["Company A"],
                "salary": [50000],
            }
        )

        result_df, _ = s3_uploading(test_data)

        # Original columns should be preserved
        assert "name" in result_df.columns
        assert "company_name" in result_df.columns
        assert "salary" in result_df.columns
        assert result_df.iloc[0]["name"] == "Python Developer"
        assert result_df.iloc[0]["salary"] == 50000

    def test_s3_uploading_empty_dataframe(self):
        """Test s3_uploading with empty DataFrame."""
        test_data = pd.DataFrame()
        result_df, result_metadata = s3_uploading(test_data)

        assert "provider" in result_df.columns
        assert len(result_df) == 0
        assert "last_scrape" in result_metadata


class TestWttjQueryAndParsing:
    """Test cases for the wttj_query_and_parsing function."""

    @patch("job_finder.pipelines.wttj_scraping.nodes.requests.Session")
    @patch("job_finder.pipelines.wttj_scraping.nodes.get_job_details")
    @patch("job_finder.pipelines.wttj_scraping.nodes.generate_payload")
    @patch("job_finder.pipelines.wttj_scraping.nodes.time.sleep")
    def test_wttj_query_and_parsing_basic(
        self,
        mock_sleep,
        mock_generate_payload,
        mock_get_job_details,
        mock_session_class,
    ):
        """Test basic wttj_query_and_parsing functionality."""
        # Mock generate_payload
        mock_generate_payload.return_value = '{"test": "payload"}'

        # Mock job details
        mock_get_job_details.return_value = {
            "description": "Test description",
            "summary": "Test summary",
        }

        # Mock session and response
        mock_session = Mock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [
                {
                    "hits": [
                        {
                            "organization": {
                                "name": "Test Company",
                                "slug": "test-company",
                                "logo": {"url": "https://example.com/logo.png"},
                            },
                            "slug": "test-job",
                            "reference": "ref123",
                            "name": "Python Developer",
                            "published_at_date": "2023-10-14",
                            "published_at": "2023-10-14T10:00:00",
                            "remote": "flexible",
                            "education_level": "bachelor",
                            "offices": [{"city": "Paris", "country": "France"}],
                        }
                    ]
                    + [
                        {
                            "organization": {"name": "Empty", "logo": {"url": ""}},
                            "offices": [{"city": "Empty", "country": "Empty"}],
                        }
                    ]
                    * 29  # Fill to 30 items with minimal organization data
                }
            ]
        }
        mock_session.post.return_value = mock_response

        headers = {"test": "header"}
        queries = ["python"]
        pages = 1

        result = wttj_query_and_parsing(headers, queries, pages)

        # Should return a DataFrame
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 30  # One query * one page * 30 hits processed

        # Check first row has the correct data from the mock
        first_row = result.iloc[0]
        assert first_row["company_name"] == "Test Company"
        assert first_row["name"] == "Python Developer"
        assert first_row["city"] == "Paris"
        assert result.iloc[0]["name"] == "Python Developer"
        assert result.iloc[0]["company_name"] == "Test Company"
        assert result.iloc[0]["description"] == "Test description"

    @patch("job_finder.pipelines.wttj_scraping.nodes.requests.Session")
    def test_wttj_query_and_parsing_empty_queries(self, mock_session_class):
        """Test with empty queries list."""
        mock_session = Mock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        headers = {"test": "header"}
        queries = []
        pages = 1

        result = wttj_query_and_parsing(headers, queries, pages)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
