#!/usr/bin/env python3

import os
import argparse
from proteus import config, Model, Wizard


useless_translations = [
    #'Module'         'Field'                             'Source'
    ('health_caldav', 'calendar.event,vevent',            'vevent'),
    ('health_caldav', 'calendar.event.alarm,valarm',      'valarm'),
    ('health_%',      '%',                         'LibreOffice/%'),
    ('health',        'patient.medication',  'iVBORw0KGgoAAAANSU%')]


def main():
    options = parse_options()
    database = options.database
    user = options.user
    export_languages = options.export_languages
    add_languages = options.add_languages
    run_cleanup_step = options.run_cleanup_step
    generate_pot = options.export_pot

    if database and user:
        connect_health_server(database, user)

        if add_languages:
            add_all_languages(add_languages)

        if export_languages:
            export_all_languages(export_languages, run_cleanup_step)

        if generate_pot:
            export_all_pot_files()

        finish_export()

    else:
        print(options)
        print('No database is connected.')


def parse_options():
    parser = argparse.ArgumentParser()

    parser.add_argument('-d', '--database', default='',
                        help="A tryton database.")
    parser.add_argument('-u', '--user', default='admin',
                        help="A tryton user, for example: admin.")
    parser.add_argument('-e', '--export-languages', nargs='+',
                        help="A list of languages exporting to po files,"
                        " for example: zh_CN ca.", default=[])
    parser.add_argument('-a', '--add-languages', nargs='+',
                        help="A list of languages adding to tryton,"
                        "for example: zh_CN ca.", default=[])
    parser.add_argument('-c', '--run-cleanup-step', action="store_true",
                        help="Run 'cleanup_translations()' or not.")

    parser.add_argument('-p', '--export-pot', action="store_true",
                        help="Generate the pot files and exit")

    return parser.parse_args()


def connect_health_server(database, user):
    print(f"Connecting to database '{database}' with '{user}' ...")
    config.set_trytond(database=database, user=user)


def export_all_languages(languages, run_cleanup_step):
    extract_en_translations()
    if run_cleanup_step:
        cleanup_translations()
    for language in languages:
        update_translations_from_en(language)
        delete_useless_translations(language)
        export_all_translations(language)


def extract_en_translations():
    print("Extracting en translations from models, views, reports ...")
    translation_set = Wizard('ir.translation.set')
    translation_set.execute('set_')


def cleanup_translations():
    print("Cleaning up translations ...")
    translation_clean = Wizard('ir.translation.clean')
    translation_clean.execute('clean')


def add_all_languages(languages):
    for language in languages:
        add_language(language)


def add_language(language):
    Lang = Model.get('ir.lang')
    lang = Lang.find([('code', '=', language)])

    if not lang:
        print(f"Language {language} does not exist in tryton at "
              "the moment, adding it...")
        lang = Lang()
        lang.code = language
        lang.name = f"X_Lang({language})"
        lang.save()


def update_translations_from_en(language):
    print(f"Syncing {language} translations with en translations.")
    Lang = Model.get('ir.lang')
    translation_update = Wizard('ir.translation.update')
    translation_update.form.language, = Lang.find([('code', '=', language)])
    translation_update.execute('update')


def delete_useless_translations(language):
    for lang in ['en', language]:
        Translation = Model.get('ir.translation')
        for module, field, source in useless_translations:
            translations = Translation.find([
                ('lang', '=', lang),
                ('module', 'ilike', module),
                ('name', 'ilike', field),
                ('src', 'ilike', source)])
            for translation in translations:
                print(f'Deleting {lang} translation of "{source}" in '
                      f'{translation.name}" ...')
                translation.delete()


def export_all_translations(language):
    print(f"Starting export {language} translations of gnuhealth modules ...")
    for module in get_all_health_module_names():
        po_file = get_po_file_path(module, language)
        print(f"## Exporting to '{po_file}'")
        export_translation(language, module, po_file)
    print(f"Finish to export '{language}' translations!")


def get_all_health_module_names():
    Module = Model.get('ir.module')
    modules = Module.find([('name', 'like', "health%"),
                           ('state', 'in', ['activated'])])
    return [module.name for module in modules]


def get_po_file_path(module_name, language):
    script_dir = os.path.abspath(os.path.dirname(__file__))
    path = f'{script_dir}/../../{module_name}/locale/{language}.po'
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
        print(f"   WARN: Module {module} have no translation for languate"
              f"{lang}.\n")
    else:
        os.makedirs(os.path.dirname(po_file), exist_ok=True)
        with open(po_file, 'wb') as binary_file:
            binary_file.write(translation_export.form.file)
    translation_export.execute('end')


def export_all_pot_files():
    extract_en_translations()
    delete_useless_translations('en')
    print("Starting export pot files of gnuhealth modules ...")
    for module in get_all_health_module_names():
        pot_file = get_pot_file_path(module)
        print(f'## Exporting pot file of "{module}" to "{pot_file}"')
        export_translation('en', module, pot_file)
    print("Finish to export pot files!")


def get_pot_file_path(module_name):
    script_dir = os.path.abspath(os.path.dirname(__file__))
    path = f'{script_dir}/../../{module_name}/locale/{module_name}.pot'
    return path


def finish_export():
    print("Finish to export!")


if __name__ == '__main__':
    main()
