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
#                       gnuhealth-data-import.py                        #
#               Sample script to import data to gnuhealth               #
#########################################################################
import argparse
import csv

from proteus import Model
from proteus import config as pconfig


def main():
    options = parse_options()
    connect_service(options)
    update_criteareas()


def parse_options():
    parser = argparse.ArgumentParser()

    parser.add_argument('-H', '--hostname', default='localhost',
                        help="Hostname of GNU Health Service, "
                        "default=localhost.")
    parser.add_argument('-p', '--port', default='8000',
                        help="Port of GNU Health Service, default=8000.")
    parser.add_argument('-u', '--user', default='admin',
                        help="User name of GNU Health, default=admin.")
    parser.add_argument('-P', '--passwd', required=True,
                        help="Password of GNU Health.")
    parser.add_argument('-d', '--database', required=True,
                        help="Database name of GNU Health.")

    return parser.parse_args()


def connect_service(options):
    hostname = options.hostname
    port = options.port
    user = options.user
    passwd = options.passwd
    dbname = options.database

    health_server = 'http://' + user + ':' + passwd + \
        '@' + hostname + ':' + port + '/' + dbname + '/'

    print("## Connecting to GNU Health Server ...")
    pconfig.set_xmlrpc(health_server)
    print("## Connected!\n")


def update_criteareas():
    fallback_maps = read_fallback_maps()

    Critearea = Model.get('gnuhealth.lab.test.critearea')
    criteareas = Critearea.find(
        [['OR',
          ('code', '=', ''),
          ('code', '=', None)],
         ('gnuhealth_lab_id', '!=', None)])

    for critearea in criteareas:
        x = Critearea.find(
            [('code', '!=', None),
             ('gnuhealth_lab_id', '=', None),
             ('test_type_id', '!=', None),
             ('name', '=', critearea.name)])

        codes = list(set([c.code for c in x]))
        fallback_code = fallback_maps.get(critearea.name)

        if len(codes) == 1:
            critearea.code = codes[0]
            critearea.save()
            print(f"* Update: '{critearea.name}' code  -> '{codes[0]}'")
        elif fallback_code:
            critearea.code = fallback_code
            critearea.save()
            print(f"* Update: '{critearea.name}' code  -> '{fallback_code}', "
                  "using fallback maps.")
        elif len(codes) > 1:
            print("* Ignore! Found multi code "
                  f"for '{critearea.name}' ...")
        else:
            print(f"* Ignore! Find no code for '{critearea.name}' ...")


def read_fallback_maps():
    csv_file = csv.reader(open('fallback-maps.csv', 'r'))
    result = {}
    for line in csv_file:
        name = line[0]
        code = line[1]
        if name != 'name':
            result[name] = code
    return result


if __name__ == '__main__':
    main()
