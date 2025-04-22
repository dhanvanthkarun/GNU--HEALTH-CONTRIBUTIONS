# SPDX-FileCopyrightText:  2024 - Wei Zhao <wei.zhao@uclouvain.be>
# SPDX-License-Identifier: GPL-3.0-or-later

from pyorthanc import Orthanc
import logging
from trytond.model import ModelView, fields
from trytond.wizard import Wizard, StateView, StateTransition, Button
from trytond.exceptions import UserError
from trytond.pool import Pool

from io import BytesIO

__all__ = ['UploadImageDataStart', 'UploadImageData']

logger = logging.getLogger(__name__)

#
# Start upload image data view
#


class UploadImageDataStart(ModelView):
    "Upload Image Data Start"
    __name__ = "gnuhealth.imaging_orthanc.upload_image_data.start"
    # The image data needs to be uploaded to the orthanc server.
    data_to_upload = fields.Binary("File to upload", required=True)
    # The target orthanc server where the image data will be saved
    server_config = fields.Many2One(
        'gnuhealth.orthanc.config',
        'Server',
        help='Orthanc server',
        required=True)

#
# Uploading of image data
#


class UploadImageData(Wizard):
    'Upload Image Data'
    __name__ = 'gnuhealth.imaging_orthanc.upload_image_data'
    start = StateView(
        'gnuhealth.imaging_orthanc.upload_image_data.start',
        'health_orthanc.upload_image_data_start_form',
        [Button('Cancel', 'end', 'tryton-cancel'),
         Button('Upload Image Data',
                'upload', 'tryton-ok',
                validate=True)])
    upload = StateTransition()

    def upload_image_data(self, data_to_upload, server_config):
        # A function to upload image data to the selected server.
        # data_to_upload contains the byte data of multiple dicom files.
        # The format is:
        # 1.the bytes 'M', 'U', 'L', 'T' (ASCII 77,85,76,84)
        # 2.8 bytes containing the length of the file (Little Endian)
        # 3.the data of the file
        # 4.repeat steps 2 and 3 for next file
        try:
            if (data_to_upload[0] == 77
                and data_to_upload[1] == 85
                and data_to_upload[2] == 76
                    and data_to_upload[3] == 84):
                pos = 4
                while pos < len(data_to_upload):
                    # get length of file from data
                    data_length = 0

                    for i in range(0, 8):
                        data_length = (
                            data_to_upload[pos + 7 - i]
                            + data_length
                            * 256)

                    pos = pos + 8
                    # get content of file from data
                    data = BytesIO(data_to_upload[pos: pos + data_length])
                    pos = pos + data_length
                    # send file to Orthanc
                    client = Orthanc(
                        url=server_config.domain,
                        username=server_config.user,
                        password=server_config.password,
                        timeout=600)
                    client.post_instances(data.getvalue())
            else:
                data = BytesIO(data_to_upload[4:])
                client = Orthanc(
                    url=server_config.domain,
                    username=server_config.user,
                    password=server_config.password,
                    timeout=600)
                client.post_instances(data.getvalue())
        except Exception as exception:
            logger.error('Upload dicom files: %s', exception, exc_info=True)
            raise UserError(str(exception))

    def transition_upload(self):
        # Transitions the upload process by uploading the image data specified
        # in the start view

        self.upload_image_data(
            self.start.data_to_upload,
            self.start.server_config)  # noqa	E501

        Pool().get('gnuhealth.imaging_orthanc.study').get_new_studies()
        return 'end'

    def end(self):
        return 'reload'
