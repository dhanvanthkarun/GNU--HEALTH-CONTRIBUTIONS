# SPDX-FileCopyrightText: 2008-2025 Luis Falcón <falcon@gnuhealth.org>
# SPDX-FileCopyrightText: 2011-2025 GNU Solidario <health@gnusolidario.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#########################################################################
#   Hospital Management Information System (HMIS) component of the      #
#                       GNU Health project                              #
#                   https://www.gnuhealth.org                           #
#########################################################################
#                     HEALTH SERVICES IMAGING package                   #
#                 __init__.py: Package declaration file                 #
#########################################################################

from trytond.pool import Pool
from . import health_services_imaging
from . import wizard


def register():
    Pool.register(
        health_services_imaging.ImagingTestRequest,
        wizard.wizard_health_services.RequestPatientImagingTestStart,
        module='health_services_imaging', type_='model')
    Pool.register(
        wizard.wizard_health_services.RequestPatientImagingTest,
        module='health_services_imaging', type_='wizard')
