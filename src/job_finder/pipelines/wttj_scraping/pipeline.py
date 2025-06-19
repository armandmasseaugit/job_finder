from kedro.pipeline import Pipeline, node, pipeline

from .nodes import wttj_query_and_parsing, jobs_filtering, s3_uploading


def create_pipeline() -> Pipeline:
    "Welcome to the Jungle pipeline."
    return pipeline(
        [
            node(
                func=wttj_query_and_parsing,
                inputs=[
                    "params:wttj_params.headers_jobs",
                    "params:wttj_params.queries",
                    "params:wttj_params.number_of_pages_to_search_into",
                ],
                outputs="wttj_jobs",
                name="node_1_wttj_query_and_parsing",
            ),
            node(
                func=jobs_filtering,
                inputs=[
                    "wttj_jobs",
                    "params:wttj_params.queries",
                ],
                outputs="wttj_jobs_filtered",
                name="node_2_jobs_filtering",
            ),
            node(
                func=s3_uploading,
                inputs=[
                    "wttj_jobs_filtered",
                ],
                outputs=["wttj_jobs_output", "wttj_last_scrape"],
                name="node_3_js3_uploading",
            ),
        ]
    )
