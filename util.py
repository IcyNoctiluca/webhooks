import base64
import hmac
import hashlib
import binascii
import json
import logging
from flask import jsonify


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

ACCEPTED_MESSAGE_DICT = {"message": "[accepted]"}


def getTemplateResponseMessage():
    return ACCEPTED_MESSAGE_DICT.copy()


def convertWebhookToDict(webhook: str) -> dict:
    return dict(json.loads(webhook))


def logAndSendResponseMessage(responseMessage: dict, responseCode: int):
    logging.info("Sending response: %s", str(responseMessage))
    return jsonify(responseMessage), responseCode


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


def isValidHmacNotification(webhookData, hmac_key) -> bool:

    if ('notificationItems' not in webhookData):
        raise RuntimeError("notificationItems key not inside webhook!")

    if len(webhookData['notificationItems']) > 1:
        raise RuntimeError("too many elements inside notificationItems array!")

    notificationItem = webhookData['notificationItems'][0]['NotificationRequestItem']

    if 'additionalData' not in notificationItem:
        raise RuntimeError(
            "additionalData key not inside notificationItem! Cannot verify HMAC signature")

    if "hmacSignature" not in notificationItem['additionalData']:
        raise RuntimeError("No hmacSignature provided in additionalData")

    receivedSignature = notificationItem['additionalData']['hmacSignature']
    expectedSignature = computeExpectedNotificationSignature(
        notificationItem, hmac_key)
    return hmac.compare_digest(expectedSignature, receivedSignature)
