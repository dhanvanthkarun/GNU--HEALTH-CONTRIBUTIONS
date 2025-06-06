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

# Sequences
ambulatory_care_sequence = fields.Many2One(
    'ir.sequence', 'Ambulatory Sequence', required=True,
    domain=[('sequence_type', '=', Id(
        'health_nursing', 'seq_type_gnuhealth_ambulatory_care'))])


# GNU HEALTH SEQUENCES
class GnuHealthSequences(metaclass=PoolMeta):
    'Standard Sequences for GNU Health'
    __name__ = 'gnuhealth.sequences'

    ambulatory_care_sequence = fields.MultiValue(
        ambulatory_care_sequence)

    @classmethod
    def default_ambulatory_care_sequence(cls, **pattern):
        pool = Pool()
        ModelData = pool.get('ir.model.data')
        try:
            return ModelData.get_id('health_nursing',
                                    'seq_gnuhealth_ambulatory_care')
        except KeyError:
            return None


class _ConfigurationValue(ModelSQL):

    _configuration_value_field = None

    @classmethod
    def __register__(cls, module_name):
        super(_ConfigurationValue, cls).__register__(module_name)


class AmbulatoryCareSequence(_ConfigurationValue, ModelSQL, ValueMixin):
    'Ambulatory Care Sequences setup'
    __name__ = 'gnuhealth.sequences.ambulatory_care_sequence'
    ambulatory_care_sequence = ambulatory_care_sequence
    _configuration_value_field = 'ambulatory_care_sequence'

    @classmethod
    def check_xml_record(cls, records, values):
        return True
