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
    extract_en_translations()
    ## cleanup_translations() is very very slow when export all
    ## languages, for we always recreate db in po-export.sh, so i
    ## think this step is no need to run.
    ## 
    ## cleanup_translations()
    for language in languages:
        update_translations_from_en(language)
        delete_useless_translations(language)
        export_all_translations(language)
    finish_export_translations()

def connect_health_server(database, user):
    print("Connecting to database '{}' with '{}' ...".format(database, user))
    config.set_trytond(database=database, user=user)

def extract_en_translations():
    print("Extracting en translations from models, views, reports ...")
    translation_set = Wizard('ir.translation.set')
    translation_set.execute('set_')

def cleanup_translations():
    print("Cleaning up translations ...")
    translation_clean = Wizard('ir.translation.clean')
    translation_clean.execute('clean')

def update_translations_from_en(language):
    print("Syncing {0} translations with en translations.".format(language))
    Lang = Model.get('ir.lang')
    translation_update = Wizard('ir.translation.update')
    translation_update.form.language, = Lang.find([('code', '=', language)])
    translation_update.execute('update')

def delete_useless_translations(language):
    for lang in ['en', language]:
        useless_translations = [
            # Module            Field                          Source
            ('health_caldav',  'calendar.event,vevent',       'vevent'),
            ('health_caldav',  'calendar.event.alarm,valarm', 'valarm'),
            ('health_%',       '%',                           'LibreOffice/%'),
            ('health',         'patient.medication',          'iVBORw0KGgoAAAANSU%')]
        Translation = Model.get('ir.translation')
        for module, field, source in useless_translations:
            translations = Translation.find([
                ('lang', '=', lang),
                ('module', 'ilike', module),
                ('name', 'ilike', field),
                ('src', 'ilike', source)])
            for translation in translations:
                print("Deleting {} translation of '{}' in '{}' ...".format(lang, source, translation.name))
                translation.delete()
 
def export_all_translations(language):
    print("Starting export {0} translations of gnuhealth modules ...".format(language))
    for module in get_all_health_module_names():
        po_file = get_po_file_path(module, language)
        print("## Exporting to '{0}'".format(po_file))
        export_translation(language, module, po_file)
    print("Finish to export '{0}' translations!".format(language))

def get_all_health_module_names():
    Module = Model.get('ir.module')
    modules = Module.find([('name', 'like', "health%"),
                           ('state', 'in', ['activated'])])
    return [module.name for module in modules]
    
def get_po_file_path(module_name, language):
    script_dir = os.path.abspath(os.path.dirname(__file__))
    path = script_dir + "/../../" + module_name + "/locale/" + language + ".po"
    return path

def export_translation(lang, module, po_file):
    Lang = Model.get('ir.lang')
    Module = Model.get('ir.module')
    translation_export = Wizard('ir.translation.export')
    translation_export.form.language, = Lang.find([('code', '=', lang)])
    translation_export.form.module, = Module.find([('name', '=', module)])
    translation_export.execute('export')
    data = translation_export.form.file
    if data is None:
        print("   WARN: Module {0} have no translation for languate {1}.\n".format(module, lang))
    else:
        os.makedirs(os.path.dirname(po_file), exist_ok=True)
        with open(po_file, 'wb') as binary_file:
            binary_file.write(translation_export.form.file)
    translation_export.execute('end')

def finish_export_translations():
    print("Finish to export!")

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

