"""CV matching service using embeddings and ChromaDB."""

import logging
from typing import List, Dict, Tuple, Optional

import chromadb
import numpy as np
from sentence_transformers import SentenceTransformer

from .cv_processing import process_cv_for_matching
from .azure_storage import get_offers

logger = logging.getLogger(__name__)

# Use the same model as for jobs to ensure compatibility
MODEL_NAME = "intfloat/multilingual-e5-small"


class CVMatcher:
    """CV matching service using embeddings and ChromaDB."""
    
    def __init__(self, chroma_db_path: str = "../../data/chroma"):
        """Initialize CV matcher with ChromaDB connection.
        
        Args:
            chroma_db_path: Path to ChromaDB database
        """
        self.chroma_db_path = chroma_db_path
        self.model = None
        self.chroma_client = None
        self.collection = None
        
    def _initialize_model(self):
        """Lazy load the sentence transformer model."""
        if self.model is None:
            logger.info(f"Loading sentence transformer model: {MODEL_NAME}")
            self.model = SentenceTransformer(MODEL_NAME)
            
    def _initialize_chroma(self):
        """Lazy load ChromaDB connection."""
        if self.chroma_client is None:
            logger.info(f"Connecting to ChromaDB at {self.chroma_db_path}")
            self.chroma_client = chromadb.PersistentClient(path=self.chroma_db_path)
            
            # Get the jobs collection (should already exist from job scraping)
            try:
                self.collection = self.chroma_client.get_collection(name="jobs")
                logger.info(f"Connected to jobs collection with {self.collection.count()} jobs")
            except Exception as e:
                logger.error(f"Could not connect to jobs collection: {e}")
                raise
    
    def create_cv_embedding(self, cv_text: str) -> np.ndarray:
        """Create embedding for CV text.
        
        Args:
            cv_text: Cleaned CV text
            
        Returns:
            np.ndarray: CV embedding vector
        """
        self._initialize_model()  # Initialize model if not done yet
        
        logger.info(f"Creating embedding for CV text: '{cv_text[:50]}...'")
        
        # Use the same model as job embeddings for consistency
        embedding = self.model.encode(cv_text)
        
        logger.info(f"CV embedding shape: {embedding.shape}")
        
        return embedding
    
    def find_matching_jobs(
        self, 
        cv_text: str, 
        top_k: int = 20,
        min_score: float = 0.0
    ) -> List[Dict]:
        """Find jobs that match the CV using semantic similarity.
        
        Args:
            cv_text: Cleaned CV text
            top_k: Number of top matches to return
            min_score: Minimum similarity score threshold
            
        Returns:
            List[Dict]: List of matching jobs with scores and complete data
        """
        self._initialize_chroma()
        
        # Create CV embedding
        cv_embedding = self.create_cv_embedding(cv_text)
        
        # Query ChromaDB for similar jobs
        logger.info(f"Searching for top {top_k} matching jobs...")
        logger.info(f"CV text: '{cv_text[:100]}...' (length: {len(cv_text)})")
        
        results = self.collection.query(
            query_embeddings=[cv_embedding.tolist()],
            n_results=top_k,
            include=['metadatas', 'distances', 'documents']
        )
        
        logger.info(f"ChromaDB query results: {len(results.get('metadatas', []))} metadata sets")
        if results.get('distances'):
            logger.info(f"Distance range: {min(results['distances'][0]) if results['distances'][0] else 'N/A'} - {max(results['distances'][0]) if results['distances'][0] else 'N/A'}")
        
        # Load complete job data for cross-referencing
        try:
            complete_jobs = get_offers()  # Récupère toutes les données complètes
            jobs_dict = {job.get('reference', ''): job for job in complete_jobs}
            logger.info(f"Loaded {len(complete_jobs)} complete job records for cross-referencing")
        except Exception as e:
            logger.warning(f"Could not load complete job data: {e}")
            jobs_dict = {}
        
        # Process results
        matches = []
        
        if results['metadatas'] and results['metadatas'][0]:
            for i, (metadata, distance, document) in enumerate(zip(
                results['metadatas'][0],
                results['distances'][0], 
                results['documents'][0]
            )):
                # Calculate score based on distance with your logic
                if distance < 0.9:
                    score = 1 - distance
                else:
                    score = 0.1
                
                # Apply minimum score filter
                if score >= min_score:
                    job_ref = metadata.get('reference', f'job_{i}')
                    
                    # Get complete job data if available
                    complete_job = jobs_dict.get(job_ref, {})
                    
                    match = {
                        # Core matching data
                        'job_reference': job_ref,
                        'similarity_score': score,
                        'match_percentage': round(score * 100, 1),
                        'match_score': round(score * 100, 1),  # For template compatibility
                        'rank': i + 1,
                        'distance': round(distance, 4),  # Keep original distance for debugging
                        
                        # Basic info (fallback to ChromaDB metadata if complete data missing)
                        # Using template-compatible names
                        'name': complete_job.get('name') or metadata.get('name', 'Unknown Title'),
                        'job_title': complete_job.get('name') or metadata.get('name', 'Unknown Title'),  # Alias
                        'company_name': complete_job.get('company_name') or metadata.get('company_name', 'Unknown Company'),
                        'city': complete_job.get('city') or metadata.get('city', 'Unknown City'),
                        'remote': complete_job.get('remote') or metadata.get('remote', 'Unknown'),
                        
                        # Enhanced data from complete job record
                        # Using template-compatible names
                        'logo_url': complete_job.get('logo_url'),
                        'company_logo': complete_job.get('logo_url'),  # Alias
                        'url': complete_job.get('url'),
                        'job_url': complete_job.get('url'),  # Alias
                        'contract_type': complete_job.get('contract_type'),
                        'publication_date': complete_job.get('publication_date'),
                        'relevance_score': round(score * 100, 1),  # For template compatibility
                        
                        'job_description': document[:200] + "..." if len(document) > 200 else document,
                        'description_preview': document[:200] + "..." if len(document) > 200 else document,  # For template compatibility
                    }
                    matches.append(match)
        
        logger.info(f"Found {len(matches)} jobs matching CV (min score: {min_score})")
        
        return matches
    
    def explain_match(
        self, 
        cv_text: str, 
        job_reference: str,
        top_n_words: int = 10
    ) -> Dict:
        """Explain why a CV matches a specific job using perturbation analysis.
        
        This method performs feature importance analysis by removing each word
        from the CV text and measuring the impact on similarity score.
        
        Args:
            cv_text: The CV text to analyze
            job_reference: Reference ID of the job to explain match for
            top_n_words: Number of most important words to return
            
        Returns:
            Dict: Explanation with word importance scores and details
        """
        self._initialize_chroma()
        
        # Get the specific job
        job_results = self.collection.get(
            where={"reference": job_reference},
            include=['embeddings', 'documents', 'metadatas']
        )
        
        if not job_results['ids']:
            raise ValueError(f"Job with reference {job_reference} not found")
        
        job_embedding = job_results['embeddings'][0]
        job_document = job_results['documents'][0]
        job_metadata = job_results['metadatas'][0]
        
        # Calculate baseline similarity
        cv_embedding = self.create_cv_embedding(cv_text)
        baseline_distance = float(np.linalg.norm(cv_embedding - job_embedding))
        
        # Tokenize CV text (simple word splitting)
        words = cv_text.lower().split()
        words = [word.strip('.,!?;:"()[]{}') for word in words if len(word.strip('.,!?;:"()[]{}')) > 2]
        
        word_importance = []
        
        logger.info(f"Analyzing importance of {len(words)} words for job {job_reference}")
        
        # Perturbation analysis: remove each word and measure impact
        for i, word in enumerate(words):
            # Create modified CV text without this word
            modified_words = words.copy()
            modified_words.pop(i)
            modified_cv_text = ' '.join(modified_words)
            
            if not modified_cv_text.strip():
                continue
            
            # Calculate similarity without this word
            modified_embedding = self.create_cv_embedding(modified_cv_text)
            modified_distance = float(np.linalg.norm(modified_embedding - job_embedding))
            
            # Impact is the change in distance (higher distance = worse match)
            # Positive impact means the word helps matching (removing it makes distance higher)
            impact = modified_distance - baseline_distance
            
            word_importance.append({
                'word': word,
                'importance': impact,
                'baseline_distance': baseline_distance,
                'modified_distance': modified_distance
            })
        
        # Sort by importance (descending - most helpful words first)
        word_importance.sort(key=lambda x: x['importance'], reverse=True)
        
        # Calculate similarity scores for display
        baseline_score = max(0, 1 - (baseline_distance / 2))  # Normalize distance to 0-1 score
        
        return {
            'job_reference': job_reference,
            'job_title': job_metadata.get('name', 'Unknown Title'),
            'company_name': job_metadata.get('company_name', 'Unknown Company'),
            'baseline_similarity_score': round(baseline_score, 3),
            'baseline_distance': round(baseline_distance, 4),
            'cv_word_count': len(words),
            'top_positive_words': [
                {
                    'word': w['word'],
                    'importance_score': round(w['importance'], 4),
                    'explanation': f"Removing this word increases distance by {round(w['importance'], 4)}"
                }
                for w in word_importance[:top_n_words] if w['importance'] > 0
            ],
            'top_negative_words': [
                {
                    'word': w['word'],
                    'importance_score': round(abs(w['importance']), 4),
                    'explanation': f"Removing this word decreases distance by {round(abs(w['importance']), 4)}"
                }
                for w in sorted(word_importance, key=lambda x: x['importance'])[:5] if w['importance'] < 0
            ],
            'analysis_summary': {
                'total_words_analyzed': len(words),
                'helpful_words': len([w for w in word_importance if w['importance'] > 0]),
                'neutral_words': len([w for w in word_importance if abs(w['importance']) < 0.001]),
                'harmful_words': len([w for w in word_importance if w['importance'] < -0.001])
            }
        }
    
    def process_cv_file_and_match(
        self, 
        file_content: bytes, 
        filename: str,
        top_k: int = 20,
        min_score: float = 0.3
    ) -> Tuple[str, List[Dict]]:
        """Complete pipeline: process CV file and find matches.
        
        Args:
            file_content: CV file content
            filename: Original filename
            top_k: Number of matches to return
            min_score: Minimum similarity threshold
            
        Returns:
            Tuple[str, List[Dict]]: (extracted_text, matching_jobs)
        """
        # Process CV file
        cv_text = process_cv_for_matching(file_content, filename)
        
        if not cv_text:
            raise ValueError(f"Could not extract text from {filename}")
        
        # Find matching jobs
        matches = self.find_matching_jobs(cv_text, top_k, min_score)
        
        return cv_text, matches
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the jobs collection.
        
        Returns:
            Dict: Collection statistics
        """
        self._initialize_chroma()
        
        try:
            count = self.collection.count()
            return {
                'total_jobs': count,
                'collection_name': 'jobs',
                'status': 'connected'
            }
        except Exception as e:
            return {
                'total_jobs': 0,
                'collection_name': 'jobs',
                'status': f'error: {e}'
            }


# Global instance for reuse across requests
_cv_matcher_instance = None

def get_cv_matcher() -> CVMatcher:
    """Get a CV matcher instance (singleton pattern for efficiency)."""
    global _cv_matcher_instance
    if _cv_matcher_instance is None:
        _cv_matcher_instance = CVMatcher()
    return _cv_matcher_instance