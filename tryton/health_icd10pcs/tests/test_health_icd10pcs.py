# SPDX-FileCopyrightText: 2008-2026 Luis Falcón <falcon@gnuhealth.org>
# SPDX-FileCopyrightText: 2011-2026 GNU Solidario <health@gnusolidario.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later
from trytond.tests.test_tryton import ModuleTestCase


class HealthICD10PCSTestCase(ModuleTestCase):
    '''
    Test Health ICD10PCS module.
    '''
    module = 'health_icd10pcs'


del ModuleTestCase
