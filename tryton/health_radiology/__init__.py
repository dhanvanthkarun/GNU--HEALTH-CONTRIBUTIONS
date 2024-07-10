# SPDX-FileCopyrightText:  2024 - Wei Zhao <wei.zhao@uclouvain.be>
# SPDX-License-Identifier: GPL-3.0-or-later
#
#########################################################################
#   Hospital Management Information System (HMIS) component of the      #
#                       GNU Health project                              #
#                   https://www.gnuhealth.org                           #
#########################################################################
#                        HEALTH RADIOLOGY package                         #
#              __init__.py: Package declaration file                    #
#########################################################################


from trytond.pool import Pool
from . import health_radiology
from . import health_orthanc_configuration
from . import wizard


def register():
    """
    Registers the models and wizards for the health_radiology module.
    """
    Pool.register(
        health_radiology.View,
        health_radiology.PatientData,
        health_radiology.TestResult,
        health_radiology.PatientOrthancStudy,
        wizard.wizard_upload_image_data.UploadImageDataStart,
        wizard.wizard_get_new_studies.GetNewStudiesStart,
        wizard.wizard_full_synchronize.FullSynchronizeStart,
        wizard.wizard_orthanc_config.AddOrthancInitData,
        health_radiology.StudySeries,
        health_radiology.SeriesInstances,
        health_orthanc_configuration.ServerConfig,
        module='health_radiology', type_='model'
    )
    Pool.register(
        wizard.wizard_full_synchronize.FullSynchronize,
        wizard.wizard_get_new_studies.GetNewStudies,
        wizard.wizard_upload_image_data.UploadImageData,
        wizard.wizard_orthanc_config.ConnectNewOrthancServer,
        module='health_radiology', type_='wizard'
    )
