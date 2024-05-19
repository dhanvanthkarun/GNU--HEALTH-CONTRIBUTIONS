# SPDX-FileCopyrightText: 2019-2022 Chris Zimmerman <chris@teffalump.com>
# SPDX-FileCopyrightText: 2021-2024 Luis Falcón <falcon@gnuhealth.org>
# SPDX-FileCopyrightText: 2021-2024 GNU Solidario <health@gnusolidario.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from trytond.pool import Pool
from . import wizard
from . import health_orthanc_configuration


def register():
    """
    Register various components related to OrthancServerConfig and ConnectNewOrthancServer.
    """
    Pool.register(
        health_orthanc_configuration.OrthancServerConfig,
        wizard.wizard_orthanc_config.AddOrthancInitData,
        module='health_orthanc_configuration', type_='model'
    )
    Pool.register(
        wizard.wizard_orthanc_config.ConnectNewOrthancServer,
        module='health_orthanc_configuration', type_='wizard'
    )
