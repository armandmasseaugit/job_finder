import pandas as pd
import pytest


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
