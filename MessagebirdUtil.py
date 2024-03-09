import yaml
import messagebird
import os

import Logging
import DeploymentUtil

# Load configuration from the YAML file
with open('config.yaml', 'r') as config_file:
    config = yaml.safe_load(config_file)


MESSAGEBIRD_KEY = config['messagebird_key']
TEXT_RECIPIENTS = ['+31686446115']

messagebirdClient = messagebird.Client(MESSAGEBIRD_KEY)


def sendTextMessage(messageBody: str) -> None:

    if DeploymentUtil.getIsLocalEnvironment():
        # local dev env.
        Logging.configureLogging().info("Not sending in local env. Text message: %s",
                                        str(messageBody))
        return None

    Logging.configureLogging().info("Sending text message: %s", str(messageBody))

    try:
        msg = messagebirdClient.message_create(
            originator='TestMessage', recipients=TEXT_RECIPIENTS, body=messageBody)
        Logging.configureLogging().info('Message id received: %s' % msg.id)

    except messagebird.client.ErrorException as e:
        Logging.configureLogging().error(
            '\nAn error occured while requesting a Message object:\n')
        for error in e.errors:
            Logging.configureLogging().error('  code        : %d' % error.code)
            Logging.configureLogging().error('  description : %s' % error.description)
            Logging.configureLogging().error('  parameter   : %s\n' % error.parameter)


# Example usage
if __name__ == "__main__":
    sendTextMessage({})
