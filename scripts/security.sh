#! /bin/bash

# Usage:
# 1. bash scripts/security.sh

# Commands equal package names on PyPI

cd ./tryton/

# Run pip-audit to check dependencies for known vulnerabilities
# Todo: Uncomment once modules are on PyPI
#for module in $(ls -d health*); do
#  echo "Running pip-audit on ${module}"
#  pip-audit $module || exit_status=$?
#done

# Bandit is a tool designed to find common security issues in Python code
printf "\n\n\nRunning bandit\n"
bandit -r . || exit_status=$?

# Don't exit 0 if we had errors
exit "${exit_status:-0}"
