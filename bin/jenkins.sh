#!/bin/bash

set -e  # exit on errors
set -x  # echo commands

if [[ -z "$WORKSPACE" ]]; then
    export WORKSPACE=$(pwd)
fi

docker-compose -p drc_tests -f ./docker-compose.yml build --no-cache tests
docker-compose -p drc_tests -f ./docker-compose.yml run tests
