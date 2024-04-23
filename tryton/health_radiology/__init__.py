# SPDX-FileCopyrightText: 2008-2024 Luis Falcón <falcon@gnuhealth.org>
# SPDX-FileCopyrightText: 2011-2024 GNU Solidario <health@gnusolidario.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#########################################################################
#   Hospital Management Information System (HMIS) component of the      #
#                       GNU Health project                              #
#                   https://www.gnuhealth.org                           #
#########################################################################
#                        HEALTH RADIOLOGY package                         #
#              __init__.py: Package declaration file                    #
#########################################################################


from trytond.pool import Pool
from . import wizard
from . import health_radiology


def register():
    """
    Registers the models and wizards for the health_radiology module.

    This function registers the following models and wizards:
    - health_radiology.PatientData
    - health_radiology.PatientOrthancStudy
    - wizard.wizard_upload_image_data.UploadImageDataStart
    - wizard.wizard_get_new_studies.getNewStudies.Start,
    - health_radiology.ImagingStudySeries
    - health_radiology.ImagingSeriesInstances

    The models are registered with the 'health_radiology' module and the 'model' type.
    The wizards are registered with the 'health_radiology' module and the 'wizard' type.

    This function does not have any parameters.

    This function does not return any values.
    """
    Pool.register(
        health_radiology.View,
        health_radiology.PatientData,
        health_radiology.PatientOrthancStudy,
        wizard.wizard_upload_image_data.UploadImageDataStart,
        wizard.wizard_get_new_studies.GetNewStudiesStart,
        wizard.wizard_full_synchronize.FullSynchronizeStart,
        health_radiology.ImagingStudySeries,
        health_radiology.ImagingSeriesInstances,
        module='health_radiology', type_='model'
    )
    Pool.register(
        wizard.wizard_full_synchronize.FullSynchronize,
        wizard.wizard_get_new_studies.GetNewStudies,
        wizard.wizard_upload_image_data.UploadImageData,
        module='health_radiology', type_='wizard'
    )
