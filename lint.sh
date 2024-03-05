#! /bin/bash

# Following uses PyPi package flake8, run "pipx install flake8" to get it
echo "Running pycodestyle linting"
pycodestyle .
printf "\n\n\nRunning pyflakes linting\n"
pyflakes .

# Following uses PyPI package reuse, run "pipx install reuse" to get it
printf "\n\n\nRunning reuse linting\n"
reuse --root tryton/ lint
