#!/bin/bash

set -x 

ROOT=/code/reasoner-tools
cd $ROOT

MODULE=greent/flow/dag
source ./setenv.sh
source $MODULE/conf.sh
$ROOT/$MODULE/start_task_queue.sh
