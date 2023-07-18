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
#                       health_lab_interface.py                         #
#         Sample script to upload lab orders from a CSV file            #
#########################################################################

from proteus import Model
from proteus import config as pconfig
import pandas as pd

import csv
import sys
import argparse

def main():
    options = parse_options()
    filename = options.filename
    results = read_file(filename)
    connect_service(options)
    import_results(results)

def parse_options():
    parser = argparse.ArgumentParser()

    parser.add_argument('-f', '--filename', required=True,
                        help="A csv or ods file.")
    parser.add_argument('-H', '--hostname', default='localhost',
                        help="Hostname of GNU Health Service, for example: localhost.")
    parser.add_argument('-p', '--port', default='8000',
                        help="Port of GNU Health Service, for example: 8000.")
    parser.add_argument('-u', '--user', default='admin',
                        help="User name of GNU Health.")
    parser.add_argument('-P', '--passwd', required=True,
                        help="Password of GNU Health.")
    parser.add_argument('-d', '--database', required=True,
                        help="Database name of GNU Health.")

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

def read_file(filename):
    if filename.endswith('ods'):
        return pd.read_excel(filename,
                             ## Note: user need install odfpy
                             ## package.
                             engine='odf',
                             dtype='str',
                             keep_default_na=False,
                             index_col=False)    
    else:
        return pd.read_csv(filename,
                           sep=',',
                           skipinitialspace=True,
                           skip_blank_lines=True,
                           comment='#',
                           dtype='str',
                           keep_default_na=False,
                           index_col=False)
            
def import_results(results):
    LabTest = Model.get('gnuhealth.lab')
    LabTestLine = Model.get('gnuhealth.lab.test.critearea')
    note_fmt = "NOTE: '{0}/{1}' import success!"
    warn_fmt = "WARN: '{0}/{1}' is not found, ignore ..."
    for index, line in results.iterrows():
        line = dict(line)
        ignore = line.get('ignore')
        test_id = line.get('test_id')
        analyte_code = line.get('analyte_code')
        analyte_name = line.get('analyte_name')
        result = line.get('result')
        result_text = line.get('result_text')

        if (not ignore=='yes'):
            ## NOTE: 
            ## We prefer 'analyte_code' to 'analyte_name', for
            ## 'analyte_name' will change when user use different
            ## languages.        
            domain = [['OR', ('code','=',analyte_code), ('name','=',analyte_name)],
                      ('gnuhealth_lab_id','=',test_id)]
            test_lines = LabTestLine.find(domain)
            
            ## Update the model with the result values
            if test_lines:
                for result_line in test_lines:
                    result_line.result = float(result)
                    result_line.result_text = str(result_text)
                    result_line.save()
                    print(note_fmt.format(test_id, analyte_code))
            else:
                print(warn_fmt.format(test_id, analyte_code))

if __name__ == '__main__':
    main()
