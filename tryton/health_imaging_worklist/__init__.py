# SPDX-FileCopyrightText: 2019-2022 Chris Zimmerman <chris@teffalump.com>
# SPDX-FileCopyrightText: 2021-2024 Luis Falcón <falcon@gnuhealth.org>
# SPDX-FileCopyrightText: 2021-2024 GNU Solidario <health@gnusolidario.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#########################################################################
#   Hospital Management Information System (HMIS) component of the      #
#                       GNU Health project                              #
#                   https://www.gnuhealth.org                           #
#########################################################################
#                       HEALTH IMAGING WORKLIST package                 #
#                  __init__.py: Package declaration file                #
#########################################################################

"""
Initialization module for the ``health_imaging_worklist`` module.

This module registers the necessary classes and methods of the
``health_imaging_worklist`` module and its wizard in the Tryton pool.
This allows other modules to access the functionalities provided by
the ``health_imaging_worklist`` module.
"""

from trytond.pool import Pool
from . import health_imaging_worklist


def register():
    Pool.register(
        health_imaging_worklist.WorklistTemplate,
        health_imaging_worklist.ImagingTestRequest,
        health_imaging_worklist.ImagingTest,
        health_imaging_worklist.TestResult,
        module="health_imaging_worklist",
        type_="model",
    )
