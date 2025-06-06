# Copyright (C) 2008-2025 Luis Falcon <falcon@gnuhealth.org>
# Copyright (C) 2011-2025 GNU Solidario <health@gnusolidario.org>
# SPDX-FileCopyrightText: 2008-2025 Luis Falcón <falcon@gnuhealth.org>
# SPDX-FileCopyrightText: 2011-2025 GNU Solidario <health@gnusolidario.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

# GNU Health HMIS sequences for this package

from trytond.model import (ModelSQL, ValueMixin, fields)
from trytond.pyson import Id
from trytond.pool import Pool, PoolMeta
# Removed in GH 5.0
# from trytond.tools.multivalue import migrate_property

# Sequences
dengue_du_survey_sequence = fields.Many2One(
    'ir.sequence', 'Dengue DU Survey Sequence', required=True,
    domain=[('sequence_type', '=', Id(
        'health_ntd_dengue', 'seq_type_gnuhealth_dengue_du_survey'))])


# GNU HEALTH SEQUENCES
class GnuHealthSequences(metaclass=PoolMeta):
    'Standard Sequences for GNU Health'
    __name__ = 'gnuhealth.sequences'

    dengue_du_survey_sequence = fields.MultiValue(
        dengue_du_survey_sequence)

    @classmethod
    def default_dengue_du_survey_sequence(cls, **pattern):
        pool = Pool()
        ModelData = pool.get('ir.model.data')
        try:
            return ModelData.get_id('health_ntd_dengue',
                                    'seq_gnuhealth_dengue_du_survey')
        except KeyError:
            return None


class _ConfigurationValue(ModelSQL):

    _configuration_value_field = None

    @classmethod
    def __register__(cls, module_name):
        super(_ConfigurationValue, cls).__register__(module_name)


class DengueDUSurveySequence(_ConfigurationValue, ModelSQL, ValueMixin):
    'Dengue DU Survey Sequences setup'
    __name__ = 'gnuhealth.sequences.dengue_du_survey_sequence'
    dengue_du_survey_sequence = dengue_du_survey_sequence
    _configuration_value_field = 'dengue_du_survey_sequence'

    @classmethod
    def check_xml_record(cls, records, values):
        return True
