# SPDX-FileCopyrightText: 2008-2024 Luis Falcón <falcon@gnuhealth.org>
# SPDX-FileCopyrightText: 2011-2024 GNU Solidario <health@gnusolidario.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

#########################################################################
#   Hospital Management Information System (HMIS) component of the      #
#                       GNU Health project                              #
#                   https://www.gnuhealth.org                           #
#########################################################################
#                           HEALTH package                              #
#   health_report.py: Disease, Medication and Vaccination reports       #
#########################################################################
import pytz
from datetime import datetime
from trytond.pool import Pool
from trytond.transaction import Transaction
from trytond.report import Report


__all__ = ['ReportPrintDateAndTimeMixin']


class ReportPrintDateAndTimeMixin():

    @classmethod
    def get_print_date(cls):
        Company = Pool().get('company.company')

        timezone = pytz.UTC
        dt = datetime.now()
        utc = dt.astimezone(pytz.UTC)
        localdate = dt
        company_id = Transaction().context.get('company')
        if company_id:
            company = Company(company_id)
            if company.timezone:
                timezone = pytz.timezone(company.timezone)
                localdate = utc.astimezone(timezone)

        return timezone, localdate

    @classmethod
    def get_context(cls, records, header, data):
        context = super(
            ReportPrintDateAndTimeMixin, cls).get_context(records, header, data)
        timezone, tzdate = cls.get_print_date()
        context['print_datetime'] = tzdate
        context['print_date'] = tzdate.date()
        context['print_time'] = tzdate.time()
        context['tz'] = timezone

        return context
