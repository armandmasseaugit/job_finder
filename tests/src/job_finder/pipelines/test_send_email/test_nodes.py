from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from job_finder.pipelines.send_email.nodes import filter_new_jobs, send_email


class TestFilterNewJobs:
    """Test cases for the filter_new_jobs function."""

    def test_filter_new_jobs_recent_jobs(self):
        """Test filtering jobs published within the last 2 days."""
        # Create test data with recent dates
        yesterday = datetime.now() - timedelta(days=1)
        today = datetime.now()
        old_date = datetime.now() - timedelta(days=5)

        test_data = pd.DataFrame(
            {
                "name": ["Recent Job 1", "Recent Job 2", "Old Job"],
                "company_name": ["Company A", "Company B", "Company C"],
                "publication_date": [yesterday, today, old_date],
            }
        )

        result = filter_new_jobs(test_data)

        # Should return only the 2 recent jobs
        assert len(result) == 2
        job_names = [job["name"] for job in result]
        assert "Recent Job 1" in job_names
        assert "Recent Job 2" in job_names
        assert "Old Job" not in job_names

    def test_filter_new_jobs_no_recent_jobs(self):
        """Test when no jobs are recent enough."""
        # Create test data with only old dates
        old_date1 = datetime.now() - timedelta(days=5)
        old_date2 = datetime.now() - timedelta(days=10)

        test_data = pd.DataFrame(
            {
                "name": ["Old Job 1", "Old Job 2"],
                "company_name": ["Company A", "Company B"],
                "publication_date": [old_date1, old_date2],
            }
        )

        result = filter_new_jobs(test_data)

        assert len(result) == 0

    def test_filter_new_jobs_edge_case_exactly_2_days(self):
        """Test edge case where job is exactly 2 days old."""
        exactly_2_days_ago = datetime.now() - timedelta(days=2, seconds=1)
        recent_date = datetime.now() - timedelta(days=1)

        test_data = pd.DataFrame(
            {
                "name": ["Edge Case Job", "Recent Job"],
                "company_name": ["Company A", "Company B"],
                "publication_date": [exactly_2_days_ago, recent_date],
            }
        )

        result = filter_new_jobs(test_data)

        # Should only include the recent job, not the one exactly 2 days ago
        assert len(result) == 1
        assert result[0]["name"] == "Recent Job"

    def test_filter_new_jobs_string_dates(self):
        """Test with string dates that need conversion."""
        yesterday_str = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        old_date_str = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")

        test_data = pd.DataFrame(
            {
                "name": ["Recent Job", "Old Job"],
                "company_name": ["Company A", "Company B"],
                "publication_date": [yesterday_str, old_date_str],
            }
        )

        result = filter_new_jobs(test_data)

        assert len(result) == 1
        assert result[0]["name"] == "Recent Job"

    def test_filter_new_jobs_invalid_dates(self):
        """Test handling of invalid dates."""
        yesterday = datetime.now() - timedelta(days=1)

        test_data = pd.DataFrame(
            {
                "name": ["Valid Job", "Invalid Date Job"],
                "company_name": ["Company A", "Company B"],
                "publication_date": [yesterday, "invalid-date"],
            }
        )

        result = filter_new_jobs(test_data)

        # Should only include the job with valid date
        assert len(result) == 1
        assert result[0]["name"] == "Valid Job"

    def test_filter_new_jobs_empty_dataframe(self):
        """Test with empty DataFrame."""
        test_data = pd.DataFrame(columns=["name", "company_name", "publication_date"])
        result = filter_new_jobs(test_data)

        assert len(result) == 0
        assert isinstance(result, list)

    def test_filter_new_jobs_return_format(self):
        """Test that the function returns the correct format."""
        yesterday = datetime.now() - timedelta(days=1)

        test_data = pd.DataFrame(
            {
                "name": ["Test Job"],
                "company_name": ["Test Company"],
                "publication_date": [yesterday],
                "url": ["https://example.com/job"],
                "salary": [50000],
            }
        )

        result = filter_new_jobs(test_data)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], dict)

        # Check that all original columns are preserved
        job = result[0]
        assert job["name"] == "Test Job"
        assert job["company_name"] == "Test Company"
        assert job["url"] == "https://example.com/job"
        assert job["salary"] == 50000


class TestSendEmail:
    """Test cases for the send_email function."""

    @patch("job_finder.pipelines.send_email.nodes.smtplib.SMTP_SSL")
    @patch("job_finder.pipelines.send_email.nodes.credentials")
    @patch("job_finder.pipelines.send_email.nodes.logger")
    def test_send_email_success(self, mock_logger, mock_credentials, mock_smtp):
        """Test successful email sending."""
        # Mock credentials
        mock_credentials.get.return_value = "test_password"

        # Mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        # Test data
        new_jobs = [
            {
                "name": "Python Developer",
                "company_name": "Tech Corp",
                "url": "https://example.com/job1",
            },
            {
                "name": "Data Scientist",
                "company_name": "AI Corp",
                "url": "https://example.com/job2",
            },
        ]

        config = {
            "email_from": "sender@example.com",
            "email_to": "recipient@example.com",
        }

        # Call function
        send_email(new_jobs, config)

        # Verify SMTP operations
        mock_smtp.assert_called_once_with("smtp.gmail.com", 465)
        mock_server.login.assert_called_once_with("sender@example.com", "test_password")
        mock_server.sendmail.assert_called_once()

        # Verify logging
        mock_logger.info.assert_called_once_with("Sent email with %d new offers.", 2)

    @patch("job_finder.pipelines.send_email.nodes.smtplib.SMTP_SSL")
    @patch("job_finder.pipelines.send_email.nodes.credentials")
    def test_send_email_empty_jobs_list(self, mock_credentials, mock_smtp):
        """Test sending email with empty jobs list."""
        mock_credentials.get.return_value = "test_password"
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        new_jobs = []
        config = {
            "email_from": "sender@example.com",
            "email_to": "recipient@example.com",
        }

        # Should not raise an exception
        send_email(new_jobs, config)

        # Should still attempt to send email (even with 0 jobs)
        mock_server.sendmail.assert_called_once()

    @patch("job_finder.pipelines.send_email.nodes.smtplib.SMTP_SSL")
    @patch("job_finder.pipelines.send_email.nodes.credentials")
    def test_send_email_content_format(self, mock_credentials, mock_smtp):
        """Test that email content is formatted correctly."""
        mock_credentials.get.return_value = "test_password"
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        new_jobs = [
            {
                "name": "Python Developer",
                "company_name": "Tech Corp",
                "url": "https://example.com/job1",
            }
        ]

        config = {
            "email_from": "sender@example.com",
            "email_to": "recipient@example.com",
        }

        send_email(new_jobs, config)

        # Get the call arguments to check email content
        call_args = mock_server.sendmail.call_args[0]
        email_from = call_args[0]
        email_to = call_args[1]
        email_content = call_args[2]

        assert email_from == "sender@example.com"
        assert email_to == "recipient@example.com"
        assert "Python Developer" in email_content
        assert "Tech Corp" in email_content
        assert "https://example.com/job1" in email_content
        # The subject is base64 encoded in the email content, so check for the raw text in body
        assert "Python Developer at Tech Corp" in email_content

    @patch("job_finder.pipelines.send_email.nodes.smtplib.SMTP_SSL")
    @patch("job_finder.pipelines.send_email.nodes.credentials")
    def test_send_email_missing_url(self, mock_credentials, mock_smtp):
        """Test email sending when job doesn't have URL."""
        mock_credentials.get.return_value = "test_password"
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        new_jobs = [
            {
                "name": "Python Developer",
                "company_name": "Tech Corp",
                # No 'url' field
            }
        ]

        config = {
            "email_from": "sender@example.com",
            "email_to": "recipient@example.com",
        }

        # Should not raise an exception
        send_email(new_jobs, config)

        # Check that "No URL" is used as fallback
        call_args = mock_server.sendmail.call_args[0]
        email_content = call_args[2]
        assert "No URL" in email_content

    @patch("job_finder.pipelines.send_email.nodes.smtplib.SMTP_SSL")
    @patch("job_finder.pipelines.send_email.nodes.credentials")
    @patch("job_finder.pipelines.send_email.nodes.logger")
    def test_send_email_smtp_exception(self, mock_logger, mock_credentials, mock_smtp):
        """Test handling of SMTP exceptions."""
        mock_credentials.get.return_value = "test_password"
        mock_server = MagicMock()
        mock_server.login.side_effect = Exception("SMTP Error")
        mock_smtp.return_value.__enter__.return_value = mock_server

        new_jobs = [{"name": "Test Job", "company_name": "Test Corp"}]
        config = {
            "email_from": "sender@example.com",
            "email_to": "recipient@example.com",
        }

        # Should raise the exception (not handled in current implementation)
        with pytest.raises(Exception, match="SMTP Error"):
            send_email(new_jobs, config)
