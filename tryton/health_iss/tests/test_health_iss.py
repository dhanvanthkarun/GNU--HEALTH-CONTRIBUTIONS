# SPDX-FileCopyrightText: 2008-2026 Luis Falcón <falcon@gnuhealth.org>
# SPDX-FileCopyrightText: 2011-2026 GNU Solidario <health@gnusolidario.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later
from trytond.tests.test_tryton import ModuleTestCase


class HealthISSTestCase(ModuleTestCase):
    '''
    Test Health ISS module.
    '''
    module = 'health_iss'


del ModuleTestCase
