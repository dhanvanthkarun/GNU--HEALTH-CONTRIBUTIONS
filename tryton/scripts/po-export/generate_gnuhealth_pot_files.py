#!/usr/bin/env python

# Generates the template English files
#  
# The script traverses all the health* root_dirs and export
# the source English strings to the health_*.pot file in the
# locale directory

# Adapted from Tryton script to export to weblate

# Usage : generate_gnuhealth_pot_files.py --database=<db_name> root_dir
# Example: generate_gnuhealth_pot_files.py --database=health42 tryton

import os
import shutil
from optparse import OptionParser

from proteus import config, Model, Wizard


def main(root_dir, options):
    config.set_trytond(database=options.database, user='root')

    Lang = Model.get('ir.lang')
    Module = Model.get('ir.module')
    Translation = Model.get('ir.translation')
    Menu = Model.get('ir.ui.menu')

    Wizard('ir.translation.set', [Menu()]).execute('set_')
    Wizard('ir.translation.clean').execute('clean')

    languages = Lang.find([
            ('translatable', '=', True),
            ('code', '!=', 'en'),
            ])
    english, = Lang.find([
            ('code', '=', 'en'),
            ])

    for language in languages:
        update_wizard = Wizard('ir.translation.update')
        update_wizard.start.language = language
        update_wizard.execute('update')

    translations = Translation.find([
            ('value', '!=', None),
            ('value', '!=', ''),
            ])
    Translation.write(translations, {'value': ''}, {})

    for module in Module.find([('state', '=', 'activated')]):
        for language in (languages + [english]):
            export_wizard = Wizard('ir.translation.export')
            export_wizard.form.language = language
            export_wizard.form.module = module
            if 'health' in module.name:
                print(f"Exporting {module.name}") 
                export_wizard.execute('export')
                if not export_wizard.form.file:
                    continue
                if language == english:
                    poname = '%s.pot' % module.name
                elif module.name in {'ir', 'res'}:
                    poname = '%s.po' % language.code
                    path = os.path.join(
                        'trytond', 'trytond', module.name, 'locale')
                else:
                    poname = '%s.po' % language.code
                path = os.path.join(module.name, 'locale')
                pofile = os.path.join(root_dir, path, poname)
                with open(pofile, 'w') as f:
                    f.write(export_wizard.form.file.decode('utf-8'))


if __name__ == '__main__':
    parser = OptionParser("%prog [option] root_dir")
    parser.add_option('-d', '--database', dest='database')

    options, arguments = parser.parse_args()

    if not len(arguments) == 1:
        parser.error('Missing arguments')
    root_dir = arguments[0]
    print (root_dir)
    if not os.path.isdir(root_dir):
        parser.error('root_dir must be a directory')
    if not options.database:
        parser.error('Missing database')

    main(root_dir, options)
