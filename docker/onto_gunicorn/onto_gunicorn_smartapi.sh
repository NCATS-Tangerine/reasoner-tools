#!/bin/bash

set -x
set -e

# Configure the Python path.
export PYTHONPATH=$PWD/reasoner-tools

if [ "x$GIT_PULL" == "xtrue" ]; then
    echo pulling latest source.
    cd reasoner-tools
    git pull
    cd greent/api
fi

cd /code/reasoner-tools/greent/api

gunicorn \
        --bind=0.0.0.0:$APP_PORT \
        --workers=$NUM_WORKERS \
        --pythonpath '../../' \
        --timeout=120 \
        onto_gunicorn:app

echo Exiting.
exit
