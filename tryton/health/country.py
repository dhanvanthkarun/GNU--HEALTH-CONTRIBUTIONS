# SPDX-FileCopyrightText: 2008-2025 Luis Falcón <falcon@gnuhealth.org>
# SPDX-FileCopyrightText: 2011-2025 GNU Solidario <health@gnusolidario.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#########################################################################
#   Hospital Management Information System (HMIS) component of the      #
#                       GNU Health project                              #
#                   https://www.gnuhealth.org                           #
#########################################################################

from trytond.pool import PoolMeta

__all__ = ['Subdivision']

""" A list of subdivision types not included in pycountry or Tryton
    but that I consider important in our context.
    More info:
    https://en.wikipedia.org/wiki/Administrative_division
"""

SUBDIVISIONS = [
    ('first_nations_reserve', 'First Nations Reserve'),
    ('hamlet', 'Hamlet'),
    ('neighborhood', 'Neighborhood'),
    ('native_american_reserve', 'Native American Reserve'),
    ('resort', 'Resort'),
    ('village', 'Village'),
    ]


class Subdivision(metaclass=PoolMeta):
    __name__ = 'country.subdivision'

    @classmethod
    def __setup__(cls):
        """ Include new subdivisions to Tryton country package
            if they would not exist.
        """
        super().__setup__()
        for subdivision in SUBDIVISIONS:
            if subdivision not in cls.type.selection:
                cls.type.selection.append(subdivision)
