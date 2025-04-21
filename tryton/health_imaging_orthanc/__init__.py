# SPDX-FileCopyrightText:  2024 - Wei Zhao <wei.zhao@uclouvain.be>
# SPDX-License-Identifier: GPL-3.0-or-later
#
#########################################################################
#   Hospital Management Information System (HMIS) component of the      #
#                       GNU Health project                              #
#                   https://www.gnuhealth.org                           #
#########################################################################
#                   HEALTH_IMAGING_ORTHANC package                      #
#              __init__.py: Package declaration file                    #
#########################################################################


from trytond.pool import Pool
from . import health_imaging_orthanc
from . import health_imaging_orthanc_configuration
from . import wizard


def register():
    """
    Registers the models and wizards for the health_imaging_orthanc module.
    """
    Pool.register(
        health_imaging_orthanc.View,
        health_imaging_orthanc.TestResult,
        health_imaging_orthanc.PatientOrthancStudy,
        wizard.wizard_upload_image_data.UploadImageDataStart,
        wizard.wizard_get_new_studies.GetNewStudiesStart,
        wizard.wizard_full_synchronize.FullSynchronizeStart,
        wizard.wizard_orthanc_config.AddOrthancInitData,
        health_imaging_orthanc.StudySeries,
        health_imaging_orthanc.SeriesInstances,
        health_imaging_orthanc_configuration.ServerConfig,
        module='health_imaging_orthanc', type_='model'
    )
    Pool.register(
        wizard.wizard_full_synchronize.FullSynchronize,
        wizard.wizard_get_new_studies.GetNewStudies,
        wizard.wizard_upload_image_data.UploadImageData,
        wizard.wizard_orthanc_config.ConnectNewOrthancServer,
        module='health_imaging_orthanc', type_='wizard'
    )
