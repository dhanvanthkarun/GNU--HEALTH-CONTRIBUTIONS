# SPDX-FileCopyrightText:  2024- Wei Zhao <wei.zhao@uclouvain.be>
# SPDX-License-Identifier: GPL-3.0-or-later

#########################################################################
#   Hospital Management Information System (HMIS) component of the      #
#                       GNU Health project                              #
#                   https://www.gnuhealth.org                           #
#########################################################################
#                       HEALTH IMAGING ORTHANC package                  #
#                test_health_imaging_orthanc.py health unittest file    #
#########################################################################
import trytond.tests.test_tryton
from trytond.tests.test_tryton import ModuleTestCase


class HealthImagingOrthancTestCase(ModuleTestCase):
    '''
    Test Health Imaging Orthanc module.
    '''
    module = 'health_imaging_orthanc'


def suite():
    """
    Generate a test suite consisting "
    "of tests for the HealthOrthancTestCase class.
    """
    suite = trytond.tests.test_tryton.suite()
    return suite
