# SPDX-FileCopyrightText: 2008-2025 Luis Falcón <falcon@gnuhealth.org>
# SPDX-FileCopyrightText: 2011-2025 GNU Solidario <health@gnusolidario.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#########################################################################
#   Hospital Management Information System (HMIS) component of the      #
#                       GNU Health project                              #
#                   https://www.gnuhealth.org                           #
#########################################################################
#                           HEALTH package                              #
#                __init__.py: Wizard declaration file                   #
#########################################################################

from . import wizard_appointment_evaluation
from . import wizard_check_immunization_status
from . import wizard_update_patient_disease_info


__all__ = ['wizard_appointment_evaluation',
           'wizard_check_immunization_status',
           'wizard_update_patient_disease_info']
