#!/bin/bash 

# SPDX-FileCopyrightText: 2008-2024 Luis Falcón <falcon@gnuhealth.org>
# SPDX-FileCopyrightText: 2011-2024 GNU Solidario <health@gnusolidario.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later


if [[ $# -ne 2 ]]; then
    echo "Usage: `basename $0` DIR PORT" >&2
    exit 1
fi

DIR=$1
PORT=$2
DicomAets=`ls $DIR`

echo ""
echo "--------------------------------------------------"
echo "1. Directory: $DIR"
echo "2. Port:      $PORT"
echo "3. Aets:      "$DicomAets
echo "4. Test cmd:  findscu -W 127.0.0.1 $PORT -k 0008,0005=\"*\" -k 0010,0010=\"*\" -aec <Aet>"
echo "--------------------------------------------------"
echo ""

wlmscpfs --debug \
         --keep-char-set \
         --disable-file-reject \
         --data-files-path $DIR \
         $PORT
