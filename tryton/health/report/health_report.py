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

__all__ = ['PatientDiseaseReport',
           'PatientMedicationReport',
           'PatientVaccinationReport',
           'PatientEvaluationReport']


def get_print_date():
    Company = Pool().get('company.company')

    timezone = None
    dt = datetime.now()
    company_id = Transaction().context.get('company')
    if company_id:
        company = Company(company_id)
        if company.timezone:
            timezone = pytz.timezone(company.timezone)
            return timezone, timezone.localize(dt)

    else:
        return dt


class PatientDiseaseReport(Report):
    __name__ = 'patient.disease'

    @classmethod
    def get_context(cls, records, header, data):
        context = super(
            PatientDiseaseReport, cls).get_context(records, header, data)
        timezone, tzdate = get_print_date()
        context['print_date'] = tzdate.date()
        context['print_time'] = tzdate.time()
        context['tz'] = timezone


class PatientMedicationReport(Report):
    __name__ = 'patient.medication'

    @classmethod
    def get_context(cls, records, header, data):
        context = super(
            PatientMedicationReport, cls).get_context(records, header, data)
        timezone, tzdate = get_print_date()
        context['print_date'] = tzdate.date()
        context['print_time'] = tzdate.time()
        context['tz'] = timezone

        return context


class PatientVaccinationReport(Report):
    __name__ = 'patient.vaccination'

    @classmethod
    def get_context(cls, records, header, data):
        context = super(
            PatientVaccinationReport, cls).get_context(records, header, data)
        timezone, tzdate = get_print_date()
        context['print_date'] = tzdate.date()
        context['print_time'] = tzdate.time()
        context['tz'] = timezone

        return context


class PatientEvaluationReport(Report):
    __name__ = 'gnuhealth.patient_evaluation'

    @classmethod
    def get_context(cls, records, header, data):
        context = super(
            PatientEvaluationReport, cls).get_context(records, header, data)
        timezone, tzdate = get_print_date()
        context['print_date'] = tzdate.date()
        context['print_time'] = tzdate.time()
        context['tz'] = timezone

        return context
