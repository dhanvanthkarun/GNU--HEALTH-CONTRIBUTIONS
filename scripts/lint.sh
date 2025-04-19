#! /bin/bash

# Usage:
# 1. bash scripts/lint.sh
# 2. bash scripts/lint.sh |grep -v pyc |grep -v __init__ |grep -v setup

# Following uses PyPi package flake8, run "pipx install flake8" to get it
echo "Running pycodestyle linting"
pycodestyle .  || exit_status=$?
printf "\n\n\nRunning pyflakes linting\n"
pyflakes .  || exit_status=$?

# Following uses PyPI package reuse, run "pipx install reuse" to get it
printf "\n\n\nRunning reuse linting\n"
reuse --root tryton/ lint  || exit_status=$?

printf "\n\n\nRunning fodt direct formatting test ...\n\n"
find "." -type f -name "*.fodt" -print0 | while IFS= read -r -d '' file; do
    if [[ ! "$file" == *"default_gnuhealth_report_template"* ]] && grep -q "text:span text:style-name=" "$file"; then
        echo "WARN: Direct formatting found, it MAYBE impact translation ..."
        echo ""
        echo "1. Open $file"
        echo "2. Click: Edit -> Select ALL"
        echo "3. Click: Format -> Clean Direct Formatting"
        echo "4. Save file."
        echo ""
        echo "More info: https://docs.gnuhealth.org/his/techguide/development/reports.html"
        echo ""
        exist_status=1
    fi
done

# Don't exit 0 if we had errors
exit "${exit_status:-0}"
