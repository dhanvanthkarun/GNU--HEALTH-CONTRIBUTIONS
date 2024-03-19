#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2008-2024 Luis Falcón <falcon@gnuhealth.org>
# SPDX-FileCopyrightText: 2011-2024 GNU Solidario <health@gnusolidario.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later
import polib
import argparse


def main():
    options = parse_options()
    po_file = options.file
    try:
        # NOTE: Code needs to be compatible with 'translation_export'
        # method of 'trytond/ir/translation.py'.
        content = polib.pofile(po_file)
        if content:
            content.sort()
            with open(po_file, 'wb') as f:
                f.write(str(content).encode('utf-8'))
    except BaseException:
        return None


def parse_options():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-f', '--file',
        help="PO file need to format, the result will "
        "consistent as much as possible with po file "
        "exported by gnuhealth.")

    return parser.parse_args()


if __name__ == '__main__':
    main()
