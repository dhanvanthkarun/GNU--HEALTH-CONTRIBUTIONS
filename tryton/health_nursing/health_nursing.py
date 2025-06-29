#!/usr/bin/env python

# SPDX-FileCopyrightText: 2008-2025 Luis Falcón <falcon@gnuhealth.org>
# SPDX-FileCopyrightText: 2011-2025 GNU Solidario <health@gnusolidario.org>

# SPDX-License-Identifier: GPL-3.0-or-later

#########################################################################
#   Hospital Management Information System (HMIS) component of the      #
#                       GNU Health project                              #
#                   https://www.gnuhealth.org                           #
#########################################################################
#                     HEALTH NURSING package                            #
#                health_nursing.py: main module                         #
#########################################################################
from trytond.model import ModelView, ModelSQL, fields
from datetime import datetime
from trytond.pool import Pool
from trytond.pyson import Eval, Equal
from trytond.i18n import gettext
from trytond.modules.health.core import get_health_professional

from .exceptions import (
    NoAssociatedHealthProfessional
)

__all__ = [
    'PatientAmbulatoryCare', 'AmbulatoryCareProcedure']


class PatientAmbulatoryCare(ModelSQL, ModelView):
    'Ambulatory Care'
    __name__ = 'gnuhealth.patient.ambulatory_care'

    STATES = {'readonly': Eval('state') == 'done'}

    name = fields.Char('ID', readonly=True)
    patient = fields.Many2One(
        'gnuhealth.patient', 'Patient',
        required=True, states=STATES)

    state = fields.Selection([
        (None, ''),
        ('draft', 'In Progress'),
        ('done', 'Done'),
    ], 'State', readonly=True)

    base_condition = fields.Many2One(
        'gnuhealth.pathology', 'Condition',
        states=STATES)
    evaluation = fields.Many2One(
        'gnuhealth.patient.evaluation',
        'Related Evaluation', domain=[('patient', '=', Eval('patient'))],
        depends=['patient'], states=STATES)
    ordering_professional = fields.Many2One(
        'gnuhealth.healthprofessional',
        'Requested by', states=STATES)
    health_professional = fields.Many2One(
        'gnuhealth.healthprofessional',
        'Health Prof', readonly=True)

    ambulatory_procedures = fields.One2Many(
        'gnuhealth.patient.procedure', 'reference', 'Procedures',
        domain=[
            ('patient', '=', Eval('patient')),
            ('ctx', '=', 'ambulatory'),
            # ('pdate', '=', Eval('session_start')),
        ],
        depends=['patient'],
        help='Procedures done during the ambulatory care session')

    # Deprecated in GH 5.0 by ambulatory_procedures
    procedures = fields.One2Many(
        'gnuhealth.ambulatory_care_procedure', 'ambcare',
        'Procedures', states=STATES,
        help="List of the procedures in this session. Please enter the first "
        "one as the main procedure")
    session_number = fields.Integer('Session #', states=STATES)
    session_start = fields.DateTime('Start', required=True, states=STATES)

    # Vital Signs
    systolic = fields.Integer('Systolic Pressure', states=STATES)
    diastolic = fields.Integer('Diastolic Pressure', states=STATES)
    bpm = fields.Integer(
        'Heart Rate', states=STATES,
        help='Heart rate expressed in beats per minute')
    respiratory_rate = fields.Integer(
        'Respiratory Rate', states=STATES,
        help='Respiratory rate expressed in breaths per minute')
    osat = fields.Integer(
        'Oxygen Saturation', states=STATES,
        help='Oxygen Saturation(arterial).')
    temperature = fields.Float(
        'Temperature', states=STATES,
        help='Temperature in celsius')

    warning = fields.Boolean(
        'Warning', help="Check this box to alert the "
        "supervisor about this session. A warning icon will be shown in the "
        "session list", states=STATES)
    warning_icon = fields.Function(
        fields.Char('Warning Icon'), 'get_warn_icon')

    # Glycemia
    glycemia = fields.Integer(
        'Glycemia', help='Blood Glucose level',
        states=STATES)

    weight = fields.Integer(
        'Weight',
        help="Measured weight, in kg")

    pain = fields.Boolean(
        'Pain',
        help="Check if the patient is in pain")

    pain_level = fields.Integer(
        'Pain level',
        help="Enter the pain level, from 1 to 10.")

    evolution = fields.Selection([
        (None, ''),
        ('initial', 'Initial'),
        ('n', 'Status Quo'),
        ('i', 'Improving'),
        ('w', 'Worsening'),
    ], 'Evolution', help="Check your judgement of current "
        "patient condition", sort=False, states=STATES)

    evolution_str = evolution.translated('evolution')

    session_end = fields.DateTime('End', readonly=True)
    next_session = fields.DateTime('Next Session', states=STATES)
    session_notes = fields.Text('Notes', states=STATES)

    signed_by = fields.Many2One(
        'gnuhealth.healthprofessional', 'Signed by', readonly=True,
        states={'invisible': Equal(Eval('state'), 'draft')},
        help="Health Professional that signed the session")

    @staticmethod
    def default_ambulatory_procedures():
        """When creating a new patient ambulatory session,
           GNU Health checks if there is one code set on the
           gnuhealth.procedures.config model, and use it as the first line
           on the procedure list.
           The user can remove it or use another in that ambulatory care
           context.
        """
        ProceduresConfig = Pool().get('gnuhealth.procedures.config')(1)
        if (ProceduresConfig and ProceduresConfig.ambulatory_care):
            medical_procedure = int(ProceduresConfig.ambulatory_care)

            return [{'procedure': medical_procedure}]
        else:
            return []

    @staticmethod
    def default_health_professional():
        return get_health_professional()

    @staticmethod
    def default_session_start():
        return datetime.now()

    @staticmethod
    def default_state():
        return 'draft'

    def get_report_pain_and_level(self):
        if self.pain and self.pain_level:
            return gettext('health_nursing.msg_report_pain_level',
                           pain_level=str(self.pain_level))
        elif self.pain:
            return gettext('health_nursing.msg_report_pain_yes')
        else:
            return gettext('health_nursing.msg_report_pain_no')

    @classmethod
    def __setup__(cls):
        super(PatientAmbulatoryCare, cls).__setup__()
        cls._buttons.update({
            'end_session': {
                'invisible': ~Eval('state').in_(['draft']),
            }})

        cls._order.insert(0, ('session_start', 'DESC'))

        # Do not cache default_key as it depends on time
        cls.__rpc__['default_get'].cache = None

    @classmethod
    @ModelView.button
    def end_session(cls, sessions):
        # End the session and discharge the patient
        # Change the state of the session to "Done"
        signing_hp = get_health_professional()

        cls.write(sessions, {
            'state': 'done',
            'signed_by': signing_hp,
            'session_end': datetime.now()
        })

    @classmethod
    def validate(cls, records):
        super(PatientAmbulatoryCare, cls).validate(records)
        for record in records:
            record.check_health_professional()

    def check_health_professional(self):
        if not self.health_professional:
            raise NoAssociatedHealthProfessional(
                gettext('health.msg_no_associated_health_professional'))

    @classmethod
    def generate_code(cls, **pattern):
        Config = Pool().get('gnuhealth.sequences')
        config = Config(1)
        sequence = config.get_multivalue(
            'ambulatory_care_sequence', **pattern)
        if sequence:
            return sequence.get()

    @classmethod
    def create(cls, vlist):
        vlist = [x.copy() for x in vlist]
        for values in vlist:
            if not values.get('name'):
                values['name'] = cls.generate_code()
        return super(PatientAmbulatoryCare, cls).create(vlist)

    @classmethod
    def copy(cls, ambulatorycares, default=None):
        if default is None:
            default = {}
        default = default.copy()
        default['name'] = None
        default['session_start'] = cls.default_session_start()
        default['session_end'] = cls.default_session_start()
        return super(
            PatientAmbulatoryCare, cls).copy(
                ambulatorycares,
                default=default)

    def get_warn_icon(self, name):
        if self.warning:
            return 'gnuhealth-warning'


class AmbulatoryCareProcedure(ModelSQL, ModelView):
    'Ambulatory Care Procedure'
    __name__ = 'gnuhealth.ambulatory_care_procedure'

    ambcare = fields.Many2One('gnuhealth.patient.ambulatory_care', 'Session')
    procedure = fields.Many2One(
        'gnuhealth.procedure', 'Code', required=True,
        help="Procedure Code")
    comments = fields.Char('Comments')

    @classmethod
    def __register__(cls, module):
        table_h = cls.__table_handler__(module)

        # Migration from 4.4: rename name to ambcare
        if (table_h.column_exist('name')
                and not table_h.column_exist('ambcare')):
            table_h.column_rename('name', 'ambcare')

        super().__register__(module)
        table_h = cls.__table_handler__(module)
