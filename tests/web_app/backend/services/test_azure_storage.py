"""Tests for Azure Storage services."""
import json
from unittest.mock import Mock, patch

import pandas as pd


class TestAzureStorage:
    """Test Azure Storage functionality."""

    def test_get_offers(self):
        """Test getting offers from Azure storage."""
        with patch(
            "web_app.backend.services.azure_storage.pd.read_parquet"
        ) as mock_read_parquet:
            df = pd.DataFrame(
                [
                    {
                        "reference": "job1",
                        "name": "Data Scientist",
                        "company_name": "Company A",
                    },
                    {
                        "reference": "job2",
                        "name": "ML Engineer",
                        "company_name": "Company B",
                    },
                ]
            )
            mock_read_parquet.return_value = df

            with patch(
                "web_app.backend.services.azure_storage.get_blob_service_client"
            ) as mock_get_blob_client:
                mock_get_blob_client.return_value.get_blob_client.return_value.download_blob.return_value.readall.return_value = (
                    b"mock_data"
                )

                from web_app.backend.services.azure_storage import get_offers

                offers = get_offers()

                assert isinstance(offers, list)
                assert len(offers) == 2
                assert offers[0]["reference"] == "job1"
                assert offers[1]["name"] == "ML Engineer"

    def test_get_likes(self):
        """Test getting user likes from Azure storage."""
        mock_likes_data = {"job1": "like", "job2": "dislike"}

        with patch("web_app.backend.services.azure_storage.REDIS_AVAILABLE", False):
            with patch(
                "web_app.backend.services.azure_storage.get_blob_service_client"
            ) as mock_get_blob_client:
                mock_get_blob_client.return_value.get_blob_client.return_value.download_blob.return_value.readall.return_value = json.dumps(
                    mock_likes_data
                ).encode(
                    "utf-8"
                )

                from web_app.backend.services.azure_storage import get_likes

                likes = get_likes()

                assert isinstance(likes, dict)
                assert likes["job1"] == "like"
                assert likes["job2"] == "dislike"

    def test_get_relevance(self):
        """Test getting job relevance scores from Azure storage."""
        mock_relevance_data = {"job1": 0.9, "job2": 0.7}

        with patch("web_app.backend.services.azure_storage.REDIS_AVAILABLE", False):
            with patch(
                "web_app.backend.services.azure_storage.get_blob_service_client"
            ) as mock_get_blob_client:
                mock_get_blob_client.return_value.get_blob_client.return_value.download_blob.return_value.readall.return_value = json.dumps(
                    mock_relevance_data
                ).encode(
                    "utf-8"
                )

                from web_app.backend.services.azure_storage import get_relevance

                relevance = get_relevance()

                assert isinstance(relevance, dict)
                assert relevance["job1"] == 0.9
                assert relevance["job2"] == 0.7

    def test_update_like(self):
        """Test updating user like feedback."""
        existing_data = {"job1": "like"}

        with patch(
            "web_app.backend.services.azure_storage.get_blob_service_client"
        ) as mock_get_blob_client:
            # Mock download to return existing data
            mock_get_blob_client.return_value.get_blob_client.return_value.download_blob.return_value.readall.return_value = json.dumps(
                existing_data
            ).encode(
                "utf-8"
            )

            # Mock upload_blob to avoid the ContentSettings error
            mock_get_blob_client.return_value.get_blob_client.return_value.upload_blob = (
                Mock()
            )

            from web_app.backend.services.azure_storage import update_like

            # Should not raise an exception
            update_like("job1", "dislike")

            # Verify upload was called
            mock_get_blob_client.return_value.get_blob_client.return_value.upload_blob.assert_called_once()
