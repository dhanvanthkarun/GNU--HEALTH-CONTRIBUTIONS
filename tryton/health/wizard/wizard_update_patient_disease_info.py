# SPDX-FileCopyrightText: 2008-2023 Luis Falcón <falcon@gnuhealth.org>
# SPDX-FileCopyrightText: 2011-2023 GNU Solidario <health@gnusolidario.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#########################################################################
#   Hospital Management Information System (HMIS) component of the      #
#                       GNU Health project                              #
#                   https://www.gnuhealth.org                           #
#########################################################################
#                           HEALTH package                              #
#              wizard_update_patient_disease_info.py: wizard            #
#########################################################################
from trytond.wizard import Wizard, StateView, Button, StateAction, StateTransition
from trytond.model import ModelView, fields
from trytond.transaction import Transaction
from trytond.pool import Pool

from trytond.modules.health.core import (parse_compute_age)

__all__ = ['UpdatePatientDiseaseInfo']


class UpdatePatientDiseaseInfo(Wizard):
    __name__ = 'gnuhealth.update_patient_disease_info'

    start = StateView(
        'gnuhealth.patient.disease',
        'health.gnuhealth_patient_diseases_view_form_for_wizard', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Save', 'save', 'tryton-ok', default=True)])

    save = StateTransition()

    def default_start(self, fields):
        pool = Pool()
        Evaluation = pool.get('gnuhealth.patient.evaluation')

        evaluation = Evaluation.browse(
            [Transaction().context.get('active_id')])[0]

        return {'name': evaluation.patient and evaluation.patient.id,
                # XXX: ONLY get years number from age string of
                # evaluation, for age of disease info is an Integer
                # field, can we change age of disease info to char
                # field?
                'age': evaluation.patient and parse_compute_age(evaluation.patient.age)[0],
                'pathology': evaluation.diagnosis and evaluation.diagnosis.id,
                'institution': evaluation.institution and evaluation.institution.id,
                'diagnosed_date': evaluation.evaluation_endtime}

    def transition_save(self):
        pool = Pool()
        Disease = Pool().get('gnuhealth.patient.disease')
        Disease.save([self.start])
        return 'end'
