"""Project settings. There is no need to edit this file unless you want to change values
from the Kedro defaults. For further information, including these default values, see
https://docs.kedro.org/en/stable/kedro_project_setup/settings.html."""

import os
from kedro.config import OmegaConfigLoader  # noqa: E402
from kedro.framework.session import KedroSession
from kedro.framework.startup import bootstrap_project


# Directory that holds configuration.
CONF_SOURCE = "conf"

# Class that manages how configuration is loaded.

CONFIG_LOADER_CLASS = OmegaConfigLoader

project_path = os.getcwd()
bootstrap_project(project_path)

# Open a Kedro session
with KedroSession.create(project_path) as session:
    context = session.load_context()

config_loader: CONFIG_LOADER_CLASS = context.config_loader
credentials = config_loader.get("credentials")

# Keyword arguments to pass to the `CONFIG_LOADER_CLASS` constructor.

# Class that manages Kedro's library components.
# from kedro.framework.context import KedroContext
# CONTEXT_CLASS = KedroContext

# Class that manages the Data Catalog.
# from kedro.io import DataCatalog
# DATA_CATALOG_CLASS = DataCatalog
