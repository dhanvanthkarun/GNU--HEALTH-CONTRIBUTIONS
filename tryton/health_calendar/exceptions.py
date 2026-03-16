# SPDX-FileCopyrightText: 2008-2026 Luis Falcón <falcon@gnuhealth.org>
# SPDX-FileCopyrightText: 2011-2026 GNU Solidario <health@gnusolidario.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

#########################################################################
#   Hospital Management Information System (HMIS) component of the      #
#                       GNU Health project                              #
#                   https://www.gnuhealth.org                           #
#########################################################################
#                       HEALTH CALENDAR package                         #
#                  exceptions.py: Exceptions classes                    #
#########################################################################

from trytond.model.exceptions import ValidationError


class NoCompanyTimezone(ValidationError):
    pass


class EndDateBeforeStart(ValidationError):
    pass


class PeriodTooLong(ValidationError):
    pass


class AppointmentEndDateBeforeStart(ValidationError):
    pass
