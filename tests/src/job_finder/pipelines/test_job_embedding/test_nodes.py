"""Tests for job embedding pipeline nodes."""
import pytest
import pandas as pd
from unittest.mock import patch
from src.job_finder.pipelines.job_embedding.nodes import (
    clean_job_text,
    optimize_job_text_for_embedding,
    preprocess_jobs_for_embedding,
    vectorize_preprocessed_jobs
)


class TestCleanJobText:
    """Test job text cleaning functionality."""

    def test_clean_job_text_basic(self):
        """Test basic text cleaning."""
        text = "We are looking for a Senior Python Developer with 5+ years experience"
        result = clean_job_text(text)
        
        # Should remove stopwords and normalize
        assert isinstance(result, str)
        assert len(result) > 0
        assert "python" in result.lower()
        assert "developer" in result.lower()
        # Common stopwords should be removed
        assert " are " not in result
        assert " for " not in result

    def test_clean_job_text_empty(self):
        """Test cleaning empty text."""
        assert clean_job_text("") == ""
        assert clean_job_text(None) == ""

    def test_clean_job_text_removes_urls_and_emails(self):
        """Test removal of URLs and emails."""
        text = "Contact us at jobs@company.com or visit https://company.com for more info"
        result = clean_job_text(text)
        
        assert "jobs@company.com" not in result
        assert "https://company.com" not in result
        assert "contact" in result

    def test_clean_job_text_removes_job_stopwords(self):
        """Test removal of job-specific stopwords."""
        text = "This is a job posting for a position in our company looking for candidates"
        result = clean_job_text(text)
        
        # Job stopwords should be removed
        assert "job" not in result
        assert "position" not in result
        assert "company" not in result
        assert "looking" not in result

    def test_clean_job_text_preserves_technical_terms(self):
        """Test that technical terms are preserved."""
        text = "Python Django PostgreSQL JavaScript React.js machine-learning"
        result = clean_job_text(text)
        
        assert "python" in result
        assert "django" in result
        assert "postgresql" in result
        assert "javascript" in result


class TestOptimizeJobTextForEmbedding:
    """Test job text optimization for embeddings."""

    def test_optimize_job_text_basic(self):
        """Test basic job text optimization."""
        job_data = {
            'name': 'Senior Python Developer',
            'company_name': 'TechCorp',
            'city': 'Paris',
            'description': 'We need a Python developer with Django experience',
            'skills': 'Python, Django, PostgreSQL'
        }
        
        result = optimize_job_text_for_embedding(job_data)
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert "python" in result.lower()
        assert "django" in result.lower()

    def test_optimize_job_text_with_missions_list(self):
        """Test optimization with key missions as list."""
        job_data = {
            'name': 'Data Scientist',
            'key_missions': ['Build ML models', 'Analyze data', 'Create dashboards']
        }
        
        result = optimize_job_text_for_embedding(job_data)
        
        assert "models" in result.lower()
        assert "analyze" in result.lower()
        assert "dashboards" in result.lower()

    def test_optimize_job_text_with_missions_string(self):
        """Test optimization with key missions as string."""
        job_data = {
            'name': 'Backend Developer',
            'key_missions': 'Develop APIs and microservices'
        }
        
        result = optimize_job_text_for_embedding(job_data)
        
        assert "develop" in result.lower()
        assert "apis" in result.lower()

    def test_optimize_job_text_empty_data(self):
        """Test optimization with empty job data."""
        job_data = {}
        result = optimize_job_text_for_embedding(job_data)
        
        assert isinstance(result, str)
        # Should handle empty data gracefully

    def test_optimize_job_text_with_nan_missions(self):
        """Test optimization with NaN missions."""
        job_data = {
            'name': 'Developer',
            'key_missions': float('nan')
        }
        
        result = optimize_job_text_for_embedding(job_data)
        
        assert "developer" in result.lower()
        # Should handle NaN gracefully


class TestPreprocessJobsForEmbedding:
    """Test job preprocessing for embeddings."""

    def test_preprocess_jobs_basic(self):
        """Test basic job preprocessing."""
        jobs_df = pd.DataFrame([
            {
                'reference': 'job1',
                'name': 'Python Developer',
                'company_name': 'TechCorp',
                'description': 'We need a Python developer'
            },
            {
                'reference': 'job2', 
                'name': 'Data Scientist',
                'company_name': 'DataCorp',
                'description': 'Looking for ML expert'
            }
        ])
        
        result = preprocess_jobs_for_embedding(jobs_df)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert 'embedding_text' in result.columns
        assert len(result['embedding_text'].iloc[0]) > 0
        assert len(result['embedding_text'].iloc[1]) > 0

    def test_preprocess_jobs_empty_dataframe(self):
        """Test preprocessing empty DataFrame."""
        jobs_df = pd.DataFrame()
        result = preprocess_jobs_for_embedding(jobs_df)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0

    def test_preprocess_jobs_preserves_original_columns(self):
        """Test that original columns are preserved."""
        jobs_df = pd.DataFrame([
            {
                'reference': 'job1',
                'name': 'Developer',
                'salary': 50000,
                'remote': True
            }
        ])
        
        result = preprocess_jobs_for_embedding(jobs_df)
        
        # All original columns should be preserved
        assert 'reference' in result.columns
        assert 'name' in result.columns
        assert 'salary' in result.columns
        assert 'remote' in result.columns
        # New column should be added
        assert 'embedding_text' in result.columns


class TestVectorizePreprocessedJobs:
    """Test job vectorization."""

    def test_vectorize_preprocessed_jobs(self):
        """Test basic job vectorization."""
        jobs_df = pd.DataFrame([
            {
                'reference': 'job1',
                'embedding_text': 'python developer django postgresql'
            },
            {
                'reference': 'job2',
                'embedding_text': 'data scientist machine learning python'
            }
        ])
        
        result = vectorize_preprocessed_jobs(jobs_df)
        
        # Should pass through the same DataFrame
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert 'reference' in result.columns
        assert 'embedding_text' in result.columns
        
        # Should be the same data
        pd.testing.assert_frame_equal(result, jobs_df)

    def test_vectorize_empty_dataframe(self):
        """Test vectorization with empty DataFrame."""
        jobs_df = pd.DataFrame()
        result = vectorize_preprocessed_jobs(jobs_df)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0