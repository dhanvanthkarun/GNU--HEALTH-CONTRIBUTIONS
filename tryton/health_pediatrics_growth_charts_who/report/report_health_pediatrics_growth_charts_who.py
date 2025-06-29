# SPDX-FileCopyrightText: 2008-2025 Luis Falcón <falcon@gnuhealth.org>
# SPDX-FileCopyrightText: 2013 Sebastian Marro <smarro@thymbra.com>
# SPDX-FileCopyrightText: 2011-2025 GNU Solidario <health@gnusolidario.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from datetime import datetime
from trytond.report import Report
from trytond.pool import Pool
from trytond.i18n import gettext

__all__ = ['PediatricsGrowthChartsWHOReport', 'WeightForAge',
           'LengthHeightForAge', 'BMIForAge']


class PediatricsGrowthChartsWHOReport(Report):
    __name__ = 'gnuhealth.pediatrics.growth.charts.who.report'

    @classmethod
    def get_context(cls, records, header, data):

        _MODULE = "health_pediatrics_growth_charts_who"

        _TYPES = {
            '-3': 'p3',
            '-2': 'p15',
            '0': 'p50',
            '2': 'p85',
            '3': 'p97',
        }

        _INDICATORS = {
            'l/h-f-a': gettext(
                _MODULE + ".msg_indicator_length_or_height_for_age"),
            'w-f-a': gettext(
                _MODULE + ".msg_indicator_weight_for_age"),
            'bmi-f-a': gettext(
                _MODULE + ".msg_indicator_bmi_for_age"),
        }

        _MEASURES = {
            'p': gettext(_MODULE + ".msg_measure_percentiles"),
            'z': gettext(_MODULE + ".msg_measure_z_scores"),
        }

        _GENDERS = {
            'f': gettext(_MODULE + ".msg_gender_girls"),
            'm': gettext(_MODULE + ".msg_gender_boys"),
        }

        _SUBTITLE = gettext(_MODULE + ".msg_subtitle")

        pool = Pool()
        GrowthChartsWHO = pool.get(
            'gnuhealth.pediatrics.growth.charts.who')
        Patient = pool.get('gnuhealth.patient')
        Evaluation = pool.get('gnuhealth.patient.evaluation')

        context = super(
            PediatricsGrowthChartsWHOReport, cls).get_context(
                records, header, data)

        patient = Patient(data['patient'])

        growthchartswho = GrowthChartsWHO.search([
            ('indicator', '=', data['indicator']),
            ('measure', '=', data['measure']),
            ('sex', '=', patient.party.gender),
        ], order=[('month', 'ASC')],
        )

        context['title'] = _INDICATORS[data['indicator']].format(
            gender=_GENDERS[patient.party.gender])
        context['subtitle'] = _SUBTITLE.format(
            measure=_MEASURES[data['measure']])
        context['name'] = patient.party.rec_name
        context['puid'] = patient.puid
        context['date'] = datetime.now().date()
        context['age'] = patient.age
        context['measure'] = data['measure']

        if data['measure'] == 'p':
            context['p3'] = gettext(
                _MODULE + ".msg_table_header_percentile_p3"),
            context['p15'] = gettext(
                _MODULE + ".msg_table_header_percentile_p15"),
            context['p50'] = gettext(
                _MODULE + ".msg_table_header_percentile_p50"),
            context['p85'] = gettext(
                _MODULE + ".msg_table_header_percentile_p85"),
            context['p97'] = gettext(
                _MODULE + ".msg_table_header_percentile_p97"),
        else:
            context['p3'] = gettext(
                _MODULE + ".msg_table_header_z_score_p3"),
            context['p15'] = gettext(
                _MODULE + ".msg_table_header_z_score_p15"),
            context['p50'] = gettext(
                _MODULE + ".msg_table_header_z_score_p50"),
            context['p85'] = gettext(
                _MODULE + ".msg_table_header_z_score_p85"),
            context['p97'] = gettext(
                _MODULE + ".msg_table_header_z_score_p97"),

        for value in growthchartswho:
            if data['measure'] == 'p':
                context[value.type.lower() + '_' + str(value.month)] = \
                    value.value
            else:
                context[_TYPES[value.type] + '_' + str(value.month)] = \
                    value.value

        evaluations = Evaluation.search([
            ('patient', '=', data['patient']),
        ])

        for month in range(61):
            context['v' + str(month)] = ''

        for evaluation in evaluations:
            if evaluation.age_months is not None:
                con = ''.join(['v', str(evaluation.age_months)])
                if data['indicator'] == 'l/h-f-a':
                    context[con] = evaluation.height
                elif data['indicator'] == 'w-f-a':
                    context[con] = evaluation.weight
                else:
                    context[con] = evaluation.bmi

        return context


class WeightForAge(PediatricsGrowthChartsWHOReport):
    __name__ = 'gnuhealth.pediatrics.growth.charts.who.wfa.report'


class LengthHeightForAge(PediatricsGrowthChartsWHOReport):
    __name__ = 'gnuhealth.pediatrics.growth.charts.who.lhfa.report'


class BMIForAge(PediatricsGrowthChartsWHOReport):
    __name__ = 'gnuhealth.pediatrics.growth.charts.who.bmifa.report'
