# SPDX-FileCopyrightText: 2019-2022 Chris Zimmerman <chris@teffalump.com>
# SPDX-FileCopyrightText: 2021-2023 Luis Falcón <falcon@gnuhealth.org>
# SPDX-FileCopyrightText: 2021-2023 GNU Solidario <health@gnusolidario.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#########################################################################
#   Hospital Management Information System (HMIS) component of the      #
#                       GNU Health project                              #
#                   https://www.gnuhealth.org                           #
#########################################################################
#                       HEALTH ORTHANC package                          #
#                  __init__.py: Package declaration file                #
#########################################################################

from trytond.pool import Pool
from . import health_orthanc
from . import wizard
from . import ir


def register():
    Pool.register(
        wizard.wizard.AddOrthancInit,
        wizard.wizard.AddOrthancResult,
        health_orthanc.OrthancServerConfig,
        health_orthanc.OrthancWorklistTemplate,
        health_orthanc.OrthancStudy,
        health_orthanc.OrthancPatient,
        health_orthanc.ImagingTestRequest,
        health_orthanc.ImagingTest,
        health_orthanc.TestResult,
        health_orthanc.Patient,
        ir.Cron,
        module="health_orthanc",
        type_="model",
    )
    Pool.register(
        wizard.wizard.FullSyncOrthanc, module="health_orthanc", type_="wizard")
