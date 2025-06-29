# SPDX-FileCopyrightText:  2024 - Wei Zhao <wei.zhao@uclouvain.be>
# SPDX-License-Identifier: GPL-3.0-or-later


from trytond.model import ModelView
from trytond.wizard import Wizard, StateView, StateTransition, Button
from trytond.pool import Pool
import logging

__all__ = ['FullSynchronizeStart', 'FullSynchronize']

logger = logging.getLogger(__name__)


class FullSynchronizeStart(ModelView):
    """
    Full Synchronize studies Start
    """
    __name__ = "gnuhealth.imaging_orthanc.full_synchronize.start"

#
# This class is responsible for retrieving all
# saved studies from the Orthanc server.


class FullSynchronize(Wizard):
    "Full Synchronize Studies"
    __name__ = 'gnuhealth.imaging_orthanc.full_synchronize'

    start = StateView(
        'gnuhealth.imaging_orthanc.full_synchronize.start',
        'health_orthanc.full_synchronize_start_form', [
            Button("Cancel", 'end', 'tryton-cancel'),
            Button("Synchronize", 'synchronize', 'tryton-ok'),
        ])
    synchronize = StateTransition()

    def transition_synchronize(self):
        """
        Full Synchronize studies and return 'end'.
        """
        Pool().get('gnuhealth.imaging_orthanc.study').full_synchronize()
        return 'end'

    def end(self):
        """
        Method to signal the end of the process and return the string 'reload'.
        """
        return 'reload'
