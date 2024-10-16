#!/bin/bash

for py in $(find . -name '*.py'); 
do
    echo "# Formating ${py} ..."
    autopep8 --aggressive --max-line-length=79 --in-place ${py}
done
