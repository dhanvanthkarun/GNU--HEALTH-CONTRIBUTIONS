# SPDX-FileCopyrightText: 2019-2022 Chris Zimmerman <chris@teffalump.com>
# SPDX-FileCopyrightText: 2021-2024 Luis Falcón <falcon@gnuhealth.org>
# SPDX-FileCopyrightText: 2021-2024 GNU Solidario <health@gnusolidario.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from trytond.model import ModelView, fields
from trytond.wizard import Wizard, StateTransition, StateView, Button
from trytond.pool import Pool
from requests.exceptions import HTTPError
from pyorthanc import Orthanc
import logging

logger = logging.getLogger(__name__)

__all__ = ["AddOrthancInitData", "AddOrthancStatus", "ConnectNewOrthancServer"]


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

class AddOrthancStatus(ModelView):
    """Display status"""

    __name__ = "gnuhealth.orthanc.add.status"

    status = fields.Text("status", help="Information")
    
class ConnectNewOrthancServer(Wizard):
    "Connect new Orthanc server"
    __name__ = "gnuhealth.orthanc.wizard.newConnect"
    
    start = StateView(
        "gnuhealth.orthanc.add.initData",
        "health_orthanc_configuration.view_orthanc_add_initData",
        [
            Button("Cancel", "end", "tryton-cancel"),
            Button("Begin", "connect", "tryton-ok", default=True),
        ]
    )
    
    connect = StateTransition()
    
    status = StateView(
        "gnuhealth.orthanc.add.status",
        "health_orthanc_configuration.view_orthanc_add_status",
        [Button("Close", "end", "tryton-close")],
        )
    
    def transition_connect(self):
        """
        A function that connects to a server using provided credentials. 
        It handles different exceptions such as HTTPError with specific error codes. 
        If successful, it creates a new server entry and saves it. 
        Finally, it logs the success or failure of the connection attempt. 
        Returns 'status' after completion.
        """
        try:
            pool = Pool()
            Config = pool.get("gnuhealth.orthanc.configServer")
            client = Orthanc(url=self.start.domain, username=self.start.user, password=self.start.password)
        except HTTPError as err:
            if err.response.status_code == 401:
                self.status.status = "Invalid credentials provided"
                logger.exception("Invalid credentials provided")
            else:
                self.status.status = "Invalid domain provided"
                logger.exception("Request returned error status code")
        except:
            self.status.status = "Invalid domain provided"
            logger.exception("Other error occurred")
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
            self.status.status = "Successfully added and synced <{}>".format(
                server.label
            )
            logger.info(
                "<{} with domain {} > has connected.".format( server.label, server.domain))
        finally:
            return 'status'
        
    def default_status(self, fields):
        """
        Generates a default status dictionary based on the provided fields.

        Args:
            fields (dict): A dictionary containing the fields for generating the default status.

        Returns:
            dict: A dictionary containing the default status with the key "status" mapped to the value of self.status.status.
        """
        return {"status": self.status.status}