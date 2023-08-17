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
#                     update_worklists_database.py.py                   #
# Update Worklists Database direcory of Orthanc when orthanc Worklists  #
# plugin is used.                                                       #
#########################################################################

import sys
import os
import argparse
import hashlib
import subprocess
import time

from proteus import Model
from proteus import config as pconfig


worklist_files = []


def main():
    options = parse_options()
    worklists_db = options.worklists_db
    regenerate = options.regenerate
    seconds = options.seconds
    connect_service(options)

    if seconds:
        while True:
            global worklist_files
            worklist_files = []
            update_worklists_database(worklists_db, regenerate)
            time.sleep(int(seconds))
    else:
        update_worklists_database(worklists_db, regenerate)


def parse_options():
    parser = argparse.ArgumentParser()

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
    parser.add_argument('-w', '--worklists-db',
                        help="Worklists database.",
                        default='/var/lib/orthanc/worklists')
    parser.add_argument('-r', '--regenerate', action="store_true",
                        help="Regenerate worklists database.")
    parser.add_argument('-s', '--seconds',
                        help="Update Worklists database every n seconds.")

    return parser.parse_args()


def connect_service(options):
    hostname = options.hostname
    port     = options.port
    user     = options.user
    passwd   = options.passwd
    dbname   = options.database

    health_server = 'http://'+user+':'+passwd+'@'+hostname+':'+port+'/'+dbname+'/'
    
    print("# Connecting to GNU Health Server ...")
    conf = pconfig.set_xmlrpc(health_server)
    # Use XML RPC using session
    #conf = pconfig.set_xmlrpc_session(health_server, username=user, password=passwd)


def update_worklists_database(worklists_db, regenerate):
    TestRequest = Model.get('gnuhealth.imaging.test.request')

    test_requests = TestRequest.find(
        [('state', '=', 'requested')])

    if test_requests:
        print(f'\n# Updating Worklists Database: "{worklists_db}" ...\n')
        for request in test_requests:
            worklist_text = request.worklist_text
            request_num = request.request
            patient = request.patient.rec_name
            if len(worklist_text) > 0:
                print(f'  * "{request_num}" - "{patient}" ...')
                create_worklist_file(worklist_text, worklists_db, regenerate)

    cleanup_worklists_database(worklists_db)


def create_worklist_file(worklist_text, worklists_db, regenerate):
    name = hashlib.md5(worklist_text.encode()).hexdigest()
    dump_file = os.path.join(worklists_db, name + ".dump")
    worklist_file = os.path.join(worklists_db, name + ".wl")
    
    if regenerate or (not os.path.exists(worklist_file)):
        with open(dump_file, 'w') as f:
            f.write(worklist_text)
        
        subprocess.check_call([
            'dump2dcm', '-g', '-q',
            dump_file, worklist_file])
    
    worklist_files.append(worklist_file)


def cleanup_worklists_database(worklists_db):
    print(f'\n# Removing useless files from "{worklists_db}" ...\n')
    for f in sorted(os.listdir(worklists_db)):
        path = os.path.join(worklists_db, f)
        if not (path in worklist_files):
            print(f'  * {f} ...')
            os.remove(path)


if __name__ == '__main__':
    main()
