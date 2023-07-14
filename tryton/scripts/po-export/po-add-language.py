#!/usr/bin/env python3

import sys
import os
from optparse import OptionParser
from proteus import config, Model, Wizard

def main(options):
    database = options.db
    user = options.user
    languages = options.lang.split()
    connect_health_server(database, user)
    for language in languages:
        add_language(language)

def connect_health_server(database, user):
    print("Connecting to database '{}' with '{}' ...".format(database, user))
    config.set_trytond(database=database, user=user)

def add_language(language):
    Lang = Model.get('ir.lang')
    lang = Lang.find([('code', '=', language)])

    if not lang:
        print("Language '{0}' is not exist in tryton at the moment, adding ...".format(language))
        lang=Lang()
        lang.code=language
        lang.name="X_Lang({0})".format(language)
        lang.save()

if __name__ == '__main__':
    parser = OptionParser("%prog [options]")
    parser.add_option('-d', '--database', dest='db')
    parser.add_option('-u', '--user', dest='user')
    ## Need improve: At the moment, --languages is a string, for
    ## example: --language "zh_CN ca", we should support:
    ## --languages zh_CN ca.
    parser.add_option('-l', '--languages', dest="lang")
    parser.set_defaults(user='admin', db='', lang='')

    options, module_path = parser.parse_args()
    if not options.db:
        parser.error('You must define a database')
    if not options.lang:
        parser.error('You must set a string of languages, for example: "zh_CN ca"')

    main(options)

