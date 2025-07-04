import os
import numpy as np
from kedro.framework.startup import bootstrap_project
from kedro.framework.session import KedroSession

bootstrap_project(os.getcwd())

def load_offers():
    with KedroSession.create(os.getcwd()) as session:
        context = session.load_context()
        df = context.catalog.load("wttj_jobs_output")
        df = df.replace({np.nan: None, np.inf: None, -np.inf: None})
        return df.to_dict(orient="records")