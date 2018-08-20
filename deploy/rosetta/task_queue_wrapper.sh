#!/bin/bash

set -x

ROOT=/code/reasoner-tools
while true; do
#    su - rosetta -c "$ROOT/task_queue.sh"
    $ROOT/task_queue.sh
    sleep 10
done
