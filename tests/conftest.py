import pytest
import pandas as pd

@pytest.fixture
def mock_feedback():
    return {
        "job_1": "like",
        "job_2": "dislike",
        "job_3": "like"
    }

@pytest.fixture
def mock_jobs():
    return pd.DataFrame({
        "reference": ["job_1", "job_2", "job_3", "job_4"],
        "name": ["Data Scientist", "ML Engineer", "Data Analyst", "Backend Developer"],
        "company_name": ["A", "B", "C", "D"],
        "publication_date": pd.to_datetime(["2025-06-01"] * 4)
    })
