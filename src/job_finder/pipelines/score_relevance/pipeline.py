from kedro.pipeline import Pipeline, node, pipeline
from .nodes import (
    load_and_merge_feedback,
    feature_engineering,
    train_rl_model,
    score_all_offers,
)


def create_pipeline() -> Pipeline:
    """Score relevance pipeline."""
    return pipeline(
        [
            node(
                load_and_merge_feedback,
                inputs=["job_likes", "wttj_jobs_output"],
                outputs="merged_data",
                name="node_1_load_and_merge_feedback",
            ),
            node(
                feature_engineering,
                inputs="merged_data",
                outputs="features_with_rewards",
                name="node_2_feature_engineering",
            ),
            node(
                train_rl_model,
                inputs=["features_with_rewards", "rl_model_old"],
                outputs="rl_model_new",
                name="node_3_train_rl_model",
            ),
            node(
                score_all_offers,
                inputs=["wttj_jobs_output", "rl_model_new"],
                outputs="scored_offers",
                name="node_4_score_all_offers",
            ),
        ]
    )
