#!/usr/bin/env python
# SPDX-FileCopyrightText: 2008-2024 Luis Falcón <falcon@gnuhealth.org>
# SPDX-FileCopyrightText: 2011-2024 GNU Solidario <health@gnusolidario.org>
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

import sys
import argparse
import time

from proteus import Model
from proteus import config as pconfig


def main():
    options = parse_options()
    label = options.label
    seconds = options.seconds
    if seconds:
        while True:
            try:
                connect_service(options)
                orthanc_sync(label)
            except:
                None    
            time.sleep(seconds)
    else:
        connect_service(options)
        orthanc_sync(label)

def parse_options():
    parser = argparse.ArgumentParser()

    parser.add_argument('-l', '--label', required=True,
                        help="Lable of Orthanc server")
    parser.add_argument('-H', '--hostname', default='localhost',
                        help="Hostname of GNU Health Service, default=localhost.")
    parser.add_argument('-p', '--port', default='8000',
                        help="Port of GNU Health Service, default=8000.")
    parser.add_argument('-u', '--user', default='admin',
                        help="User name of GNU Health, default=admin.")
    parser.add_argument('-P', '--passwd', required=True,
                        help="Password of GNU Health.")
    parser.add_argument('-d', '--database', required=True,
                        help="Database name of GNU Health.")
    parser.add_argument('-s', '--seconds', type = int,
                        help="Sync orthanc service every n seconds.")

    return parser.parse_args()

def connect_service(options):
    hostname = options.hostname
    port     = options.port
    user     = options.user
    passwd   = options.passwd
    dbname   = options.database

    health_server = 'http://'+user+':'+passwd+'@'+hostname+':'+port+'/'+dbname+'/'
    
    print("Connecting to GNU Health Server ...")
    conf = pconfig.set_xmlrpc(health_server)
    # Use XML RPC using session
    #conf = pconfig.set_xmlrpc_session(health_server, username=user, password=passwd)
    print("Connected!")

def orthanc_sync(orthanc_server_label):
    OrthancConfig = Model.get('gnuhealth.orthanc.config')

    # Try to find the orthanc server associated to the provided label
    find_orthanc_server = OrthancConfig.find(
        [('label', '=', orthanc_server_label)])

    if find_orthanc_server:
        orthanc_server, = find_orthanc_server
    else:
        print(f"Orthanc Server Label: '{orthanc_server_label}' is not found.")
        sys.exit(2)

    index = orthanc_server.last
    last_sync = orthanc_server.sync_time
    orthanc_server_url = orthanc_server.domain

    print(f"Last index: {index}\nLast Synced on: {last_sync}")
    print(f"Orthanc Server URL: {orthanc_server_url}")

    orthanc_server.click('do_sync')


if __name__ == '__main__':
    main()
