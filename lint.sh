#! /bin/bash

# Usage:
# 1. bash lint.sh
# 2. bash lint.sh |grep -v pyc |grep -v __init__ |grep -v setup

# Following uses PyPi package flake8, run "pipx install flake8" to get it
echo "Running pycodestyle linting"
pycodestyle .
printf "\n\n\nRunning pyflakes linting\n"
pyflakes .

# Following uses PyPI package reuse, run "pipx install reuse" to get it
printf "\n\n\nRunning reuse linting\n"
reuse --root tryton/ lint
