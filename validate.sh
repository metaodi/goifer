#!/bin/bash

set -e

function cleanup {
    exit $?
}

trap "cleanup" EXIT

# check with black
black . --diff

# Check PEP-8 code style and McCabe complexity
flake8 . --count --show-source --statistics

# run tests with test coverage
pytest --cov=goifer tests/
