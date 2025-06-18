import pandas as pd
from job_finder.pipelines.score_relevance.nodes import (
    load_and_merge_feedback,
    feature_engineering,
    train_rl_model,
    score_all_offers,
)


def test_load_and_merge_feedback(mock_feedback, mock_jobs):
    result = load_and_merge_feedback(mock_feedback, mock_jobs)
    assert isinstance(result, pd.DataFrame)
    assert "reward" in result.columns
    assert result.shape[0] == 3  # Only 3 feedbacks should match
    assert set(result["reward"].unique()) <= {1, -1}


def test_feature_engineering(mock_feedback, mock_jobs):
    merged = load_and_merge_feedback(mock_feedback, mock_jobs)
    features = feature_engineering(merged)
    assert isinstance(features, pd.DataFrame)
    assert "reward" in features.columns
    assert features.shape[0] == 3
    assert features.drop(columns=["reward"]).shape[1] > 0  # TF-IDF vector size


def test_train_rl_model(mock_feedback, mock_jobs):
    merged = load_and_merge_feedback(mock_feedback, mock_jobs)
    features = feature_engineering(merged)
    model = train_rl_model(features)
    assert hasattr(model, "predict_proba")


def test_score_all_offers(mock_feedback, mock_jobs):
    merged = load_and_merge_feedback(mock_feedback, mock_jobs)
    features = feature_engineering(merged)
    model = train_rl_model(features)
    scores = score_all_offers(mock_jobs, model)
    assert isinstance(scores, dict)
    assert all(ref in scores for ref in mock_jobs["reference"])
    assert all(isinstance(score, float) for score in scores.values())
