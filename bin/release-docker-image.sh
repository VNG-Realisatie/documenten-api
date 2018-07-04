#!/bin/bash

set -e # exit on error
set -x # echo commands

CONTAINER_REPO=nlxio/gemma-drc


git_tag=$(git tag --points-at HEAD) &>/dev/null


if [[ ! -z "$git_tag" ]]; then
    echo "Building image for git tag $git_tag"
    RELEASE_TAG=$git_tag
else
    RELEASE_TAG=${RELEASE_TAG:-latest}
fi


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
