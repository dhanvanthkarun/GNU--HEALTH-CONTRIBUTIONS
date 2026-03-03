# SPDX-FileCopyrightText: 2008-2026 Luis Falcón <falcon@gnuhealth.org>
# SPDX-FileCopyrightText: 2011-2026 GNU Solidario <health@gnusolidario.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

#########################################################################
#   Hospital Management Information System (HMIS) component of the      #
#                       GNU Health project                              #
#                   https://www.gnuhealth.org                           #
#########################################################################
#                       HEALTH ARCHIVES package                         #
#                test_health_archives.py unittest file                  #
#########################################################################
from trytond.tests.test_tryton import ModuleTestCase


class HealthArchivesTestCase(ModuleTestCase):
    '''
    Test Health Archives module.
    '''
    module = 'health_archives'


del ModuleTestCase
