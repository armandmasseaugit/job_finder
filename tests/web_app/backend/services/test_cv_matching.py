"""Tests for CV matching services."""
from unittest.mock import Mock, patch

import numpy as np


class TestCVMatching:
    """Test CV matching functionality."""

    def test_cv_matcher_initialization(self):
        """Test CVMatcher initialization."""
        with patch("web_app.backend.services.cv_matching.SentenceTransformer"):
            with patch("web_app.backend.services.cv_matching.chromadb"):
                from web_app.backend.services.cv_matching import CVMatcher

                matcher = CVMatcher()
                assert matcher is not None

    def test_create_cv_embedding(self, sample_cv_content):
        """Test CV embedding creation."""
        with patch(
            "web_app.backend.services.cv_matching.SentenceTransformer"
        ) as mock_model:
            mock_model.return_value.encode.return_value = np.array([0.1, 0.2, 0.3])

            with patch("web_app.backend.services.cv_matching.chromadb"):
                from web_app.backend.services.cv_matching import CVMatcher

                matcher = CVMatcher()
                embedding = matcher.create_cv_embedding(sample_cv_content)

                assert isinstance(embedding, np.ndarray)
                assert len(embedding) > 0  # Just check it has content

    def test_get_collection_stats(self):
        """Test collection statistics retrieval."""
        mock_collection = Mock()
        mock_collection.count.return_value = 100
        mock_collection.peek.return_value = {
            "ids": ["1", "2"],
            "documents": ["doc1", "doc2"],
        }

        with patch("web_app.backend.services.cv_matching.SentenceTransformer"):
            with patch("web_app.backend.services.cv_matching.chromadb"):
                from web_app.backend.services.cv_matching import CVMatcher

                matcher = CVMatcher()
                # Prevent initialization from running by setting collection directly
                matcher.collection = mock_collection
                matcher.chroma_client = Mock()  # Mock client too

                stats = matcher.get_collection_stats()

                assert isinstance(stats, dict)
                assert "total_jobs" in stats
                assert stats["total_jobs"] == 100

    def test_get_cv_matcher_function(self):
        """Test get_cv_matcher function."""
        with patch("web_app.backend.services.cv_matching.CVMatcher"):
            from web_app.backend.services.cv_matching import get_cv_matcher

            matcher = get_cv_matcher()
            assert matcher is not None
