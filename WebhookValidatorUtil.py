import base64
import hmac
import hashlib
import binascii
import yaml
import json
from flask import jsonify

import Logging

# Load configuration from the YAML file
with open('config.yaml', 'r') as config_file:
    config = yaml.safe_load(config_file)

HMAC_SECRET_KEY = config['hmac_secret_key'].encode()

PAYLOAD_KEYS = [
    'pspReference',
    'originalReference',
    'merchantAccountCode',
    'merchantReference',
    'value',
    'currency',
    'eventCode',
    'success',
]

EVENT_CODES = ["AUTHORISATION", "REPORT_AVAILABLE", "RECURRING_CONTRACT"]


def getValidEventCodes() -> list:
    return EVENT_CODES.copy()


def validateWebhook(webhook: dict) -> None:
    validateWebhookEventCodeOrException(getWebhookEventCode(webhook))
    validHmacSignatureOrException(webhook)


def validateWebhookEventCodeOrException(eventCode: str) -> str:
    if eventCode in getValidEventCodes():
        return True
    raise ValueError(f"eventCode {eventCode} is not recognised!")


def getWebhookEventCode(webhook: dict) -> str:
    return webhook['notificationItems'][0]['NotificationRequestItem']['eventCode']


def getWebhookPspReference(webhook: dict) -> str:
    return webhook['notificationItems'][0]['NotificationRequestItem']['pspReference']


def convertWebhookToDict(webhook: str) -> dict:
    return dict(json.loads(webhook))


def computeExpectedNotificationSignature(notificationItem: dict, hmac_key: str) -> str:

    if not isinstance(notificationItem, dict):
        raise ValueError("Must Provide dictionary object")

    hmac_key = binascii.a2b_hex(hmac_key)

    request_dict = dict(notificationItem)
    request_dict['value'] = request_dict['amount']['value']
    request_dict['currency'] = request_dict['amount']['currency']

    signing_string = ':'.join(
        map(str, (request_dict.get(element, '') for element in PAYLOAD_KEYS)))

    hm = hmac.new(hmac_key, signing_string.encode('utf-8'), hashlib.sha256)
    return base64.b64encode(hm.digest()).decode("utf-8")


def validHmacSignatureOrException(webhookData: dict) -> None:

    if ('notificationItems' not in webhookData):
        raise ValueError("notificationItems key not inside webhook!")

    if len(webhookData['notificationItems']) > 1:
        raise ValueError("too many elements inside notificationItems array!")

    notificationItem = webhookData['notificationItems'][0]['NotificationRequestItem']

    if 'additionalData' not in notificationItem:
        raise ValueError(
            "additionalData key not inside notificationItem! Cannot verify HMAC signature")

    if "hmacSignature" not in notificationItem['additionalData']:
        raise ValueError("No hmacSignature provided in additionalData")

    receivedSignature = notificationItem['additionalData']['hmacSignature']
    expectedSignature = computeExpectedNotificationSignature(
        notificationItem, HMAC_SECRET_KEY)

    if not (hmac.compare_digest(expectedSignature, receivedSignature)):
        raise ValueError("HMAC verification failed for incoming webhook")


if __name__ == "__main__":

    with open('resource/example_webhook.json', 'r') as webhookFile:
        webhook = yaml.safe_load(webhookFile)

    validateWebhook(webhook)
