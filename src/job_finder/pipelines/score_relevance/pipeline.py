from kedro.pipeline import Pipeline, node, pipeline
from .nodes import *

def create_pipeline(**kwargs) -> Pipeline:
    return pipeline([
        node(load_and_merge_feedback, inputs=["likes_dislikes", "wttj_jobs_output"], outputs="merged_data", name="merge_feedback"),
        node(feature_engineering, inputs="merged_data", outputs="features_with_rewards", name="feature_engineering"),
        node(train_rl_model, inputs=["features_with_rewards", "rl_model_old"], outputs="rl_model_new", name="train_model"),
        node(score_all_offers, inputs=["wttj_jobs_output", "rl_model_new"], outputs="scored_offers", name="score_offers"),
    ])