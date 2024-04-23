# Copyright (C) 2008-2024 Luis Falcon <lfalcon@gnuhealth.org>
# Copyright (C) 2013  Sebastián Marro <smarro@thymbra.com>
# SPDX-FileCopyrightText: 2008-2024 Luis Falcón <falcon@gnuhealth.org>
# SPDX-FileCopyrightText: 2011-2024 GNU Solidario <health@gnusolidario.org>
#
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
    __name__ = "gnuhealth.imaging.getNewStudies.start"

#
# This class is responsible for retrieving all saved studies from the Orthanc server.
#
class GetNewStudies(Wizard):
    "Get New Studies"
    __name__ = 'gnuhealth.imaging.getNewStudies'
        
    start = StateView(
        'gnuhealth.imaging.getNewStudies.start',
        'health_radiology.get_new_studies_start_form', [
            Button("Cancel", 'end', 'tryton-cancel'),
            Button("Start", 'update', 'tryton-ok'),
            ])
    update = StateTransition()    
    
    def transition_update(self):
        """
        Get new studies and return 'end'.
        """
        Pool().get('gnuhealth.imaging.imagingStudy').get_new_studies()
        return 'end'
    
    def end(self):
        """
        Method to signal the end of the process and return the string 'reload'.
        """
        return 'reload'