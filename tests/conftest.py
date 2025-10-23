"""Global test configuration and fixtures for the job_finder project."""
import os
import sys
from pathlib import Path
import pandas as pd
import pytest


# Add project root to Python path to enable imports
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
web_app_path = project_root / "web_app"

if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))
if str(web_app_path) not in sys.path:
    sys.path.insert(0, str(web_app_path))
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


@pytest.fixture(scope="session")
def test_env_vars():
    """Set up test environment variables."""
    test_vars = {
        "CHROMA_HOST": "localhost",
        "CHROMA_PORT": "8000",
        "CHROMA_USE_SSL": "false",
        "REDIS_HOST": "localhost",
        "REDIS_PORT": "6379",
        "AZURE_STORAGE_CONNECTION_STRING": "DefaultEndpointsProtocol=https;AccountName=test;AccountKey=test",
        "AZURE_CONTAINER_NAME": "test-container",
    }
    
    # Store original values to restore later
    original_values = {}
    for key, value in test_vars.items():
        original_values[key] = os.environ.get(key)
        os.environ[key] = value
    
    yield test_vars
    
    # Restore original values
    for key, original_value in original_values.items():
        if original_value is not None:
            os.environ[key] = original_value
        else:
            os.environ.pop(key, None)


@pytest.fixture
def mock_feedback():
    """
    Fixture that returns a mock dictionary of user feedback on job offers.

    Returns:
        dict: A mapping of job references to user feedback ("like" or "dislike").
    """
    return {"job_1": "like", "job_2": "dislike", "job_3": "like"}


@pytest.fixture
def mock_jobs():
    """
    Fixture that returns a mock DataFrame representing job offers.

    Returns:
        pd.DataFrame: A DataFrame with job references, titles, companies, and publication dates.
    """
    return pd.DataFrame(
        {
            "reference": ["job_1", "job_2", "job_3", "job_4"],
            "name": [
                "Data Scientist",
                "ML Engineer",
                "Data Analyst",
                "Backend Developer",
            ],
            "company_name": ["A", "B", "C", "D"],
            "publication_date": pd.to_datetime(["2025-06-01"] * 4),
        }
    )


@pytest.fixture
def sample_cv_content():
    """Sample CV content for testing CV processing."""
    return """
    John Doe
    Data Scientist
    
    Experience:
    - 3 years as Data Scientist at TechCorp
    - Machine Learning, Python, SQL
    - Built recommendation systems
    
    Skills: Python, Machine Learning, SQL, Docker, AWS
    """


@pytest.fixture
def sample_job_description():
    """Sample job description for testing matching algorithms."""
    return {
        "title": "Senior Data Scientist",
        "company": "TechStartup",
        "description": "We are looking for a Senior Data Scientist with experience in machine learning, Python programming, and cloud platforms like AWS.",
        "requirements": ["Python", "Machine Learning", "SQL", "AWS"],
        "location": "Paris, France"
    }