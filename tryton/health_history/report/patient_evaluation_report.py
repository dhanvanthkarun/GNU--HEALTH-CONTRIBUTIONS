# Copyright (C) 2008-2025 Luis Falcon <falcon@gnuhealth.org>
# Copyright (C) 2011-2025 GNU Solidario <health@gnusolidario.org>
# SPDX-FileCopyrightText: 2008-2025 Luis Falcón <falcon@gnuhealth.org>
# SPDX-FileCopyrightText: 2011-2025 GNU Solidario <health@gnusolidario.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

# import pytz
# from datetime import datetime
from trytond.pool import Pool
# from trytond.transaction import Transaction
from trytond.report import Report

__all__ = ['PatientEvaluationReport']


class PatientEvaluationReport(Report):
    __name__ = 'patient.evaluation'

    @classmethod
    def module_status(cls, module_name):
        Module = Pool().get('ir.module')
        module = Module.search([('name', '=', module_name)], limit=1)
        if (module and module[0].state == 'activated'):
            return True
        else:
            return False

    @classmethod
    def get_context(cls, records, header, data):
        context = super(
            PatientEvaluationReport, cls).get_context(records, header, data)

        # Check if the socioecomics package is installed
        if (cls.module_status('health_socioeconomics')):
            context['socioeconomicsmod'] = True
        else:
            context['socioeconomicsmod'] = False

        # Check if the surgery package is installed
        if (cls.module_status('health_surgery')):
            context['surgerymod'] = True
        else:
            context['surgerymod'] = False

        # Check if the genetics package is installed
        if (cls.module_status('health_genetics')):
            context['geneticsmod'] = True
        else:
            context['geneticsmod'] = False

        # Check if the lifestyle package is installed
        if (cls.module_status('health_lifestyle')):
            context['lifestylemod'] = True
        else:
            context['lifestylemod'] = False

        # Check if the crypto package is installed
        if (cls.module_status('health_crypto')):
            context['cryptomod'] = True
        else:
            context['cryptomod'] = False

        return context
