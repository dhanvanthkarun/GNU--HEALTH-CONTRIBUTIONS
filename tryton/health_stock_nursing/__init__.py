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
#                         HEALTH STOCK NURSING package                  #
#                 __init__.py: Package declaration file                 #
#########################################################################

from trytond.pool import Pool
from . import health_stock_nursing


def register():
    Pool.register(
        health_stock_nursing.Move,
        health_stock_nursing.PatientAmbulatoryCare,
        health_stock_nursing.PatientAmbulatoryCareMedicament,
        health_stock_nursing.PatientAmbulatoryCareMedicalSupply,
        module='health_stock_nursing', type_='model')
