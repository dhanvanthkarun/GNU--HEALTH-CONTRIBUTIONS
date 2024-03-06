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
    seconds = options.seconds

    if seconds:
        while True:
            global worklist_files
            worklist_files = []
            try:
                connect_service(options)
                update_worklists_database(options)
            except BaseException:
                None
            time.sleep(seconds)
    else:
        connect_service(options)
        update_worklists_database(options)


def parse_options():
    parser = argparse.ArgumentParser()

    parser.add_argument('-H', '--hostname', default='localhost',
                        help="Hostname of GNU Health Service, "
                        "default=localhost.")
    parser.add_argument('-p', '--port', default='8000',
                        help="Port of GNU Health Service, "
                        "default=8000.")
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
    parser.add_argument('-m', '--handle-done-state',
                        action="store_true",
                        help="Create worklists when "
                        "request state is 'done', slowly.")
    parser.add_argument('-s', '--seconds', type=int,
                        help="Update Worklists database every n seconds.")

    return parser.parse_args()


def connect_service(options):
    hostname = options.hostname
    port = options.port
    user = options.user
    passwd = options.passwd
    dbname = options.database

    health_server = 'http://' + user + ':' + passwd + \
        '@' + hostname + ':' + port + '/' + dbname + '/'

    print("# Connecting to GNU Health Server ...")
    pconfig.set_xmlrpc(health_server)


def update_worklists_database(options):
    worklists_db = options.worklists_db
    regenerate = options.regenerate
    handle_done_state = options.handle_done_state

    # Create lockfile, this file is useful when use wlmscpfs of dcmtk
    # to debug.
    lockfile = os.path.join(worklists_db, "lockfile")
    if not os.path.exists(lockfile):
        with open(lockfile, 'w') as f:
            f.write('')

    TestRequest = Model.get('gnuhealth.imaging.test.request')
    OrthancStudy = Model.get('gnuhealth.orthanc.study')

    if handle_done_state:
        domain = [('state', '!=', 'draft')]
    else:
        domain = [('state', '=', 'requested')]

    test_requests = TestRequest.find(domain)

    if test_requests:
        print(f'\n# Updating Worklists Database: "{worklists_db}" ...\n')
        for request in test_requests:
            worklist_text = request.worklist_text
            request_num = request.request
            patient = request.patient.rec_name
            requested_test = request.requested_test.rec_name
            worklist_template = request.requested_test.worklist_template
            encoding = worklist_template.dump_file_encoding

            merge_id = request.merge_id
            if len(merge_id) > 0:
                studies = OrthancStudy.find([('merge_id', '=', merge_id)])
            if len(worklist_text) > 0 and (not studies):
                print(f'  * "{request_num}" - '
                      f'"{patient}" - "{requested_test}" ...')
                create_worklist_file(
                    worklist_text, worklists_db, regenerate, encoding)

    cleanup_worklists_database(worklists_db)


def create_worklist_file(
        worklist_text, worklists_db, regenerate, encoding):
    name = hashlib.md5((worklist_text + encoding).encode()).hexdigest()
    dump_file = os.path.join(worklists_db, name + ".dump")
    worklist_file = os.path.join(worklists_db, name + ".wl")

    if regenerate or (not os.path.exists(worklist_file)):
        with open(dump_file, 'w', encoding=encoding) as f:
            f.write(worklist_text)

        subprocess.check_call([
            'dump2dcm', '-g', '-q',
            dump_file, worklist_file])

    worklist_files.append(worklist_file)


def cleanup_worklists_database(worklists_db):
    print(f'\n# Removing useless files from "{worklists_db}" ...\n')
    for f in sorted(os.listdir(worklists_db)):
        path = os.path.join(worklists_db, f)
        root, ext = os.path.splitext(path)
        # XXX: Do not remove other type files, for example: lockfile,
        # which is useful when debug with wlmscpfs of dcmtk.
        if (ext in ['.dump', '.wl']) and (not (path in worklist_files)):
            print(f'  * {f} ...')
            os.remove(path)


if __name__ == '__main__':
    main()
