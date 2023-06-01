#!/usr/bin/env python
# SPDX-FileCopyrightText: 2008-2023 Luis Falcón <falcon@gnuhealth.org>
# SPDX-FileCopyrightText: 2011-2023 GNU Solidario <health@gnusolidario.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

#########################################################################
#   Hospital Management Information System (HMIS) component of the      #
#                       GNU Health project                              #
#                   https://www.gnuhealth.org                           #
#########################################################################
#                     sync_orthanc_server.py                            #
#  Pulls the studies from a Orthanc DICOM server to the GNU Health HMIS #
#         Includes studies and patients from the DICOM server           #
#                                                                       #
#                   Return codes (rc):                                  #
#                    0 : No errors                                      #
#                    1 : Wrong number of arguments                      #
#                    2 : Orthanc Server label not found                 #
#########################################################################

from proteus import Model, config as pconfig
import sys

usage = "Usage : sync_orthanc_server <hostname> <port> <user> <password> " \
        "<dbname> <orthanc_server_label>"


def orthanc_sync():
    OrthancConfig = Model.get('gnuhealth.orthanc.config')

    # Try to find the orthanc server associated to the provided label
    find_orthanc_server = OrthancConfig.find(
        [('label', '=', orthanc_server_label)])

    if find_orthanc_server:
        orthanc_server, = find_orthanc_server
    else:
        print(f"Orthanc Server Label {orthanc_server_label} not found")
        sys.exit(2)

    index = orthanc_server.last
    last_sync = orthanc_server.sync_time
    orthanc_server_url = orthanc_server.domain

    print(f"Last index: {index}\nLast Synced on: {last_sync}")
    print(f"Orthanc Server URL: {orthanc_server_url}")

    orthanc_server.click('do_sync')

if (len(sys.argv) != 7):
    sys.exit(usage)

hostname = sys.argv[1]
port = sys.argv[2]
user = sys.argv[3]
passwd = sys.argv[4]
dbname = sys.argv[5]
orthanc_server_label = sys.argv[6]

health_server = f'http://{user}:{passwd}@{hostname}:{port}/{dbname}/'

print(f"Connecting to GNU Health Server {health_server}")
conf = pconfig.set_xmlrpc(health_server)
print("Connected !")

orthanc_sync()
