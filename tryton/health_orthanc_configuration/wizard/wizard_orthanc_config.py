# SPDX-FileCopyrightText: 2019-2022 Chris Zimmerman <chris@teffalump.com>
# SPDX-FileCopyrightText: 2021-2024 Luis Falcón <falcon@gnuhealth.org>
# SPDX-FileCopyrightText: 2021-2024 GNU Solidario <health@gnusolidario.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from trytond.model import ModelView, fields
from trytond.wizard import Wizard, StateTransition, StateView, Button
from trytond.pool import Pool
from trytond.exceptions import UserError
from requests.exceptions import HTTPError
from httpx import ConnectError
from pyorthanc import Orthanc
import logging

logger = logging.getLogger(__name__)

__all__ = ["AddOrthancInitData", "ConnectNewOrthancServer"]


class AddOrthancInitData(ModelView):
    """Init data for Orthanc connection"""

    __name__ = "gnuhealth.orthanc.add.initData"

    label = fields.Char(
        "Label", required=True,
        help="The label of the Orthanc server. Must be unique"
    )
    domain = fields.Char(
        "URL", required=True, help="The full URL of the Orthanc server. Must be unique"
    )
    user = fields.Char(
        "Username", required=True, help="Username for Orthanc REST server"
    )
    password = fields.Char(
        "Password", required=True, help="Password for Orthanc REST server"
    )
    
class ConnectNewOrthancServer(Wizard):
    "Connect new Orthanc server"
    __name__ = "gnuhealth.orthanc.wizard.newConnect"
    
    start = StateView(
        "gnuhealth.orthanc.add.initData",
        "health_orthanc_configuration.view_orthanc_add_initData",
        [
            Button("Cancel", "end", "tryton-cancel"),
            Button("Connect", "connect", "tryton-ok", default=True),
        ]
    )
    
    connect = StateTransition()
    
    def transition_connect(self):
        pool = Pool()
        Config = pool.get("gnuhealth.orthanc.configServer")
        
        # check if domain already exists
        if len(Config.search([["label", "=", self.start.label]])) > 0 or len(Config.search([["domain", "=", self.start.domain]])) > 0:
            raise UserError("There is already a server configuration with the same label or URL")
        else:    
            try:
                client = Orthanc(url=self.start.domain, username=self.start.user, password=self.start.password)
                # check if connection works
                client.get_changes({"limit": 1})
            except ConnectError as err:
                raise UserError("Cannot connect to the specified Orthanc server. Is the URL correct?")
            except Exception as err:
                logger.error(type(err))
                raise UserError(str(err))
            else:
                new_server = {
                    "label": self.start.label,
                    "domain": self.start.domain,
                    "user": self.start.user,
                    "password": self.start.password,
                }
                server, = Config.create([new_server])
                server.validated = True
                Config.save([server])
        return 'end'
        
    def end(self):
        return 'reload'