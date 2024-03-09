import yaml

import MessagebirdUtil
import WebhookValidatorUtil
import Logging


# Define the interface for the strategy
class Strategy:
    def execute(self, webhook: dict):
        pass


# Concrete implementations of the strategy
class AuthorisationStrategy(Strategy):
    def execute(self, webhook: dict):
        # store authed payment in DB
        Logging.configureLogging().info("Executing AuthorisationStrategy")
        textMessageBody = str(webhook)
        MessagebirdUtil.sendTextMessage(textMessageBody)


class RecurringContractStrategy(Strategy):
    def execute(self, webhook: dict):
        # store recurring contract in DB
        Logging.configureLogging().info("Executing RecurringContractStrategy")


class ReportAvailableStrategy(Strategy):
    def execute(self, webhook: dict):
        # get report through SFTP
        Logging.configureLogging().info("Executing ReportAvailableStrategy")


STRATEGY_MAP = {"AUTHORISATION": AuthorisationStrategy(),
                "REPORT_AVAILABLE": ReportAvailableStrategy(),
                "RECURRING_CONTRACT": RecurringContractStrategy()}


def processWebhook(webhook: dict) -> None:
    strategy = STRATEGY_MAP[WebhookValidatorUtil.getWebhookEventCode(webhook)]
    strategy.execute(webhook)


# Example usage
if __name__ == "__main__":

    with open('resource/example_webhook.json', 'r') as webhookFile:
        webhook = yaml.safe_load(webhookFile)

    processWebhook(dict(webhook))
