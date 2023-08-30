#!/bin/bash 

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
