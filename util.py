import base64
import hmac
import hashlib
import binascii
import json
import logging
from flask import jsonify
import messagebird
import os


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
TEXT_RECIPIENTS = ['+31686446115']


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


def validHmacSignatureOrException(webhookData: dict, hmac_key: str):

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

    if not (hmac.compare_digest(expectedSignature, receivedSignature)):
        raise RuntimeError("HMAC verification failed for incoming webhook")


def sendTextMessage(messagebirdClient, messageBody: str):

    logging.info("Sending text message: %s", str(messageBody))

    try:
        if not (os.getenv('GAE_ENV', '').startswith('standard')):
            # local dev env.
            return None

        msg = messagebirdClient.message_create(
            originator='TestMessage', recipients=TEXT_RECIPIENTS, body=messageBody)
        logging.info('Message id received: %s' % msg.id)

    except messagebird.client.ErrorException as e:
        logging.info('\nAn error occured while requesting a Message object:\n')
        for error in e.errors:
            logging.error('  code        : %d' % error.code)
            logging.error('  description : %s' % error.description)
            logging.error('  parameter   : %s\n' % error.parameter)
