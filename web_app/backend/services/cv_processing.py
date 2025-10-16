"""CV processing utilities for text extraction."""

import io
import logging
import re
from pathlib import Path
from typing import Union, BinaryIO

import PyPDF2
import pdfplumber
from docx import Document
import spacy
from spacy.lang.fr.stop_words import STOP_WORDS as FR_STOP_WORDS
from spacy.lang.en.stop_words import STOP_WORDS as EN_STOP_WORDS

logger = logging.getLogger(__name__)

# Combine French and English stopwords from spaCy
STOPWORDS = FR_STOP_WORDS.union(EN_STOP_WORDS)

# Common CV section headers to remove
CV_HEADERS = {
    'curriculum', 'vitae', 'resume', 'cv', 'profil', 'profile', 'experience', 'expérience', 
    'formation', 'education', 'compétences', 'competences', 'skills', 'langues', 'languages',
    'centres', 'intérêts', 'interests', 'hobbies', 'loisirs', 'contact', 'coordonnées',
    'références', 'references', 'projets', 'projects', 'certifications', 'diplômes',
    'diplomes', 'degrees', 'objectif', 'objective', 'summary', 'résumé', 'about'
}


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
    
    This function removes:
    - Email addresses and phone numbers
    - URLs and social media handles
    - Common stopwords (French and English)
    - CV section headers
    - Personal information patterns
    - Special characters and formatting artifacts
    
    Args:
        text: Raw extracted text from CV
        
    Returns:
        str: Cleaned text ready for embedding, focused on technical skills and experience
    """
    if not text:
        return ""
    
    # Convert to lowercase for processing
    text_lower = text.lower()
    
    # Remove email addresses
    text_lower = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', text_lower)
    
    # Remove phone numbers (various formats)
    text_lower = re.sub(r'(?:\+33|0)[1-9](?:[.\-\s]?\d{2}){4}', '', text_lower)  # French phone
    text_lower = re.sub(r'(\+\d{1,3}\s?)?\(?\d{1,4}\)?[\s.-]?\d{1,4}[\s.-]?\d{1,9}', '', text_lower)  # International
    
    # Remove URLs
    text_lower = re.sub(r'https?://\S+|www\.\S+', '', text_lower)
    
    # Remove social media handles
    text_lower = re.sub(r'@\w+', '', text_lower)
    
    # Remove linkedin profile patterns
    text_lower = re.sub(r'linkedin\.com/in/\S+', '', text_lower)
    text_lower = re.sub(r'github\.com/\S+', '', text_lower)
    
    # Remove addresses (simple patterns)
    text_lower = re.sub(r'\d+\s+(?:rue|avenue|boulevard|street|ave|blvd)\s+\w+', '', text_lower)
    text_lower = re.sub(r'\d{5}\s+\w+', '', text_lower)  # Postal codes + city
    
    # Remove dates in various formats
    text_lower = re.sub(r'\b\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}\b', '', text_lower)
    text_lower = re.sub(r'\b(?:janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre|january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{4}\b', '', text_lower)
    
    # Remove excessive whitespace and newlines
    lines = [line.strip() for line in text_lower.split('\n') if line.strip()]
    cleaned_text = ' '.join(lines)
    
    # Remove special characters and formatting artifacts
    cleaned_text = re.sub(r'[●•▪▫◦‣⁃]', '', cleaned_text)
    cleaned_text = re.sub(r'[\t\r\n]+', ' ', cleaned_text)
    cleaned_text = re.sub(r'[^\w\s\-\+\#]', ' ', cleaned_text)  # Keep only alphanumeric, spaces, hyphens, plus, hash
    
    # Split into words for filtering
    words = cleaned_text.split()
    
    # Filter out stopwords, CV headers, and very short words
    filtered_words = []
    for word in words:
        word_clean = word.strip().lower()
        if (len(word_clean) > 2 and 
            word_clean not in STOPWORDS and 
            word_clean not in CV_HEADERS and
            not word_clean.isdigit() and  # Remove standalone numbers
            not re.match(r'^[a-z]$', word_clean)):  # Remove single letters
            filtered_words.append(word_clean)
    
    # Remove consecutive duplicates while preserving order
    final_words = []
    prev_word = None
    for word in filtered_words:
        if word != prev_word:
            final_words.append(word)
            prev_word = word
    
    # Join back and clean up spacing
    result = ' '.join(final_words)
    
    # Remove multiple consecutive spaces
    while '  ' in result:
        result = result.replace('  ', ' ')
    
    return result.strip()


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