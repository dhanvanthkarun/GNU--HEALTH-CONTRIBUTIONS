# SPDX-FileCopyrightText: 2008-2025 Luis Falcón <falcon@gnuhealth.org>
# SPDX-FileCopyrightText: 2011-2025 GNU Solidario <health@gnusolidario.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from trytond.pool import PoolMeta

__all__ = ['PatientProcedure']


class PatientProcedure(metaclass=PoolMeta):
    __name__ = 'gnuhealth.patient.procedure'

    """
    Include patient rounding and ambulatory care references to the
    list of allowed procedures
    """

    @classmethod
    def _get_origin(cls):
        return super(PatientProcedure, cls)._get_origin() + [
            'gnuhealth.patient.ambulatory_care',
        ]
