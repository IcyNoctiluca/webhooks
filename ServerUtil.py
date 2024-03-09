import yaml
from flask import jsonify

import Logging


# Load configuration from the YAML file
with open('config.yaml', 'r') as config_file:
    config = yaml.safe_load(config_file)

PORT = int(config['python_port'])  # Read the port from the config

ACCEPTED_MESSAGE_DICT = {"message": "[accepted]"}


def getServerPort() -> int:
    return PORT


def getTemplateResponseMessage() -> dict:
    return ACCEPTED_MESSAGE_DICT.copy()


def logAndSendResponseMessage(responseMessage: dict, responseCode: int) -> None:
    Logging.configureLogging().info("Sending response code: %s Response: %s",
                                    responseCode, str(responseMessage))
    return jsonify(responseMessage), responseCode
