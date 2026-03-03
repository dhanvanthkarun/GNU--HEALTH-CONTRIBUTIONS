# SPDX-FileCopyrightText: 2008-2026 Luis Falcón <falcon@gnuhealth.org>
# SPDX-FileCopyrightText: 2011-2026 GNU Solidario <health@gnusolidario.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#########################################################################
#   Hospital Management Information System (HMIS) component of the      #
#                       GNU Health project                              #
#                   https://www.gnuhealth.org                           #
#########################################################################
#                HEALTH INPATIENT CALENDAR package                      #
#         test_health_inpatient_calendar.py main test module            #
#########################################################################
from trytond.tests.test_tryton import ModuleTestCase


class HealthInpatientCalendarTestCase(ModuleTestCase):
    '''
    Test Health Inpatient Calendar module.
    '''
    module = 'health_inpatient_calendar'


del ModuleTestCase
