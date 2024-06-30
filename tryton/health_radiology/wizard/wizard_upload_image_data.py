# SPDX-FileCopyrightText:  2024 - Wei Zhao <wei.zhao@uclouvain.be>
# SPDX-License-Identifier: GPL-3.0-or-later

from pyorthanc import Orthanc
import logging
from trytond.model import ModelView, fields
from trytond.wizard import Wizard, StateView, StateTransition, Button
from trytond.exceptions import UserError
from trytond.pool import Pool
from trytond.i18n import gettext

from io import BytesIO

__all__ = ['UploadImageDataStart', 'UploadImageData']

logger = logging.getLogger(__name__)

#
# Start upload image data view
#
class UploadImageDataStart(ModelView):
    "Upload Image Data Start"
    __name__ = "gnuhealth.imaging.uploadImageData.start"
    
    # The image data needs to be uploaded to the orthanc server.
    dataToUpload = fields.Binary("File to upload", required=True)
    # The target orthanc server where the image data will be saved
    serverConfig = fields.Many2One('gnuhealth.orthanc.configServer', 'Server', select=True, help='Orthanc server', required=True) 

#
# Uploading of image data 
#
class UploadImageData(Wizard):
    'Upload Image Data'
    __name__ = 'gnuhealth.imaging.uploadImageData'
    

    start = StateView('gnuhealth.imaging.uploadImageData.start',
                      'health_radiology.upload_image_data_start_form',
                      [Button('Cancel', 'end', 'tryton-cancel'),
                       Button('Upload Image Data', 'upload', 'tryton-ok', validate = True)])
    upload = StateTransition()
    
    def upload_imageData(self, dataToUpload, serverConfig):
        """
        A function to upload image data to the selected server.

        Parameters:
            dataToUpload: The byte data of multiple dicom files.
            serverConfig: The configuration for the server.

        Raises:
            UserError: If an exception is encountered during the upload process.
        """
        # dataToUpload contains the byte data of multiple dicom files.
        # The format is:
        #   1. the bytes 'M', 'U', 'L', 'T' (ASCII 77,85,76,84)
        #   2. 8 bytes containing the length of the file (Little Endian)
        #   3. the data of the file
        #   4. repeat steps 2 and 3 for next file
        try:          
            if dataToUpload[0]==77 and dataToUpload[1]==85 and dataToUpload[2]==76 and dataToUpload[3]==84:
                pos = 4
                while pos<len(dataToUpload):
                    # get length of file from data
                    dataLength = 0
                    for i in range(0,8):
                        dataLength = dataToUpload[pos+7-i] + dataLength*256
                    pos = pos + 8
                    # get content of file from data
                    data = BytesIO(dataToUpload[pos : pos+dataLength])
                    pos = pos + dataLength
                    # send file to Orthanc
                    client = Orthanc(url=serverConfig.domain, username=serverConfig.user, password=serverConfig.password, timeout=600)
                    client.post_instances(data.getvalue())
            else:
                data = BytesIO(dataToUpload[4:])
                client = Orthanc(url=serverConfig.domain, username=serverConfig.user, password=serverConfig.password, timeout=600)
                client.post_instances(data.getvalue())
        except Exception as exception:
            logger.error('Upload dicom files: %s', exception, exc_info=True)
            raise UserError(str(exception))
                          
    def transition_upload(self):
        """
        Transitions the upload process by uploading the image data specified in `self.start.dataToUpload` to the server specified in `self.start.serverConfig`. 
        After the upload is complete, it updates the imaging studies using the `get_new_studies()` method from the `gnuhealth.imaging.imagingStudy` pool.
        
        Returns:
            str: The string 'end' indicating the end of the upload process.
        """
        self.upload_imageData(self.start.dataToUpload, self.start.serverConfig)
        Pool().get('gnuhealth.imaging.imagingStudy').get_new_studies()
        return 'end' 
    
    def end(self):
        return 'reload'