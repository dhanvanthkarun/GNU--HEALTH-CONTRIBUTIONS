# SPDX-FileCopyrightText:  2024 - Wei Zhao <wei.zhao@uclouvain.be>
# SPDX-License-Identifier: GPL-3.0-or-later


from . import wizard_full_synchronize  # noqa: F401
from . import wizard_get_new_studies  # noqa: F401
from . import wizard_upload_image_data  # noqa: F401
from . import wizard_orthanc_config  # noqa: F401

full_sync = wizard_full_synchronize.full_synchronize_start()
get_new_studies = wizard_get_new_studies.get_new_studies_start()
upload_image = wizard_upload_image_data.upload_image_data_start()
config = wizard_orthanc_config.add_orthanc_init_data()
