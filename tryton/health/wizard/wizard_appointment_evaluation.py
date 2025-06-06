# SPDX-FileCopyrightText: 2008-2025 Luis Falcón <falcon@gnuhealth.org>
# SPDX-FileCopyrightText: 2011-2025 GNU Solidario <health@gnusolidario.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#########################################################################
#   Hospital Management Information System (HMIS) component of the      #
#                       GNU Health project                              #
#                   https://www.gnuhealth.org                           #
#########################################################################
#                           HEALTH package                              #
#                  wizard_appointment_evaluation.py: wizard             #
#########################################################################

from trytond.wizard import Wizard, StateAction
from trytond.transaction import Transaction
from trytond.pool import Pool
from trytond.pyson import PYSONEncoder

from trytond.i18n import gettext

from ..exceptions import NoAppointmentSelected
__all__ = ['CreateAppointmentEvaluation']


class CreateAppointmentEvaluation(Wizard):
    'Create Appointment Evaluation'
    __name__ = 'wizard.gnuhealth.appointment.evaluation'

    start_appointment_evaluation = StateAction('health.act_app_evaluation')
    start_state = 'start_appointment_evaluation'

    def do_start_appointment_evaluation(self, action):
        """ Fill in the relevant fields on the target patient evaluation
            form. The domain fields will be read-only, while the ones
            coming from the context can be manually updated
        """
        context = {}

        active_id = Transaction().context.get('active_id')

        if not active_id:
            raise NoAppointmentSelected(gettext(
                'health.msg_no_appointment_selected')
            )

        active_model = Transaction().context.get('active_model')
        action['name'] = f"{action['name']} {self.record.patient.rec_name}"

        Model = Pool().get(active_model)
        record = Model(active_id)

        action['pyson_domain'] = PYSONEncoder().encode([
            ('patient', '=', record.patient.id),
            ('appointment', '=', active_id),

        ])

        # Avoid overriding the patient evaluation default values
        # if they are not coded explicitly in the wizard.
        if record.healthprof:
            context['default_healthprof'] = record.healthprof.id

        if record.institution:
            context['default_institution'] = record.institution.id

        if record.insurance:
            context['default_insurance'] = record.insurance.id

        if record.speciality:
            context['default_specialty'] = record.speciality.id

        context.update({
            'default_urgency': record.urgency,
            'default_visit_type': record.visit_type,
            'default_evaluation_type': record.appointment_type,
        })

        action['pyson_context'] = PYSONEncoder().encode(context)
        return action, {}
