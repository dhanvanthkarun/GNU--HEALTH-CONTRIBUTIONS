# SPDX-FileCopyrightText:  2024 - Wei Zhao <wei.zhao@uclouvain.be>
# SPDX-License-Identifier: GPL-3.0-or-later
#
#########################################################################
#   Hospital Management Information System (HMIS) component of the      #
#                       GNU Health project                              #
#                   https://www.gnuhealth.org                           #
#########################################################################
#                     HEALTH IMAGING ORTHANC package                          #
#                  health_orthanc_configuration.py
#########################################################################


"""
The Configuration of Orthanc DICOM Server.
"""

from trytond.model import ModelView, ModelSQL, fields, Unique
from pyorthanc import Orthanc
from urllib.parse import urljoin
from requests.exceptions import HTTPError, RequestException
from trytond.exceptions import UserError
from trytond.pool import Pool
import logging

__all__ = ['ServerConfig']

logger = logging.getLogger(__name__)


class ServerConfig(ModelSQL, ModelView):
    """
    Orthanc Server Config

    This class is used to connect to an Orthanc DICOM server and
    to check if a connection to the corresponding domain can be established.
    """
    __name__ = "gnuhealth.orthanc.config"
    _rec_name = "label"

    label = fields.Char(
        "Label", required=True,
        readonly=True,
        help="Label for server (eg., remote)")

    domain = fields.Char(
        "URL",
        required=True,
        readonly=True,
        help="The full URL of the Orthanc server")

    proxy_domain = fields.Char(
        "Proxy URL",
        required=False,
        readonly=True,
        help="The proxy URL of the Orthanc server")

    link_base_url = fields.Function(
        fields.Char(
            "Link Base URL",
            help="Base URL for links"),
        "get_link_base_url")

    user = fields.Char(
        "Username",
        required=True,
        help="Username for Orthanc REST server")

    password = fields.Char(
        "Password",
        required=True,
        help="Password for Orthanc REST server")

    validated = fields.Boolean(
        "Validated",
        help="Whether the server details have "
        "been successfully checked")

    link = fields.Function(
        fields.Char(
            "Link",
            help="Link to Orthanc Explorer"),
        "get_link")

    last_changed_index = fields.Integer(
        "Last Changed Index",
        readonly=True,
        help="Index of last change")

    @classmethod
    def default_last_changed_index(cls):
        """
        Class method to return the default last changed index.
        """
        return -1

    def get_link_base_url(self, name):
        """
        Get the base URL for links shown in the client
        """
        url = self.proxy_domain
        if url is None or url.strip() == "":
            url = self.domain
        return "".join([url.strip().rstrip("/"), "/"])

    def get_link(self, name):
        """
        Get the full explorer link
        """
        # return urljoin(self.link_base_url, "app/explorer.html")
        return urljoin(self.link_base_url, "")

    @classmethod
    def __setup__(cls):
        """
        Set up the ServerConfig class for database access.

        This method is a class method that initializes various properties
        and constraints of the ServerConfig model. It sets up a SQL
        constraint to ensure that the ``label`` coulmn is unique.
        """
        super().__setup__()
        t = cls.__table__()
        cls._buttons.update({
            'remove_config_server': {}
        })

        cls._sql_constraints = [
            ("label_unique", Unique(t, t.label),
             "The label must be unique."),
            ("domain_unique", Unique(t, t.domain),
             "The domain must be unique."),
        ]

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
            client = Orthanc(
                url=domain, username=user, password=password)
            client.get_changes({'last': 1})
        except ConnectionError:
            logger.exception(
                "No connection to the server can be established."
                "Check connectivity and port."
            )
            return False
        except HTTPError as err:
            status_code = err.response.status_code
            if status_code in ServerConfig.http_error_messages:
                error_message = (
                    ServerConfig.http_error_messages[status_code] +
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
        except BaseException:
            logger.exception(
                "Other error for <%s> occurred", domain)
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

    @classmethod
    @ModelView.button
    def remove_config_server(cls, records):
        Study = Pool().get("gnuhealth.imaging_orthanc.study")

        # check which configurations we can delete
        failed_domains = []
        for config in records:
            # check if there are studies with same domain as this config
            studies = Study.search([("server", "=", config.domain)])
            if len(studies) > 0:
                failed_domains.append(config.domain)
            else:
                cls.delete([config])

        if len(failed_domains) > 0:
            raise UserError(
                ("Cannot remove the following servers "
                 "because there are studies from them: {}").format(
                     ", ".join(failed_domains)))
        return "reload"
