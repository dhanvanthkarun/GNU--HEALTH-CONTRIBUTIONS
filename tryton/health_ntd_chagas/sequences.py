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
chagas_du_survey_sequence = fields.Many2One(
    'ir.sequence', 'Chagas DU Survey Sequence', required=True,
    domain=[('sequence_type', '=', Id(
        'health_ntd_chagas', 'seq_type_gnuhealth_chagas_du_survey'))])


# GNU HEALTH SEQUENCES
class GnuHealthSequences(metaclass=PoolMeta):
    'Standard Sequences for GNU Health'
    __name__ = 'gnuhealth.sequences'

    chagas_du_survey_sequence = fields.MultiValue(
        chagas_du_survey_sequence)

    @classmethod
    def default_chagas_du_survey_sequence(cls, **pattern):
        pool = Pool()
        ModelData = pool.get('ir.model.data')
        try:
            return ModelData.get_id('health_ntd_chagas',
                                    'seq_gnuhealth_chagas_du_survey')
        except KeyError:
            return None


class _ConfigurationValue(ModelSQL):

    _configuration_value_field = None

    @classmethod
    def __register__(cls, module_name):

        super(_ConfigurationValue, cls).__register__(module_name)


class ChagasDUSurveySequence(_ConfigurationValue, ModelSQL, ValueMixin):
    'Chagas DU Survey Sequences setup'
    __name__ = 'gnuhealth.sequences.chagas_du_survey_sequence'
    chagas_du_survey_sequence = chagas_du_survey_sequence
    _configuration_value_field = 'chagas_du_survey_sequence'

    @classmethod
    def check_xml_record(cls, records, values):
        return True
