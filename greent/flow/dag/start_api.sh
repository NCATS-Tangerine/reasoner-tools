#!/bin/bash

set -x

cd $APP_ROOT
export PYTHONPATH=$APP_ROOT

source $APP_ROOT/greent/flow/dag/setenv.sh
source $APP_ROOT/greent/flow/dag/conf.sh

python greent/flow/dag/api.py

exit 0
