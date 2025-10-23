"""Job embedding pipeline definition."""

from kedro.pipeline import Pipeline, node, pipeline

from .nodes import preprocess_jobs_for_embedding, vectorize_preprocessed_jobs


def create_pipeline() -> Pipeline:
    """Create job embedding pipeline.

    This pipeline:
    1. Takes raw job data from WTTJ scraping
    2. Preprocesses text for optimal embedding (removes stopwords, optimizes for 512 token limit)
    3. Vectorizes and saves to ChromaDB
    """
    return pipeline(
        [
            node(
                func=preprocess_jobs_for_embedding,
                inputs="wttj_jobs_output",  # Output from WTTJ scraping pipeline
                outputs="jobs_preprocessed",
                name="node_1_preprocess_jobs_text",
            ),
            node(
                func=vectorize_preprocessed_jobs,
                inputs="jobs_preprocessed",
                outputs="jobs_vector_db",
                name="node_2_vectorize_jobs",
            ),
        ]
    )
