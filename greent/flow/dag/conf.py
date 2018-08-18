import os

app_name = os.environ["APP_NAME"]
celery_app_package = os.environ["CELERY_APP_PACKAGE"]
celery_broker_url = os.environ["CELERY_BROKER_URL"]
celery_result_backend = os.environ["CELERY_RESULT_BACKEND"]
