#!/bin/bash

# This requires a running PostgreSQL and GNU Health server
# TRYTOND_CONFIG pointing to your config file
# DB_NAME pointing to your database

[[ ! -f fail.log ]] || rm fail.log
[[ ! -f fail_short.log ]] || rm fail_short.log
cd tryton
for module in $(ls -d health*); do
  cd $module
  python3 setup.py test >> ../../fail.log 2>&1
  echo "$module" >> ../../fail_short.log
  tail -n 5 ../../fail.log >> ../../fail_short.log
  rm -r "gnu${module}.egg-info/"
  cd ..
done
