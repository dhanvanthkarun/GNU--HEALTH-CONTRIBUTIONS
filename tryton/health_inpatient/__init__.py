# SPDX-FileCopyrightText: 2008-2025 Luis Falcón <falcon@gnuhealth.org>
# SPDX-FileCopyrightText: 2011-2025 GNU Solidario <health@gnusolidario.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#########################################################################
#   Hospital Management Information System (HMIS) component of the      #
#                       GNU Health project                              #
#                   https://www.gnuhealth.org                           #
#########################################################################
#                      HEALTH INPATIENT package                         #
#              __init__.py: Package declaration file                    #
#########################################################################
from trytond.pool import Pool
from . import health_inpatient
from . import wizard
from . import sequences
from . import health


def register():
    Pool.register(
        health.PatientProcedure,
        health_inpatient.DietTherapeutic,
        health_inpatient.InpatientRegistration,
        health_inpatient.BedTransfer,
        health_inpatient.Appointment,
        health_inpatient.PatientEvaluation,
        health_inpatient.ECG,
        health_inpatient.PatientData,
        health_inpatient.InpatientMedication,
        health_inpatient.InpatientMedicationAdminTimes,
        health_inpatient.InpatientMedicationLog,
        health_inpatient.InpatientDiet,
        wizard.wizard_health_inpatient.CreateBedTransferInit,
        health_inpatient.InpatientMeal,
        health_inpatient.InpatientMealOrder,
        health_inpatient.InpatientMealOrderItem,
        health_inpatient.PatientRounding,
        health_inpatient.RoundingProcedure,
        sequences.GnuHealthSequences,
        sequences.InpatientRegistrationSequence,
        sequences.InpatientMealOrderSequence,
        sequences.PatientRoundingSequence,
        module='health_inpatient', type_='model')

    Pool.register(
        wizard.wizard_health_inpatient.CreateBedTransfer,
        wizard.wizard_inpatient_evaluation.CreateInpatientEvaluation,
        module='health_inpatient', type_='wizard')
