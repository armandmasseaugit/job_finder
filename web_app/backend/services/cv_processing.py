"""CV processing utilities for text extraction."""

import io
import logging
from pathlib import Path
from typing import Union, BinaryIO

import PyPDF2
import pdfplumber
from docx import Document

logger = logging.getLogger(__name__)


def extract_text_from_pdf(file_content: Union[BinaryIO, bytes]) -> str:
    """Extract text from PDF file using pdfplumber (more reliable than PyPDF2).
    
    Args:
        file_content: PDF file content as bytes or file-like object
        
    Returns:
        str: Extracted text from the PDF
    """
    try:
        # Ensure we have a file-like object
        if isinstance(file_content, bytes):
            file_content = io.BytesIO(file_content)
        
        text_parts = []
        
        with pdfplumber.open(file_content) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
        
        extracted_text = "\n".join(text_parts)
        
        # Fallback to PyPDF2 if pdfplumber fails
        if not extracted_text.strip():
            logger.warning("pdfplumber extracted empty text, trying PyPDF2...")
            file_content.seek(0)  # Reset file pointer
            extracted_text = _extract_with_pypdf2(file_content)
            
        return extracted_text.strip()
        
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        return ""


def _extract_with_pypdf2(file_content: BinaryIO) -> str:
    """Fallback PDF extraction using PyPDF2."""
    try:
        pdf_reader = PyPDF2.PdfReader(file_content)
        text_parts = []
        
        for page in pdf_reader.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)
                
        return "\n".join(text_parts)
    except Exception as e:
        logger.error(f"PyPDF2 extraction failed: {e}")
        return ""


def extract_text_from_docx(file_content: Union[BinaryIO, bytes]) -> str:
    """Extract text from DOCX file.
    
    Args:
        file_content: DOCX file content as bytes or file-like object
        
    Returns:
        str: Extracted text from the DOCX
    """
    try:
        # Ensure we have a file-like object
        if isinstance(file_content, bytes):
            file_content = io.BytesIO(file_content)
            
        doc = Document(file_content)
        text_parts = []
        
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text_parts.append(paragraph.text)
                
        return "\n".join(text_parts)
        
    except Exception as e:
        logger.error(f"Error extracting text from DOCX: {e}")
        return ""


def extract_text_from_cv(file_content: bytes, filename: str) -> str:
    """Extract text from CV file based on file extension.
    
    Args:
        file_content: File content as bytes
        filename: Original filename to determine file type
        
    Returns:
        str: Extracted text from the CV
    """
    file_extension = Path(filename).suffix.lower()
    
    logger.info(f"Extracting text from {filename} ({file_extension})")
    
    if file_extension == '.pdf':
        return extract_text_from_pdf(file_content)
    elif file_extension in ['.docx', '.doc']:
        return extract_text_from_docx(file_content)
    elif file_extension == '.txt':
        try:
            return file_content.decode('utf-8')
        except UnicodeDecodeError:
            try:
                return file_content.decode('latin-1')
            except UnicodeDecodeError:
                logger.error("Unable to decode text file")
                return ""
    else:
        logger.error(f"Unsupported file type: {file_extension}")
        return ""


def clean_cv_text(text: str) -> str:
    """Clean and normalize CV text for better embedding quality.
    
    Args:
        text: Raw extracted text from CV
        
    Returns:
        str: Cleaned text ready for embedding
    """
    if not text:
        return ""
        
    # Remove excessive whitespace and newlines
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    # Join lines with single space
    cleaned_text = ' '.join(lines)
    
    # Remove multiple consecutive spaces
    while '  ' in cleaned_text:
        cleaned_text = cleaned_text.replace('  ', ' ')
    
    # Basic cleaning for common CV artifacts
    cleaned_text = cleaned_text.replace('●', '').replace('•', '')
    cleaned_text = cleaned_text.replace('\t', ' ')
    
    return cleaned_text.strip()


def process_cv_for_matching(file_content: bytes, filename: str) -> str:
    """Complete CV processing pipeline: extract + clean text.
    
    Args:
        file_content: CV file content as bytes
        filename: Original filename
        
    Returns:
        str: Cleaned text ready for embedding and matching
    """
    # Extract raw text
    raw_text = extract_text_from_cv(file_content, filename)
    
    if not raw_text:
        logger.error(f"No text extracted from {filename}")
        return ""
    
    # Clean the text
    cleaned_text = clean_cv_text(raw_text)
    
    logger.info(f"Successfully processed CV: {len(cleaned_text)} characters extracted")
    
    return cleaned_text