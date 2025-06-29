# SPDX-FileCopyrightText: 2008-2025 Luis Falcón <falcon@gnuhealth.org>
# SPDX-FileCopyrightText: 2013 Sebastian Marro <smarro@thymbra.com>
# SPDX-FileCopyrightText: 2011-2025 GNU Solidario <health@gnusolidario.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#########################################################################
#   Hospital Management Information System (HMIS) component of the      #
#                       GNU Health project                              #
#                   https://www.gnuhealth.org                           #
#########################################################################
#                 HEALTH PEDIATRICS_GROWTH_CHARTS_WHO package           #
#             health_pediatrics_growth_charts_who.py:main module        #
#########################################################################
from trytond.model import ModelView, ModelSQL, fields

__all__ = ['PediatricsGrowthChartsWHO']


class PediatricsGrowthChartsWHO(ModelSQL, ModelView):
    'Pediatrics Growth Chart WHO'
    __name__ = 'gnuhealth.pediatrics.growth.charts.who'

    indicator = fields.Selection([
        ('l/h-f-a', 'Length/height for age'),
        ('w-f-a', 'Weight for age'),
        ('bmi-f-a', 'Body mass index for age (BMI for age)'),
    ], 'Indicator', sort=False, required=True)
    indicator_str = indicator.translated('indicator')

    measure = fields.Selection([
        ('p', 'percentiles'),
        ('z', 'z-scores'),
    ], 'Measure')
    measure_str = measure.translated('measure')

    sex = fields.Selection([
        ('m', 'Male'),
        ('f', 'Female'),
    ], 'Sex')
    sex_str = sex.translated('sex')

    month = fields.Integer('Month')
    type = fields.Char('Type')
    value = fields.Float('Value')
