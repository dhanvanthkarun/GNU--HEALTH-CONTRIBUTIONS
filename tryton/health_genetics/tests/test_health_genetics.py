# SPDX-FileCopyrightText: 2008-2026 Luis Falcón <falcon@gnuhealth.org>
# SPDX-FileCopyrightText: 2011-2026 GNU Solidario <health@gnusolidario.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later
from trytond.tests.test_tryton import ModuleTestCase


class HealthGeneticsTestCase(ModuleTestCase):
    '''
    Test HealthGenetics module.
    '''
    module = 'health_genetics'


del ModuleTestCase
