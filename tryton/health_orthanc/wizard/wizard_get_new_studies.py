# SPDX-FileCopyrightText:  2024 - Wei Zhao <wei.zhao@uclouvain.be>
# SPDX-License-Identifier: GPL-3.0-or-later

from trytond.model import ModelView
from trytond.wizard import Wizard, StateView, StateTransition, Button
from trytond.pool import Pool
import logging

__all__ = ['GetNewStudiesStart', 'GetNewStudies']

logger = logging.getLogger(__name__)


class GetNewStudiesStart(ModelView):
    """
    Get New Studies Start
    """
    __name__ = "gnuhealth.imaging_orthanc.get_new_studies.start"

#
# This class is responsible for retrieving
# all saved studies from the Orthanc server.


class GetNewStudies(Wizard):
    "Get New Studies"
    __name__ = 'gnuhealth.imaging_orthanc.get_new_studies'

    start = StateView(
        'gnuhealth.imaging_orthanc.get_new_studies.start',
        'health_orthanc.get_new_studies_start_form',
        [Button("Cancel", 'end', 'tryton-cancel'),
         Button("Start", 'update', 'tryton-ok'),
         ])
    update = StateTransition()

    def transition_update(self):
        """
        Get new studies and return 'end'.
        """
        Pool().get('gnuhealth.imaging_orthanc.study').get_new_studies()
        return 'end'

    def end(self):
        """
        Method to signal the end of the process and return the string 'reload'.
        """
        return 'reload'
