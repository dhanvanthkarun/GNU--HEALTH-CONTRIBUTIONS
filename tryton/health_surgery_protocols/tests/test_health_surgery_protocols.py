# SPDX-FileCopyrightText: 2008-2026 Luis Falcón <falcon@gnuhealth.org>
# SPDX-FileCopyrightText: 2011-2026 GNU Solidario <health@gnusolidario.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later
from trytond.tests.test_tryton import ModuleTestCase


class HealthSurgeryProtocolsTestCase(ModuleTestCase):
    '''
    Test Health Surgery Protocols module.
    '''
    module = 'health_surgery_protocols'


del ModuleTestCase
