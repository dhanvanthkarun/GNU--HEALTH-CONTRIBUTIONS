# SPDX-FileCopyrightText: 2008-2025 Luis Falcón <falcon@gnuhealth.org>
# SPDX-FileCopyrightText: 2011-2025 GNU Solidario <health@gnusolidario.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#########################################################################
#   Hospital Management Information System (HMIS) component of the      #
#                       GNU Health project                              #
#                   https://www.gnuhealth.org                           #
#########################################################################
#                        HEALTH LAB package                             #
#              __init__.py: Package declaration file                    #
#########################################################################

from trytond.pool import Pool
from . import health_lab
from . import wizard
from . import sequences


def register():
    Pool.register(
        health_lab.PatientData,
        health_lab.TestType,
        health_lab.Lab,
        health_lab.GnuHealthLabTestUnits,
        health_lab.GnuHealthTestCritearea,
        health_lab.GnuHealthPatientLabTest,
        wizard.wizard_create_lab_test.CreateLabTestOrderInit,
        wizard.wizard_create_lab_test.RequestPatientLabTestStart,
        wizard.wizard_create_lab_test.RequestTest,
        health_lab.PatientHealthCondition,
        sequences.GnuHealthSequences,
        sequences.LabRequestSequence,
        sequences.LabTestSequence,
        module='health_lab', type_='model')

    Pool.register(
        wizard.wizard_create_lab_test.CreateLabTestOrder,
        wizard.wizard_create_lab_test.RequestPatientLabTest,
        module='health_lab', type_='wizard')
