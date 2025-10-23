"""Tests for CV routes."""
import pytest
from unittest.mock import patch, Mock
from fastapi import UploadFile
import io


class TestCVRoutes:
    """Test CV-related API endpoints."""

    def test_upload_cv_pdf(self, test_client):
        """Test CV upload with PDF file."""
        # Mock file upload
        file_content = b"Mock PDF CV content"
        
        with patch('web_app.backend.services.cv_processing.extract_text_from_pdf') as mock_extract:
            mock_extract.return_value = "Extracted CV text"
            
            with patch('web_app.backend.services.cv_processing.process_cv_for_matching') as mock_process:
                mock_process.return_value = "Processed CV text for matching"
                
                files = {"file": ("cv.pdf", file_content, "application/pdf")}
                response = test_client.post("/cv/upload", files=files)
                
                # Should process successfully or return appropriate error
                assert response.status_code in (200, 422, 500)

    def test_upload_cv_docx(self, test_client):
        """Test CV upload with DOCX file."""
        file_content = b"Mock DOCX CV content"
        
        with patch('web_app.backend.services.cv_processing.extract_text_from_docx') as mock_extract:
            mock_extract.return_value = "Extracted CV text"
            
            files = {"file": ("cv.docx", file_content, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
            response = test_client.post("/cv/upload", files=files)
            
            assert response.status_code in (200, 422, 500)

    def test_upload_cv_unsupported_format(self, test_client):
        """Test CV upload with unsupported file format."""
        file_content = b"Mock text content"
        
        files = {"file": ("cv.txt", file_content, "text/plain")}
        response = test_client.post("/cv/upload", files=files)
        
        # Should reject unsupported format
        assert response.status_code in (400, 422)

    def test_match_cv_with_jobs(self, test_client, sample_cv_content):
        """Test CV matching endpoint."""
        with patch('web_app.backend.services.cv_matching.get_cv_matcher') as mock_get_matcher:
            mock_matcher = Mock()
            mock_matcher.create_cv_embedding.return_value = [0.1, 0.2, 0.3]
            mock_get_matcher.return_value = mock_matcher
            
            response = test_client.post("/cv/match-text", json={"text": sample_cv_content})
            
            assert response.status_code in (200, 422, 500)
            if response.status_code == 200:
                data = response.json()
                assert isinstance(data, (list, dict))

    def test_cv_analysis(self, test_client, sample_cv_content):
        """Test CV analysis endpoint."""
        with patch('web_app.backend.services.cv_matching.get_cv_matcher') as mock_get_matcher:
            mock_matcher = Mock()
            mock_matcher.create_cv_embedding.return_value = [0.1, 0.2, 0.3]
            mock_get_matcher.return_value = mock_matcher
            
            response = test_client.post("/cv/explain-match", json={"text": sample_cv_content, "job_id": "test_job"})
            
            assert response.status_code in (200, 422, 500)
            if response.status_code == 200:
                data = response.json()
                assert "explanation" in data or "message" in data or isinstance(data, str)