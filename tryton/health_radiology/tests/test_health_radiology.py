# SPDX-FileCopyrightText: 2008-2024 Luis Falcón <falcon@gnuhealth.org>
# SPDX-FileCopyrightText: 2011-2024 GNU Solidario <health@gnusolidario.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import ModuleTestCase


class HealthImagingTestCase(ModuleTestCase):
    '''
    Test Health Radiology module.
    '''
    module = 'health_radiology'

def suite():
    """
    Generate a test suite consisting of tests for the HealthImagingTestCase class.
    """
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        HealthImagingTestCase))
    return suite
