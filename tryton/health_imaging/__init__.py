# SPDX-FileCopyrightText: 2008-2025 Luis Falcón <falcon@gnuhealth.org>
# SPDX-FileCopyrightText: 2011-2025 GNU Solidario <health@gnusolidario.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#########################################################################
#   Hospital Management Information System (HMIS) component of the      #
#                       GNU Health project                              #
#                   https://www.gnuhealth.org                           #
#########################################################################
#                        HEALTH IMAGING package                         #
#              __init__.py: Package declaration file                    #
#########################################################################

from trytond.pool import Pool
from . import health_imaging
from . import wizard
from . import sequences


def register():
    Pool.register(
        health_imaging.ImagingTestType,
        health_imaging.ImagingTest,
        health_imaging.ImagingTestRequest,
        health_imaging.ImagingTestResult,
        wizard.wizard_health_imaging.RequestImagingTest,
        wizard.wizard_health_imaging.RequestPatientImagingTestStart,
        sequences.GnuHealthSequences,
        sequences.ImagingRequestSequence,
        sequences.ImagingTestSequence,
        module='health_imaging', type_='model')

    Pool.register(
        wizard.wizard_health_imaging.WizardGenerateResult,
        wizard.wizard_health_imaging.RequestPatientImagingTest,
        module='health_imaging', type_='wizard')
