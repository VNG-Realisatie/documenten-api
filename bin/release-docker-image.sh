#!/bin/bash

set -e # exit on error
set -x # echo commands

CONTAINER_REPO=nlxio/gemma-drc

RELEASE_TAG=${RELEASE_TAG:-latest}

docker build \
    --target production \
    -t ${CONTAINER_REPO}:${RELEASE_TAG} \
    -f Dockerfile .


# JOB_NAME is set by Jenkins
# only push the image if running in CI
if [[ ! -z "$JOB_NAME" ]]; then
    docker push ${CONTAINER_REPO}:${RELEASE_TAG}
else
    echo "Not pushing image, set the JOB_NAME envvar to push after building"
fi
