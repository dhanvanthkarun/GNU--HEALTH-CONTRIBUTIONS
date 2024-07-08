# SPDX-FileCopyrightText:  2024 - Wei Zhao <wei.zhao@uclouvain.be>
# SPDX-License-Identifier: GPL-3.0-or-later

from trytond.model import ModelView
from trytond.wizard import Wizard, StateView, StateTransition, Button
from trytond.pool import Pool
import logging

__all__ = ['get_new_studies_start', 'get_new_studies']

logger = logging.getLogger(__name__)


class get_new_studies_start(ModelView):
    """
    Get New Studies Start
    """
    __name__ = "gnuhealth.radiology.get_new_studies.start"

#
# This class is responsible for retrieving
# all saved studies from the Orthanc server.


class get_new_studies(Wizard):
    "Get New Studies"
    __name__ = 'gnuhealth.radiology.get_new_studies'

    start = StateView(
        'gnuhealth.radiology.get_new_studies.start',
        'health_radiology.get_new_studies_start_form',
        [Button("Cancel", 'end', 'tryton-cancel'),
         Button("Start", 'update', 'tryton-ok'),
         ])
    update = StateTransition()

    def transition_update(self):
        """
        Get new studies and return 'end'.
        """
        Pool().get('gnuhealth.radiology.study').get_new_studies()
        return 'end'

    def end(self):
        """
        Method to signal the end of the process and return the string 'reload'.
        """
        return 'reload'
