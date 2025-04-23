#! /bin/bash

# Usage:
# 1. bash scripts/lint.sh
# 2. bash scripts/lint.sh |grep -v pyc |grep -v __init__ |grep -v setup

SOURCE_DIR=$(dirname "$(realpath "${BASH_SOURCE[0]}")")
cd $SOURCE_DIR/..

# Following uses PyPi package flake8, run "pipx install flake8" to get it
echo "Running pycodestyle linting"
pycodestyle .  || exit_status=$?
printf "\n\n\nRunning pyflakes linting\n"
pyflakes .  || exit_status=$?

# Following uses PyPI package reuse, run "pipx install reuse" to get it
printf "\n\n\nRunning reuse linting\n"
reuse --root tryton/ lint  || exit_status=$?

printf "\n\n\nRunning fodt direct formatting test ...\n\n"
find $PWD -type f -name "*.fodt" -print0 | while IFS= read -r -d '' file; do
    if [[ ! "$file" == *"default_gnuhealth_report_template"* ]]; then
       if grep -q "text:span text:style-name=" "$file" || \
               grep -q "  <text:s/>" "$file" || \
               grep -q "text:span><text:span" "$file" ; then
           echo "* WARN: Direct formatting found, it MAYBE impact translation ..."
           echo ""
           echo "  1. xdg-open $file"
           echo "  2. Click: Edit -> Select ALL"
           echo "  3. Click: Format -> Clean Direct Formatting"
           echo "  4. Save file."
           echo ""
           echo "* More info: https://docs.gnuhealth.org/his/techguide/development/reports.html"
           echo ""
           exit_status=1
       fi
    fi
done

printf "\n\n\nRunning odt direct formatting test ...\n\n"
find $PWD -type f -name "*.odt" -print0 | while IFS= read -r -d '' file; do
    unzip_cmd="unzip -p $file content.xml"
    if  $unzip_cmd | grep -q "text:span text:style-name=" || \
            $unzip_cmd | grep -q "  <text:s/>" || \
            $unzip_cmd | grep -q "text:span><text:span" ; then
        echo "* WARN: Direct formatting found, it MAYBE impact translation ..."
        echo ""
        echo "  1. xdg-open $file"
        echo "  2. Click: Edit -> Select ALL"
        echo "  3. Click: Format -> Clean Direct Formatting"
        echo "  4. Save file."
        echo ""
        echo "* More info: https://docs.gnuhealth.org/his/techguide/development/reports.html"
        echo ""
        exit_status=1
    fi
done

printf "\n\n\nRunning fodt Date and DateTime field test ...\n\n"
find $PWD -type f -name "*.fodt" -print0 | while IFS= read -r -d '' file; do
    if grep -q "date&gt;<" "$file" || \
            grep -q "time&gt;<" "$file"; then
        echo ""
        echo "* WARN: Date and DateTime fields suggest handle by format_date or format_datetime function"
        echo ""
        echo "  1. xdg-open $file"
        echo ""
        exit_status=1
    fi
done

printf "Running odt Date and DateTime field test ...\n\n"
find $PWD -type f -name "*.odt" -print0 | while IFS= read -r -d '' file; do
    unzip_cmd="unzip -p $file content.xml"
    if $unzip_cmd | grep -q "date&gt;<" || \
            $unzip_cmd | grep -q "time&gt;<"; then
        echo ""
        echo "* WARN: Date and DateTime fields suggest handle by format_date or format_datetime function"
        echo ""
        echo "  1. xdg-open $file"
        echo ""
        exit_status=1
    fi
done

# Don't exit 0 if we had errors
exit "${exit_status:-0}"
