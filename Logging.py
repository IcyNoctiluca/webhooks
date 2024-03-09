import logging
import os
import yaml
import google.cloud.logging

import DeploymentUtil

# Load configuration from the YAML file
with open('config.yaml', 'r') as config_file:
    config = yaml.safe_load(config_file)

LOG_FILE = config['log_file']


def configureLogging(level=logging.INFO):

    if DeploymentUtil.getIsGoogleAppEnvironment():
        google.cloud.logging.Client().setup_logging()
    else:
        # local env.
        logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')

    return logging.getLogger(__name__)
