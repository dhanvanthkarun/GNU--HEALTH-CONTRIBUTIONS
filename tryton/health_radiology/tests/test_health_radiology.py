# SPDX-FileCopyrightText:  2024- Wei Zhao <wei.zhao@uclouvain.be>
# SPDX-License-Identifier: GPL-3.0-or-later

#########################################################################
#   Hospital Management Information System (HMIS) component of the      #
#                       GNU Health project                              #
#                   https://www.gnuhealth.org                           #
#########################################################################
#                       HEALTH RADIOLOGY package                          #
#                test_health_radiology.py health unittest file            #
#########################################################################
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
    Generate a test suite consisting of tests for the HealthOrthancTestCase class.
    """
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        HealthRadiologyTestCase))
    return suite
