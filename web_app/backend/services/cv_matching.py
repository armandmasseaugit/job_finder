"""CV matching service using embeddings and ChromaDB."""

import logging
from typing import List, Dict, Tuple, Optional

import chromadb
import numpy as np
from sentence_transformers import SentenceTransformer

from .cv_processing import process_cv_for_matching

logger = logging.getLogger(__name__)

# Use the same model as for jobs to ensure compatibility
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"


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
            List[Dict]: List of matching jobs with scores
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
        
        # Process results
        matches = []
        
        if results['metadatas'] and results['metadatas'][0]:
            # Calculate rank-based scores (more reliable than distance conversion)
            total_results = len(results['metadatas'][0])
            
            for i, (metadata, distance, document) in enumerate(zip(
                results['metadatas'][0],
                results['distances'][0], 
                results['documents'][0]
            )):
                # Rank-based scoring: 1st result = 100%, last result = higher min_score
                # This ensures the best match always gets high score regardless of absolute distance
                rank_score = (total_results - i) / total_results
                
                # Scale to ensure minimum score is reasonable (at least 10% for last result)
                min_rank_score = 0.1
                scaled_score = min_rank_score + (rank_score * (1.0 - min_rank_score))
                
                if scaled_score >= min_score:
                    match = {
                        'job_reference': metadata.get('reference', f'job_{i}'),
                        'job_title': metadata.get('name', 'Unknown Title'),
                        'company_name': metadata.get('company_name', 'Unknown Company'),
                        'city': metadata.get('city', 'Unknown City'),
                        'similarity_score': scaled_score,
                        'match_percentage': round(scaled_score * 100, 1),
                        'job_description': document[:200] + "..." if len(document) > 200 else document,
                        'rank': i + 1,
                        'distance': round(distance, 4)  # Keep original distance for debugging
                    }
                    matches.append(match)
        
        logger.info(f"Found {len(matches)} jobs matching CV (min score: {min_score})")
        
        return matches
    
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