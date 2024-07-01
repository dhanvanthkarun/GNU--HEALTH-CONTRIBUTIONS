# SPDX-FileCopyrightText:  2024 - Wei Zhao <wei.zhao@uclouvain.be>
# SPDX-License-Identifier: GPL-3.0-or-later


from . import wizard_full_synchronize  # noqa: F401
from . import wizard_get_new_studies  # noqa: F401
from . import wizard_upload_image_data  # noqa: F401
from . import wizard_orthanc_config  # noqa: F401

fullSync = wizard_full_synchronize.FullSynchronizeStart()
getNewStudies = wizard_get_new_studies.GetNewStudiesStart()
uploadImage = wizard_upload_image_data.UploadImageDataStart()
config = wizard_orthanc_config.AddOrthancInitData()
