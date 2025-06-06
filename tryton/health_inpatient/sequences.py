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
inpatient_registration_sequence = fields.Many2One(
    'ir.sequence', 'Inpatient Registration Sequence', required=True,
    domain=[('sequence_type', '=', Id(
        'health_inpatient', 'seq_type_gnuhealth_inpatient_registration'))])

inpatient_meal_order_sequence = fields.Many2One(
    'ir.sequence', 'Inpatient Meal order Sequence', required=True,
    domain=[('sequence_type', '=', Id(
        'health_inpatient', 'seq_type_gnuhealth_inpatient_meal_order'))])


patient_rounding_sequence = fields.Many2One(
    'ir.sequence', 'Patient Rounding Sequence', required=True,
    domain=[('sequence_type', '=', Id(
        'health_inpatient', 'seq_type_gnuhealth_patient_rounding'))])


# GNU HEALTH SEQUENCES
class GnuHealthSequences(metaclass=PoolMeta):
    'Standard Sequences for GNU Health'
    __name__ = 'gnuhealth.sequences'

    inpatient_registration_sequence = fields.MultiValue(
        inpatient_registration_sequence)

    inpatient_meal_order_sequence = fields.MultiValue(
        inpatient_meal_order_sequence)

    patient_rounding_sequence = fields.MultiValue(
        patient_rounding_sequence)

    @classmethod
    def default_inpatient_registration_sequence(cls, **pattern):
        pool = Pool()
        ModelData = pool.get('ir.model.data')
        try:
            return ModelData.get_id('health_inpatient',
                                    'seq_gnuhealth_inpatient_registration')
        except KeyError:
            return None

    @classmethod
    def default_inpatient_meal_order_sequence(cls, **pattern):
        pool = Pool()
        ModelData = pool.get('ir.model.data')
        try:
            return ModelData.get_id('health_inpatient',
                                    'seq_gnuhealth_inpatient_meal_order')
        except KeyError:
            return None

    @classmethod
    def default_patient_rounding_sequence(cls, **pattern):
        pool = Pool()
        ModelData = pool.get('ir.model.data')
        try:
            return ModelData.get_id('health_inpatient',
                                    'seq_gnuhealth_patient_rounding')
        except KeyError:
            return None


class _ConfigurationValue(ModelSQL):

    _configuration_value_field = None

    @classmethod
    def __register__(cls, module_name):
        super(_ConfigurationValue, cls).__register__(module_name)

    """
    @classmethod
    def _migrate_property(cls, field_names, value_names, fields):
        field_names.append(cls._configuration_value_field)
        value_names.append(cls._configuration_value_field)
        migrate_property(
            'gnuhealth.sequences', field_names, cls, value_names,
            fields=fields)

    """


class InpatientRegistrationSequence(_ConfigurationValue, ModelSQL, ValueMixin):
    'Inpatient Care Sequences setup'
    __name__ = 'gnuhealth.sequences.inpatient_registration_sequence'
    inpatient_registration_sequence = inpatient_registration_sequence
    _configuration_value_field = 'inpatient_registration_sequence'

    @classmethod
    def check_xml_record(cls, records, values):
        return True


class InpatientMealOrderSequence(_ConfigurationValue, ModelSQL, ValueMixin):
    'Patient Evaluation Sequence setup'
    __name__ = 'gnuhealth.sequences.inpatient_meal_order_sequence'
    inpatient_meal_order_sequence = inpatient_meal_order_sequence
    _configuration_value_field = 'inpatient_meal_order_sequence'

    @classmethod
    def check_xml_record(cls, records, values):
        return True


class PatientRoundingSequence(_ConfigurationValue, ModelSQL, ValueMixin):
    'Patient Evaluation Sequence setup'
    __name__ = 'gnuhealth.sequences.patient_rounding_sequence'
    patient_rounding_sequence = patient_rounding_sequence
    _configuration_value_field = 'patient_rounding_sequence'

    @classmethod
    def check_xml_record(cls, records, values):
        return True
