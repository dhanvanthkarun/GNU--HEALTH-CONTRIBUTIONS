# SPDX-FileCopyrightText: 2019-2022 Chris Zimmerman <chris@teffalump.com>
# SPDX-FileCopyrightText: 2021-2024 Luis Falcón <falcon@gnuhealth.org>
# SPDX-FileCopyrightText: 2021-2024 GNU Solidario <health@gnusolidario.org>
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

"""
Initialization module for the ``health_orthanc`` module.

This module registers the necessary classes and methods of the
``health_orthanc`` module and its wizard in the Tryton pool.
This allows other modules to access the functionalities provided by
the ``health_orthanc`` module.
"""

from trytond.pool import Pool
from . import health_orthanc
from . import health_orthanc_configuration
from . import wizard


def register():
    Pool.register(
        health_orthanc.View,
        health_orthanc.Patient,
        health_orthanc.TestResult,
        health_orthanc.PatientOrthancStudy,
        health_orthanc.StudySeries,
        health_orthanc.SeriesInstances,
        health_orthanc_configuration.ServerConfig,
        wizard.wizard_upload_image_data.UploadImageDataStart,
        wizard.wizard_get_new_studies.GetNewStudiesStart,
        wizard.wizard_full_synchronize.FullSynchronizeStart,
        wizard.wizard_orthanc_config.AddOrthancInitData,
        # DEPRECATED, Used to migrate date.
        health_orthanc.OrthancPatientDEPRECATED,
        health_orthanc.OrthancStudyDEPRECATED,
        module="health_orthanc",
        type_="model",
    )

    Pool.register(
        wizard.wizard_full_synchronize.FullSynchronize,
        wizard.wizard_get_new_studies.GetNewStudies,
        wizard.wizard_upload_image_data.UploadImageData,
        wizard.wizard_orthanc_config.ConnectNewOrthancServer,
        module='health_orthanc', type_='wizard'
    )
