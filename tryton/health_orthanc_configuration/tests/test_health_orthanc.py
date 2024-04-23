# SPDX-FileCopyrightText: 2008-2024 Luis Falcón <falcon@gnuhealth.org>
# SPDX-FileCopyrightText: 2011-2024 GNU Solidario <health@gnusolidario.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

#########################################################################
#   Hospital Management Information System (HMIS) component of the      #
#                       GNU Health project                              #
#                   https://www.gnuhealth.org                           #
#########################################################################
#                       HEALTH ORTHANC package                          #
#                test_health_orthanc.py health unittest file                    #
#########################################################################

import unittest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import ModuleTestCase


class HealthOrthancTestCase(ModuleTestCase):
    '''
    Test Orthanc configuration module.
    '''
    module = 'health_orthanc_configuration'

def suite():
    """
    Function to create a test suite for the HealthOrthancTestCase class.
    """
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        HealthOrthancTestCase))
    return suite
