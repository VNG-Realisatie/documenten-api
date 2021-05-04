#!/bin/bash

set -ex

toplevel=$(git rev-parse --show-toplevel)

cd $toplevel

# Base deps
pip-compile \
    --no-emit-index-url \
    requirements/base.in

# Jenkins/tests deps
pip-compile \
    --no-emit-index-url \
    --output-file requirements/jenkins.txt \
    requirements/base.txt \
    requirements/testing.in \
    requirements/jenkins.in
