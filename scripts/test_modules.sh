#!/bin/bash

RED='\033[0;31m'
NC='\033[0m' # No Color

[[ ! -f fail.log ]] || rm fail.log
[[ ! -f fail_short.log ]] || rm fail_short.log

cd tryton

# todo: change for loop back to all modules
# for module in $(ls -d health*); do
for module in "health" "health_archives" "health_caldav"; do
  echo "Entering module $module"
  cd $module

  echo "Creating virtual environment"
  python3 -m venv --copies venv

  echo "Installing module"
  ./venv/bin/pip install -q --index-url https://pypi.org/simple/ --extra-index-url https://test.pypi.org/simple/ . || (exit_status=$? && echo -e "${RED}Install failed for ${module}${NC}")

  echo "Running trytond module test"
  (./venv/bin/python3 -m unittest discover -s trytond.modules.$module >> ../../fail.log 2>&1) || (exit_status=$? && echo -e "${RED}Trytond module test failed for ${module}${NC}")
  printf "\n$module trytond module test output\n" >> ../../fail_short.log
  tail -n 4 ../../fail.log | tee -a ../../fail_short.log

  echo "Asserting no outdated dependencies"
  [ `./venv/bin/pip list --outdated | grep -v 'trytond' | grep -v 'proteus' | grep -v 'pip' | grep -v 'setuptools' | wc -l` -eq 2 ] || (exit_status=$? && echo -e "${RED}Found outdated pip dependencies for ${module}${NC}")
  echo "Showing outdated dependencies"
  ./venv/bin/pip list --outdated | grep -v 'trytond' | grep -v 'proteus' | grep -v 'pip' | grep -v 'setuptools'

  printf "Removing virtual environment\n\n\n"
  rm -r ./venv/

  cd ..
done

# Don't exit 0 if we had errors
exit "${exit_status:-0}"
