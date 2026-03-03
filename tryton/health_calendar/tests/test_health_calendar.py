# SPDX-FileCopyrightText: 2008-2026 Luis Falcón <falcon@gnuhealth.org>
# SPDX-FileCopyrightText: 2011-2026 GNU Solidario <health@gnusolidario.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#########################################################################
#   Hospital Management Information System (HMIS) component of the      #
#                       GNU Health project                              #
#                   https://www.gnuhealth.org                           #
#########################################################################
#                    HEALTH CALENDAR package                            #
#          test_health_calendar.py health unittest file                 #
#########################################################################
from trytond.tests.test_tryton import ModuleTestCase


class HealthCalendarTestCase(ModuleTestCase):
    '''
    Test Health Calendar module.
    '''
    module = 'health_calendar'


del ModuleTestCase
