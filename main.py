import os
from flask import Flask, request

import Logging
import WebhookValidatorUtil
import WebhookProcessorUtil
import ServerUtil

app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():

    responseCode = None
    webhookResponseBody = ServerUtil.getTemplateResponseMessage()

    webhookData = request.data.decode()
    Logging.configureLogging().info("Received webhook data: %s", webhookData)
    webhookAsDict = WebhookValidatorUtil.convertWebhookToDict(webhookData)

    try:
        WebhookValidatorUtil.validateWebhook(webhookAsDict)

        Logging.configureLogging().info("Correctly validated hmac signature")
        responseCode = 200
        WebhookProcessorUtil.processWebhook(webhookAsDict)

    except Exception as e:
        Logging.configureLogging().error("Error processing webhook: %s", str(e))
        responseCode = 400
        webhookResponseBody["error"] = str(e)

    finally:
        return ServerUtil.logAndSendResponseMessage(webhookResponseBody, responseCode)


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0',
            port=int(os.environ.get('PORT', ServerUtil.getServerPort())))
