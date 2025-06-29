# SPDX-FileCopyrightText: 2020 Luis Falcón <falcon@gnuhealth.org>
# SPDX-FileCopyrightText: 2011-2025 GNU Solidario <health@gnusolidario.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#########################################################################
#   Hospital Management Information System (HMIS) component of the      #
#                       GNU Health project                              #
#                   https://www.gnuhealth.org                           #
#########################################################################
#                       HEALTH IMAGING package                          #
#              sequences.py: Sequences for this package                 #
#########################################################################

# from trytond.model import (ModelSQL, ValueMixin, fields)
from trytond.pyson import Id
from trytond.pool import Pool, PoolMeta
from trytond.model import (ModelSQL, ValueMixin, fields)

# Removed in GH 5.0
# from trytond.tools.multivalue import migrate_property

# Sequences
imaging_req_seq = fields.Many2One(
        'ir.sequence', 'Imaging Request Sequence', required=True,
        domain=[('sequence_type', '=', Id(
            'health_imaging', 'seq_type_gnuhealth_imaging_test_request'))])

imaging_test_sequence = fields.Many2One(
        'ir.sequence', 'Imaging Sequence', required=True,
        domain=[('sequence_type', '=', Id(
            'health_imaging', 'seq_type_gnuhealth_imaging_test'))])


# GNU HEALTH SEQUENCES
class GnuHealthSequences(metaclass=PoolMeta):
    'Standard Sequences for GNU Health'
    __name__ = 'gnuhealth.sequences'

    imaging_req_seq = fields.MultiValue(
        imaging_req_seq)

    imaging_test_sequence = fields.MultiValue(
        imaging_test_sequence)

    @classmethod
    def default_imaging_req_seq(cls, **pattern):
        pool = Pool()
        ModelData = pool.get('ir.model.data')
        try:
            return ModelData.get_id('health_imaging',
                                    'seq_gnuhealth_imaging_test_request')
        except KeyError:
            return None

    @classmethod
    def default_imaging_test_sequence(cls, **pattern):
        pool = Pool()
        ModelData = pool.get('ir.model.data')
        try:
            return ModelData.get_id('health_imaging',
                                    'seq_gnuhealth_imaging_test')
        except KeyError:
            return None


class _ConfigurationValue(ModelSQL):

    _configuration_value_field = None

    @classmethod
    def __register__(cls, module_name):

        super(_ConfigurationValue, cls).__register__(module_name)


class ImagingRequestSequence(_ConfigurationValue, ModelSQL, ValueMixin):
    'Imaging Request Sequence setup'
    __name__ = 'gnuhealth.sequences.imaging_req_seq'
    imaging_req_seq = imaging_req_seq
    _configuration_value_field = 'imaging_req_seq'

    @classmethod
    def check_xml_record(cls, records, values):
        return True


class ImagingTestSequence(_ConfigurationValue, ModelSQL, ValueMixin):
    'Imaging Test Sequence setup'
    __name__ = 'gnuhealth.sequences.imaging_test_sequence'
    imaging_test_sequence = imaging_test_sequence
    _configuration_value_field = 'imaging_test_sequence'

    @classmethod
    def check_xml_record(cls, records, values):
        return True
