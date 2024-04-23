# SPDX-FileCopyrightText: 2019-2022 Chris Zimmerman <chris@teffalump.com>
# SPDX-FileCopyrightText: 2021-2024 Luis Falcón <falcon@gnuhealth.org>
# SPDX-FileCopyrightText: 2024 Patryk Rosik <p.rosik@stud.uni-hannover.de>
# SPDX-FileCopyrightText: 2024 Wei Zhao <wei.zhao@uclouvain.be>
# SPDX-FileCopyrightText: 2021-2024 GNU Solidario <health@gnusolidario.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#########################################################################
#   Hospital Management Information System (HMIS) component of the      #
#                       GNU Health project                              #
#                   https://www.gnuhealth.org                           #
#########################################################################
#              HEALTH ORTHANC Configuration package                     #
#              health_orthanc_configuration.py: configuration module    #
#########################################################################


"""
Configuration module of the Orthanc DICOM Server integration.
This module provides the configuration to connect Orthanc Server to the GNU Health HMIS. 

"""

from trytond.model import ModelView, ModelSQL, fields, Unique
from pyorthanc import Orthanc
from urllib.parse import urljoin
from requests.exceptions import HTTPError, RequestException

import logging

__all__ = ['OrthancServerConfig']

logger = logging.getLogger(__name__)

class OrthancServerConfig(ModelSQL, ModelView):
    """Orthanc server details"""

    """
    Orthanc server details.

    This class is used to connect to an Orthanc DICOM server and  
    to check if a connection to the corresponding domain can be established.

    :param ModelSQL: Inherit from the Tryton ModelSQL class for SQL
                      database operations.
    :type ModelSQL: class: ``trytond.model.ModelSQL``

    :param ModelView: Inherit from the Tryton ModelView class
                      for user interface operations.
    :type ModelView: class: ``trytond.model.ModelView``

    :var __name__: The unique name ``gnuhealth.orthanc.configServer`` of the model.
    :vartype __name__: str

    :var _rec_name: The name ``label`` of the field used as name of records.
    :vartype _rec_name: str

    :var label: Label for the server that is displayed to the user. Required.
    :vartype label: class: ``trytond.model.fields.Char``

    :var domain: The full URL for the Orthanc DICOM server. Required.
    :vartype domain: class: ``trytond.model.fields.Char``

    :var user: Username of an authorized user for the Orthanc DICOM
        Server. Required.
    :vartype user: class: ``trytond.model.fields.Char``

    :var password: Password of an authorized user with corresponding name
        for the Orthanc DICOM Server. Required.
    :vartype password: class: ``trytond.model.fields.Char``
    
    """
    
    __name__ = "gnuhealth.orthanc.configServer"
    _rec_name = "label"

    label = fields.Char(
        "Label", required=True, help="Label for server (eg., remote1)")

    domain = fields.Char(
        "URL", required=True, help="The full URL of the Orthanc server")

    user = fields.Char(
        "Username", required=True, help="Username for Orthanc REST server")

    password = fields.Char(
        "Password", required=True, help="Password for Orthanc REST server")

    validated = fields.Boolean(
        "Validated", help="Whether the server details have been "
        "successfully checked")
    
    link = fields.Function(
        fields.Char(
            "URL",
            help="Link to server in Orthanc Explorer"), "get_link")
    
    lastChangedIndex = fields.Integer("LastChangedIndex", readonly=True, help="Index of last change")

    @classmethod
    def default_lastChangedIndex(cls):
        """
        Class method to return the default last changed index.
        """
        return -1

    def get_link(self, name):
        """
        Get the full link by joining the domain and the additional path provided.

        Parameters:
            name (str): The additional path to be added to the domain.

        Returns:
            str: The full URL after joining the domain and the additional path.
        """
        pre = "".join([self.domain.rstrip("/"), "/"])
        add = "app/explorer.html"
        return urljoin(pre, add)

    @classmethod
    def __setup__(cls):
        """
        Set up the OrthancServerConfig class for database access.

        This method is a class method that initializes various properties
        and constraints of the OrthancServerConfig model. It sets up a SQL
        constraint to ensure that the ``label`` coulmn is unique.
        """
        super().__setup__()
        t = cls.__table__()
        cls._sql_constraints = [
            ("label_unique", Unique(t, t.label), "The label must be unique."),
            ("domain_unique", Unique(t, t.domain), "The domain must be unique."),
        ]
        # cls._buttons.update({"do_sync": {}})


    @staticmethod
    def quick_check(domain, user, password):
        """
        Check if the server details are correct.

        :param domain: The domain name or IP address of the Orthanc
                       DICOM server.
        :type domain: str

        :param user: The username for authentication.
        :type user: str

        :param password: The password for authentication.
        :type password: str

        :return: ``True`` if the server details are valid,
                 ``False`` otherwise.
        :rtype: bool
        """
        
        try:
            client = Orthanc(url=domain, username=user, password=password)
            client.get_changes(last=True)
        except ConnectionError:
            logger.exception(
                "No connection to the server can be established."
                "Check connectivity and port."
            )
            return False
        except HTTPError as err:
            status_code = err.response.status_code
            if status_code in OrthancServerConfig.http_error_messages:
                error_message = (
                    OrthancServerConfig.http_error_messages[status_code] +
                    f" {domain} not reacheable"
                )
                logger.exception(error_message)
            else:
                logger.exception("Unhandled HTTP error for <%s>", domain)
            return False
        except RequestException:
            logger.exception(
                "Unhandled request error for <%s> occurred", domain)
            return False
        return True

    @fields.depends("domain", "user", "password")
    def on_change_with_validated(self):
        """
        Update the ``validated`` field based on the current server details.

        :return: A boolean value indicating whether the update was
                 successful or not.
        :rtype: bool

        .. note:: This method follows the Tryton Syntax. The
                  ``@fields.depends`` decorates the method to indicate
                    that this field depends on other fields. In addition,
                    ``on_change_with_`` is appended before the field name
                    to indicate that the field should change depending on
                    the parameters after ``@fields.depends``.

        .. seealso:: React to user input and Add computed fields in Tryton
                     documentation.
        """

        return self.quick_check(self.domain, self.user, self.password)