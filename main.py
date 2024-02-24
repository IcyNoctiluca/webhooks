import logging
import google.cloud.logging
import yaml
import os
from flask import Flask, request, jsonify
import util

app = Flask(__name__)

# Load configuration from the YAML file
with open('config.yaml', 'r') as config_file:
    config = yaml.safe_load(config_file)

SECRET_KEY = config['secret_key'].encode()
LOG_FILE = config['log_file']
PORT = int(config['python_port'])  # Read the port from the config

if os.getenv('GAE_ENV', '').startswith('standard'):
    # production in google app engine
    client = google.cloud.logging.Client().setup_logging()
else:
    # local env.
    logging.basicConfig(filename='webhook.log', level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')


@app.route('/webhook', methods=['POST'])
def webhook():

    responseCode = None
    webhookData = request.data.decode()
    logging.info("Received webhook data: %s", webhookData)
    webhookAsDict = util.convertWebhookToDict(webhookData)

    try:
        if util.isValidHmacNotification(webhookAsDict, SECRET_KEY):
            logging.info("Correctly validated hmac signature")

            responseCode = 200
            responseMessage = util.getTemplateResponseMessage()

            return util.logAndSendResponseMessage(responseMessage, responseCode)

        raise RuntimeError("HMAC verification failed for incoming webhook")
    except Exception as e:
        logging.error("Error processing webhook: %s", str(e))

        responseCode = 400
        responseMessage = util.getTemplateResponseMessage()
        responseMessage["error"] = str(e)

        return util.logAndSendResponseMessage(responseMessage, responseCode)


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0',
            port=int(os.environ.get('PORT', PORT)))
