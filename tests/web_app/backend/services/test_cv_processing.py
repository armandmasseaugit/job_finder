"""Tests for CV processing services."""
import pytest
from unittest.mock import Mock, patch, MagicMock
import io


class TestCVProcessing:
    """Test CV processing functionality."""

    @pytest.fixture
    def mock_pdf_content(self):
        """Mock PDF file content."""
        return b"Mock PDF content for testing"

    @pytest.fixture
    def mock_docx_content(self):
        """Mock DOCX file content."""
        return b"Mock DOCX content for testing"

    def test_extract_text_from_pdf(self, mock_pdf_content):
        """Test PDF text extraction."""
        with patch('web_app.backend.services.cv_processing.pdfplumber.open') as mock_pdf_plumber:
            mock_page = Mock()
            mock_page.extract_text.return_value = "Sample CV text from PDF"
            mock_pdf = Mock()
            mock_pdf.pages = [mock_page]
            mock_pdf.__enter__ = Mock(return_value=mock_pdf)
            mock_pdf.__exit__ = Mock(return_value=None)
            mock_pdf_plumber.return_value = mock_pdf
            
            from web_app.backend.services.cv_processing import extract_text_from_pdf
            
            result = extract_text_from_pdf(io.BytesIO(mock_pdf_content))
            assert result == "Sample CV text from PDF"
            mock_pdf_plumber.assert_called_once()

    def test_extract_text_from_docx(self, mock_docx_content):
        """Test DOCX text extraction."""
        with patch('web_app.backend.services.cv_processing.Document') as mock_doc:
            mock_paragraph = Mock()
            mock_paragraph.text = "Sample CV text from DOCX"
            mock_doc.return_value.paragraphs = [mock_paragraph]
            
            from web_app.backend.services.cv_processing import extract_text_from_docx
            
            result = extract_text_from_docx(io.BytesIO(mock_docx_content))
            assert result == "Sample CV text from DOCX"
            mock_doc.assert_called_once()

    def test_process_cv_for_matching(self, sample_cv_content):
        """Test CV processing for matching."""
        # Mock the extract_text_from_cv function that process_cv_for_matching uses
        with patch('web_app.backend.services.cv_processing.extract_text_from_cv') as mock_extract:
            mock_extract.return_value = "Extracted CV text"
            
            from web_app.backend.services.cv_processing import process_cv_for_matching
            
            # This function returns processed text, not a dict
            result = process_cv_for_matching(b"sample content", "test.pdf")
            assert isinstance(result, str)
            assert len(result) > 0

    def test_extract_text_from_cv(self, mock_pdf_content):
        """Test CV text extraction from file."""
        with patch('web_app.backend.services.cv_processing.extract_text_from_pdf') as mock_extract_pdf:
            mock_extract_pdf.return_value = "Extracted CV text"
            
            from web_app.backend.services.cv_processing import extract_text_from_cv
            
            result = extract_text_from_cv(mock_pdf_content, "test.pdf")
            assert result == "Extracted CV text"
            mock_extract_pdf.assert_called_once()

    def test_clean_cv_text(self):
        """Test CV text cleaning."""
        from web_app.backend.services.cv_processing import clean_cv_text
        
        dirty_text = "  Some text with    extra   spaces  \n\n\n  "
        clean_text = clean_cv_text(dirty_text)
        
        assert isinstance(clean_text, str)
        assert len(clean_text) > 0