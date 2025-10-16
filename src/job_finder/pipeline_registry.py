"""Project pipelines."""

from kedro.framework.project import find_pipelines
from kedro.pipeline import Pipeline

from job_finder.pipelines import wttj_scraping, job_embedding


def register_pipelines() -> dict[str, Pipeline]:
    """Register the project's pipelines.

    Returns:
        A mapping from pipeline names to ``Pipeline`` objects.
    """
    pipelines = find_pipelines()
    
    # Register individual pipelines
    pipelines["wttj_scraping"] = wttj_scraping.create_pipeline()
    pipelines["job_embedding"] = job_embedding.create_pipeline()
    
    # Default pipeline runs both in sequence
    pipelines["__default__"] = (
        pipelines["wttj_scraping"] + 
        pipelines["job_embedding"]
    )
    
    return pipelines
