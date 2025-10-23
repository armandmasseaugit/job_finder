"""Nodes for job text preprocessing and embedding."""

import logging
import re
from typing import Dict, List, Set
import pandas as pd

try:
    import spacy
    from spacy.lang.fr.stop_words import STOP_WORDS as FR_STOP_WORDS
    from spacy.lang.en.stop_words import STOP_WORDS as EN_STOP_WORDS
    
    # Combine French and English stopwords
    STOPWORDS = FR_STOP_WORDS.union(EN_STOP_WORDS)
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    # Fallback minimal stopwords
    STOPWORDS = {
        'le', 'la', 'les', 'un', 'une', 'des', 'du', 'de', 'et', 'ou', 'mais',
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'
    }

logger = logging.getLogger(__name__)

# Job-specific stopwords to remove
JOB_STOPWORDS = {
    'poste', 'offre', 'emploi', 'job', 'position', 'role', 'opportunity', 'candidat',
    'candidate', 'recherche', 'recherchons', 'looking', 'seeking', 'team', 'équipe',
    'entreprise', 'company', 'société', 'startup', 'business', 'organization',
    'description', 'profil', 'profile', 'mission', 'missions', 'responsabilités',
    'responsibilities', 'tâches', 'tasks', 'activités', 'activities', 'skills', 'compétences',
    'qualifications', 'requirements', 'expérience', 'experience',
}

def clean_job_text(text: str) -> str:
    """Clean job text by removing noise and stopwords.
    
    Args:
        text: Raw job text
        
    Returns:
        str: Cleaned text optimized for embedding
    """
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove URLs, emails, phone numbers
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', text)
    text = re.sub(r'(?:\+33|0)[1-9](?:[.\-\s]?\d{2}){4}', '', text)
    text = re.sub(r'(\+\d{1,3}\s?)?\(?\d{1,4}\)?[\s.-]?\d{1,4}[\s.-]?\d{1,9}', '', text)
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[●•▪▫◦‣⁃]', '', text)
    text = re.sub(r'[^\w\s\-\+\#\.]', ' ', text)
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Split into words and filter
    words = text.split()
    filtered_words = []
    
    for word in words:
        word_clean = word.strip('.-+#').lower()
        
        # Keep word if:
        # - Length > 2
        # - Not a stopword
        # - Not a number
        # - Not a single character
        if (len(word_clean) > 2 and 
            word_clean not in STOPWORDS and 
            word_clean not in JOB_STOPWORDS and
            not word_clean.isdigit() and
            not re.match(r'^[a-z]$', word_clean)):
            filtered_words.append(word_clean)
    
    # Remove consecutive duplicates while preserving order
    final_words = []
    prev_word = None
    for word in filtered_words:
        if word != prev_word:
            final_words.append(word)
            prev_word = word
    
    return ' '.join(final_words)

def optimize_job_text_for_embedding(job_data: Dict) -> str:
    """Optimize job text for embedding by combining relevant fields.
    
    Args:
        job_data: Dictionary containing job information
        
    Returns:
        str: Optimized text ready for embedding
    """
    # Combine all relevant fields
    text_parts = []
    
    # Essential info
    if job_data.get('name'):
        text_parts.append(job_data['name'])
    if job_data.get('company_name'):
        text_parts.append(job_data['company_name'])
    if job_data.get('city'):
        text_parts.append(job_data['city'])
    if job_data.get('country'):
        text_parts.append(job_data['country'])

    # Skills and technologies
    if job_data.get('skills'):
        text_parts.append(job_data['skills'])
    
    # Profile
    if job_data.get('profile'):
        text_parts.append(job_data['profile'])
        
    # Summary
    if job_data.get('description'):
        text_parts.append(job_data['description'])

    # Key missions
    key_missions = job_data.get('key_missions')
    if key_missions is not None and str(key_missions) != 'nan':
        if isinstance(key_missions, list):
            text_parts.extend(key_missions)
        else:
            text_parts.append(str(key_missions))

    # Join all parts
    raw_text = ' '.join(str(part) for part in text_parts if part)
    
    # Clean the text (remove stopwords, etc.)
    cleaned_text = clean_job_text(raw_text)
    
    return cleaned_text

def preprocess_jobs_for_embedding(jobs_data: pd.DataFrame) -> pd.DataFrame:
    """Preprocess jobs data for embedding.
    
    Args:
        jobs_data: DataFrame containing raw job data
        
    Returns:
        pd.DataFrame: DataFrame with added 'embedding_text' column
    """
    logger.info(f"Preprocessing {len(jobs_data)} jobs for embedding...")
    
    # Create optimized text for each job
    embedding_texts = []
    
    for idx, job_row in jobs_data.iterrows():
        job_dict = job_row.to_dict()
        optimized_text = optimize_job_text_for_embedding(job_dict)
        embedding_texts.append(optimized_text)

        if idx % 100 == 0:  # Log progress every 100 jobs
            logger.info(f"Processed {idx + 1}/{len(jobs_data)} jobs")
                # Log to see what we get
            logger.info(f"Cleaned text sample: '{optimized_text[:2000]}...'")
    
    # Add the optimized text as a new column
    result_df = jobs_data.copy()
    result_df['embedding_text'] = embedding_texts

    # Log statistics
    if len(embedding_texts) > 0:
        avg_length = sum(len(text.split()) for text in embedding_texts) / len(embedding_texts)
        logger.info(f"Preprocessing complete. Average text length: {avg_length:.1f} words")
        
        # Show example
        logger.info(f"Example optimized text: '{embedding_texts[0][:100]}...'")
    else:
        logger.info("Preprocessing complete. No jobs to process.")

    return result_df


def vectorize_preprocessed_jobs(preprocessed_jobs: pd.DataFrame) -> pd.DataFrame:
    """Vectorize preprocessed jobs and save to ChromaDB.
    
    Args:
        preprocessed_jobs: DataFrame with 'embedding_text' column
        
    Returns:
        pd.DataFrame: Same DataFrame (pass-through for pipeline)
    """
    logger.info(f"Vectorizing {len(preprocessed_jobs)} preprocessed jobs...")
    
    # This function will use the existing ChromaDB dataset
    # The actual vectorization happens in the dataset's save method
    # We just pass through the data
    
    return preprocessed_jobs