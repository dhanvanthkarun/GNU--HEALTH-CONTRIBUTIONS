#! /bin/bash
echo "Running pycodestyle linting"
pycodestyle .
printf "\n\n\nRunning pyflakes linting\n"
pyflakes .
printf "\n\n\nRunning reuse linting\n"
reuse --root tryton/ lint
