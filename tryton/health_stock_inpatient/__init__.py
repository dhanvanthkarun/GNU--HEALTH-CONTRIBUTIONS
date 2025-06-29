# SPDX-FileCopyrightText: 2008-2025 Luis Falcón <falcon@gnuhealth.org>
# SPDX-FileCopyrightText: 2013 Sebastian Marro <smarro@thymbra.com>
# SPDX-FileCopyrightText: 2011-2025 GNU Solidario <health@gnusolidario.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#########################################################################
#   Hospital Management Information System (HMIS) component of the      #
#                       GNU Health project                              #
#                   https://www.gnuhealth.org                           #
#########################################################################
#                         HEALTH REPORTING package                      #
#                 __init__.py: Package declaration file                 #
#########################################################################

from trytond.pool import Pool
from . import health_stock_inpatient


def register():
    Pool.register(
        health_stock_inpatient.Move,
        health_stock_inpatient.PatientRounding,
        health_stock_inpatient.PatientRoundingMedicament,
        health_stock_inpatient.PatientRoundingMedicalSupply,
        module='health_stock_inpatient', type_='model')
