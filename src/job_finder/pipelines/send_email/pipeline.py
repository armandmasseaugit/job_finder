from kedro.pipeline import Pipeline, node, pipeline
from .nodes import filter_new_jobs, send_email


def create_pipeline() -> Pipeline:
    return pipeline(
        [
            node(
                func=filter_new_jobs,
                inputs="wttj_jobs_output",
                outputs="new_jobs",
                name="filter_new_jobs_node",
            ),
            node(
                func=send_email,
                inputs=["new_jobs", "params:email_config"],
                outputs=None,
                name="send_email_node",
            ),
        ]
    )
