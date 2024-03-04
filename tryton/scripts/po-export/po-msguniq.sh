#!/bin/bash
#
# This script will remove duplicate records of all po|pot files in
# gnuhealth, for duplicate records will let msgcat command run error,
# gnuhealth-control use msgcat command to handle po files.

if [ ! command -v msguniq >/dev/null 2>&1 ]; then
    echo "msguniq command is not found, please install gettext package."
    exit 1
fi

PO_EXPORT_DIR=$(dirname "$(realpath "${BASH_SOURCE[0]}")")
cd ${PO_EXPORT_DIR}/../../

echo "## Delete duplicate records of po|pot files ..."
for po_file in $(find . -name '*.po*'); 
do
    msg=$(msguniq --repeated ${po_file})
    ## msguniq will change line wrap of po|pot file, so we only deal
    ## with files needed, this can reduce diff's size.
    if [ -n "${msg}" ]; then
        echo "   Handling: ${po_file} ..."
        msguniq --no-wrap --use-first ${po_file} -o ${po_file}
    fi

done
echo "## Delete duplicate records is finished."
