"""Project settings. There is no need to edit this file unless you want to change values
from the Kedro defaults. For further information, including these default values, see
https://docs.kedro.org/en/stable/kedro_project_setup/settings.html."""

import os
from kedro.config import OmegaConfigLoader  # noqa: E402
from kedro.framework.session import KedroSession
from kedro.framework.startup import bootstrap_project
from omegaconf.resolvers import oc


CONFIG_LOADER_ARGS = {
    "custom_resolvers": {
        "oc.env": oc.env,
    }
}

# Directory that holds configuration.
CONF_SOURCE = "conf"

# Class that manages how configuration is loaded.

CONFIG_LOADER_CLASS = OmegaConfigLoader

project_path = os.getcwd()
bootstrap_project(project_path)


def load_credentials():
    """Function to load credentials from env variables (for production) or
    from conf/local if we are in local."""
    return {
        "aws_credentials": {
            "key": os.environ["AWS_ACCESS_KEY_ID"],
            "secret": os.environ["AWS_SECRET_ACCESS_KEY"],
            "client_kwargs": {
                "region_name": os.environ["AWS_REGION"],
            },
        },
        "sender_email_password": os.environ["SENDER_EMAIL_PASSWORD"],
    }


credentials = load_credentials()
