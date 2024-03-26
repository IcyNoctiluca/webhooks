# Process webhooks from Adyen

## Deployment
Use `gcloud app browse` to push to Google App Engine
Use `gcloud app logs tail -s default` to check logs

## Docs
Link to Adyen's webhook Docs:
- https://docs.adyen.com/development-resources/webhooks/

## TODOs
- Implement notification processor strategies
- Implement webhook common util, and remove methods in validator
- Add more specific exceptions to main.py#webhook, to give more targeted response codes
- Convert webhook dict to webhook object (java bean equivalent) to allow for better webhook validation and processing