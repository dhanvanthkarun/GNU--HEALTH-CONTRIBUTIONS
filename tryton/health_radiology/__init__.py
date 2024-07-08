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
        health_radiology.patient_data,
        health_radiology.patient_orthanc_study,
        wizard.wizard_upload_image_data.upload_image_data_start,
        wizard.wizard_get_new_studies.get_new_studies_start,
        wizard.wizard_full_synchronize.full_synchronize_start,
        wizard.wizard_orthanc_config.add_orthanc_init_data,
        health_radiology.study_series,
        health_radiology.series_instances,
        health_orthanc_configuration.server_config,
        module='health_radiology', type_='model'
    )
    Pool.register(
        wizard.wizard_full_synchronize.full_synchronize,
        wizard.wizard_get_new_studies.get_new_studies,
        wizard.wizard_upload_image_data.upload_image_data,
        wizard.wizard_orthanc_config.connect_new_orthanc_server,
        module='health_radiology', type_='wizard'
    )
