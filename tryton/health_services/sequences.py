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
health_service_sequence = fields.Many2One(
    'ir.sequence', 'Health service sequence', required=True,
    domain=[('sequence_type', '=', Id(
        'health_services', 'seq_type_gnuhealth_health_service'))])


# GNU HEALTH SEQUENCES
class GnuHealthSequences(metaclass=PoolMeta):
    'Standard Sequences for GNU Health'
    __name__ = 'gnuhealth.sequences'

    health_service_sequence = fields.MultiValue(
        health_service_sequence)

    @classmethod
    def default_health_service_sequence(cls, **pattern):
        pool = Pool()
        ModelData = pool.get('ir.model.data')
        try:
            return ModelData.get_id('health_services',
                                    'seq_gnuhealth_health_service')
        except KeyError:
            return None


class _ConfigurationValue(ModelSQL):

    _configuration_value_field = None

    @classmethod
    def __register__(cls, module_name):

        super(_ConfigurationValue, cls).__register__(module_name)


class HealthServiceSequence(_ConfigurationValue, ModelSQL, ValueMixin):
    'Health Service Request Sequence setup'
    __name__ = 'gnuhealth.sequences.health_service_sequence'
    health_service_sequence = health_service_sequence
    _configuration_value_field = 'health_service_sequence'

    @classmethod
    def check_xml_record(cls, records, values):
        return True
