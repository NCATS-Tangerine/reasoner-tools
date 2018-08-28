#!/bin/bash

set -x

script_bin=$(dirname ${BASH_SOURCE[0]})

export PYTHONPATH=$script_bin/../../../

source $script_bin/setenv.sh
source $script_bin/conf.sh

python $script_bin/api.py

exit 0
