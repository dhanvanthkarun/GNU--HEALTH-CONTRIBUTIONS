# SPDX-FileCopyrightText: 2008-2025 Luis Falcón <falcon@gnuhealth.org>
# SPDX-FileCopyrightText: 2011-2025 GNU Solidario <health@gnusolidario.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#########################################################################
#   Hospital Management Information System (HMIS) component of the      #
#                       GNU Health project                              #
#                   https://www.gnuhealth.org                           #
#########################################################################
#                       HEALTH NURSING package                          #
#              __init__.py: Package declaration file                    #
#########################################################################

from trytond.pool import Pool
from . import health_nursing
from . import sequences
from . import health


def register():
    Pool.register(
        health.PatientProcedure,
        health_nursing.PatientAmbulatoryCare,
        health_nursing.AmbulatoryCareProcedure,
        sequences.GnuHealthSequences,
        sequences.AmbulatoryCareSequence,
        module='health_nursing', type_='model')
