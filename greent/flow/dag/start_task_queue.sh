#!/bin/bash

set -e
set -x

celery -A ${CELERY_APP_PACKAGE}.celery worker --loglevel=info -c $NUM_WORKERS
#-Q $APP_NAME

#-n $BROKER_CONNECT_ID@$BROKER_HOSTNAME 

