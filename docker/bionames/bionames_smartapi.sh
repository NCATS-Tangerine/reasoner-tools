#!/bin/bash

set -x
set -e

# Configure the Python path.
export PYTHONPATH=$PWD/reasoner-tools

if [ "x$GIT_PULL" == "xtrue" ]; then
    echo pulling latest source.
    cd reasoner-tools
    git pull
    cd ..
fi

#Execute the smartAPI application.
echo Starting app: bionames
python $PWD/reasoner-tools/builder/api/naming.py \
       --port=5001 \
       #--data=$DATA_DIR

echo Exiting.
exit 0
