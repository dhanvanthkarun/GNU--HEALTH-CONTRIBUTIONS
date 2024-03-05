#! /bin/bash
echo "Running pycodestyle linting"
pycodestyle .
printf "\n\n\nRunning flake8 linting\n"
flake8 .
# printf "\n\n\nRunning pylint linting\n"
# pylint .
printf "\n\n\nRunning reuse linting\n"
reuse --root tryton/ lint
