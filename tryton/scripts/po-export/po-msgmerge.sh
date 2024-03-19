#!/bin/bash

# SPDX-FileCopyrightText: 2008-2024 Luis Falcón <falcon@gnuhealth.org>
# SPDX-FileCopyrightText: 2011-2024 GNU Solidario <health@gnusolidario.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

# This script will remove duplicate records of all po|pot files in
# gnuhealth, for duplicate records will let msgcat command run error,
# gnuhealth-control use msgcat command to handle po files.

if [ ! command -v msgmerge >/dev/null 2>&1 ]; then
    echo "msgmerge command is not found, please install gettext package."
    exit 1
fi

PO_EXPORT_DIR=$(dirname "$(realpath "${BASH_SOURCE[0]}")")
cd ${PO_EXPORT_DIR}/../../

echo "## Update po file with msgmerge command ..."
for dir in $(ls .)
do
    if [ -d ${dir}/locale ];then
        cd ${dir}/locale
        for po_file in $(find . -name '*.po');
        do

            msgmerge --update --backup=none ${po_file} ${dir}.pot

            # Format po file with the help of polib, reduce git diff's
            # size.
            python ${PO_EXPORT_DIR}/po-polib-format.py --file ${po_file}

        done
    fi
done
echo "## Update po files is finished."
