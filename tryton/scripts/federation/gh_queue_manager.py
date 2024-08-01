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
#                       gh_queue_manager.py                             #
#   Sends the queued messages from the HMIS to the GH Federation        #
#########################################################################

import sys
import argparse

from proteus import Model
from proteus import config as pconfig


def main():
    options = parse_options()
    action = options.action
    connect_service(options)
    federation_queue(action)

def parse_options():
    parser = argparse.ArgumentParser()

    parser.add_argument('-a', '--action', required=True,
                        help="Action: 'check' or 'push'.")
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

def federation_queue(action):
    Queue = Model.get('gnuhealth.federation.queue')

    mqueued = Queue.find ([('state', '=', 'queued')])
    queued_messages = len(mqueued)
    
    print ("Number of messages in the queue", queued_messages)
    if (action == "check"):
        exit (0)

    if (action == "push"):
        print ("Sending messages with status Queued...")
        for msg in mqueued:
            print (msg.msgid, msg.federation_locator, msg.time_stamp, msg.model, msg.node)
            try:
                msg.click('send')
            except:
                print ("Failed to send message ", msg.msgid)


if __name__ == '__main__':
    main()
