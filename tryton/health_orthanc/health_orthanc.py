# SPDX-FileCopyrightText: 2019-2022 Chris Zimmerman <chris@teffalump.com>
# SPDX-FileCopyrightText: 2021-2024 Luis Falcón <falcon@gnuhealth.org>
# SPDX-FileCopyrightText: 2023 Patryk Rosik <p.rosik@stud.uni-hannover.de>
# SPDX-FileCopyrightText: 2023 Feng Shu <tumashu@163.com>
# SPDX-FileCopyrightText: 2021-2024 GNU Solidario <health@gnusolidario.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#########################################################################
#   Hospital Management Information System (HMIS) component of the      #
#                       GNU Health project                              #
#                   https://www.gnuhealth.org                           #
#########################################################################
#                         HEALTH ORTHANC package                        #
#                     health_orthanc.py: main module                    #
#########################################################################

"""
Core module of the Orthanc DICOM Server integration.

This module provides models for synchronization between an Orthanc DICOM
Server and the GNU Health HMIS. It provides methods to check when the
last synchronization took  place and makes them available to users via
appropriate GUI elements. Additionally,  there are methods to provide
hyperlinks to the corresponding studies and patients for
given Orthanc DICOM servers.
"""

from trytond.model import ModelView, ModelSQL, fields, Unique
from trytond.pool import Pool, PoolMeta
from datetime import datetime
from urllib.parse import urljoin
from lxml import etree


import logging

try:
    from trytond.modules.health_imaging_worklist.health_imaging_worklist \
        import gnuhealth_org_root
except ImportError:
    gnuhealth_org_root = None


__all__ = [
    "View",
    "OrthancPatient",
    "OrthancStudy",
    "Patient",
    "TestResult",
]

logger = logging.getLogger(__name__)


#
#  Adding widget "dicombinary" to the server
#

class View(metaclass=PoolMeta):
    __name__ = 'ir.ui.view'

    @classmethod
    def get_rng(cls, type_):
        rng = super(View, cls).get_rng(type_)
        if type_ in ('form', 'list-form'):
            widgets = rng.xpath(
                '//ns:define/ns:optional/ns:attribute'
                '/ns:name[.="widget"]/following-sibling::ns:choice',
                namespaces={'ns': 'http://relaxng.org/ns/structure/1.0'})[0]
            subelem = etree.SubElement(
                widgets, '{http://relaxng.org/ns/structure/1.0}value')
            subelem.text = 'dicombinary'
        return rng


class OrthancPatient(ModelSQL, ModelView):
    """Orthanc patient information"""
    """
    Defines an Orthanc Patient.

    This class defines the ``OrthancPatient``. It provides methods to update
    existing patients or add new patients from the Orthanc DICOM server.
    Additionally, it allows to extract DICOM tags and automatically generates
    hyperlinks to the corresponding patients.

    :param ModelSQL: Inherit from the Tryton ModelSQL class for SQL
                     database operations.
    :type ModelSQL: class: ``trytond.model.ModelSQL``

    :param ModelView: Inherit from the Tryton ModelView class for user
                      interface operations.
    :type ModelView: class: ``trytond.model.ModelView``

    :var __name__: The unique name ``gnuhealth.orthanc.patient`` of the model.
    :vartype __name__: str

    :var patient: Local linked patient from Orthanc into GNU Health HMIS.
    :vartype patient: class: ``trytond.model.field.Many2One``

    :var name: Name of the patient. Read-only.
    :vartype name: class: ``trytond.model.field.Char``

    :var bd: Birth date of the patient. Read-only.
    :vartype bd: class: ``trytond.model.field.Date``

    :var ident: Unique ID for a patient based on the Patient ID DICOM Tag.
                Read-only.
    :vartype ident: class: ``trytond.model.field.Char``

    :var uuid: SHA-1 Hash of ``ident``. Read-only and Required.
    :vartype uuid: class: ``trytond.model.field.Char``

    :var studies: List of Orthanc studies directly related to the patient.
                  Read-only.
    :vartype studies: class: ``trytond.model.field.One2Many``

    :var server:  A field to specify the server. Required.
    :vartype server: class: ``trytond.model.field.Many2One``

    :var link: Link to the patient in the Orthanc Explorer.
    :vartype link: class: ``trytond.model.field.Char``
    """

    __name__ = "gnuhealth.orthanc.patient"

    patient = fields.Many2One(
        "gnuhealth.patient", "Patient", help="Local linked patient"
    )
    name = fields.Char("PatientName", readonly=True)
    bd = fields.Date("Birthdate", readonly=True)
    ident = fields.Char("PatientID", readonly=True)
    uuid = fields.Char("PatientUUID", readonly=True, required=True)
    studies = fields.One2Many(
        "gnuhealth.orthanc.study", "patient", "Studies", readonly=True
    )
    server = fields.Many2One(
        "gnuhealth.orthanc.config", "Server", readonly=True)
    link = fields.Function(
        fields.Char(
            "URL", help="Link to patient in Orthanc Explorer"), "get_link"
    )

    def get_link(self, name):
        """
        Return a link to the Orthanc patient with the specified uuid in
        the Orthanc explorer.

        :param name: Label of the patient to get the link for.
        :type name: str

        :return: URL to the Orthanc patient in the Orthanc Explorer.
        :rtype: str
        """

        pre = "".join([self.server.domain.rstrip("/"), "/"])
        add = "app/explorer.html#patient?uuid={}".format(self.uuid)
        return urljoin(pre, add)

    @classmethod
    def __setup__(cls):
        """
        Set up the ``OrthancPatient`` class for database access.

        This method is a class method that initializes various properties
        and constraints of the ``OrthancPatient`` model. It sets up a SQL
        constraint to ensure that the ``server`` and  ``uuid`` column
        are unique.
        """

        super().__setup__()
        t = cls.__table__()
        cls._sql_constraints = [
            (
                "uuid_unique",
                Unique(t, t.server, t.uuid),
                "UUID must be unique for a given server",
            )
        ]

    @staticmethod
    def get_info_from_dicom(patients):
        """
        Extract patient information from DICOM data for writing to database.

        :param patients: List of DICOM data for patients.
        :type patients: list

        :return: List of dictionaries with patient information.
        :rtype: list
        """

        data = []
        for patient in patients:
            try:
                bd = datetime.strptime(
                    patient["MainDicomTags"]["PatientBirthDate"], "%Y%m%d"
                ).date()

            except Exception:
                logger.exception(
                    "Invalid date format. Please provide the date in "
                    "the format %Y%m%d"
                )
                bd = None
            data.append(
                {
                    "name": patient.get("MainDicomTags").get("PatientName"),
                    "bd": bd,
                    "ident": patient.get("MainDicomTags").get("PatientID"),
                    "uuid": patient.get("ID"),
                }
            )
        return data

    @classmethod
    def update_patients(cls, patients, server):
        """
        Update patients with new information from DICOM files.

        :param patients: A list of patient data in DICOM format.
        :type patients: list

        :param server: The server to update the patients on.
        :type server: str
        """

        entries = cls.get_info_from_dicom(patients)
        updates = []
        for entry in entries:
            try:
                patient = cls.search(
                    [("uuid", "=", entry["uuid"]),
                     ("server", "=", server)], limit=1
                )[0]
                patient.party = entry["name"]
                patient.bd = entry["bd"]
                patient.ident = entry["ident"]
                # don't update unless no patient attached
                if not patient.patient:
                    try:
                        g_patient = Patient.search(
                            [("puid", "=", entry["ident"])], limit=1
                        )[0]
                        patient.patient = g_patient
                        logger.info(
                            "New Matching PUID found for {}".
                            format(entry["ident"])
                        )
                    except IndexError:
                        logger.warning(
                            "No patient from GNU Health HMIS attached")
                updates.append(patient)
                logger.info("Updating patient {}".format(entry["uuid"]))
            except IndexError:
                continue
                logger.warning("Unable to update patient {}".
                               format(entry["uuid"]))
        cls.save(updates)

    @classmethod
    def create_patients(cls, patients, server):
        """
        Create patients with information from DICOM files.

        :param patients: A list of patient data in DICOM format.
        :type patients: list

        :param server: The server to update the patients on.
        :type server: str
        """

        pool = Pool()
        Patient = pool.get("gnuhealth.patient")

        entries = cls.get_info_from_dicom(patients)
        for entry in entries:
            try:
                g_patient = Patient.search(
                    [("puid", "=", entry["ident"])], limit=1)[0]
                logger.info("Matching PUID found for {}".format(entry["uuid"]))
            except IndexError:
                g_patient = None
            entry["server"] = server
            entry["patient"] = g_patient
        cls.create(entries)


class OrthancStudy(ModelSQL, ModelView):
    """
    Defines an Orthanc Study.

    This class defines the ``OrthancStudy``. It provides methods to update
    existing studies or add new studies to the Orthanc DICOM server.
    Additionally, it allows to extract DICOM tags and automatically generates
    hyperlinks to the corresponding studies.

    :param ModelSQL: Inherit from the Tryton ModelSQL class for SQL
                     database operations.
    :type ModelSQL: class: ``trytond.model.ModelSQL``

    :param ModelView: Inherit from the Tryton ModelView class for user
                      interface operations.
    :type ModelView: class: ``trytond.model.ModelView``

    :var __name__: The unique name `gnuhealth.orthanc.study` of the model.
    :vartype __name__: str

    :var patient: Local patient of Orthanc conncted to a study. Read-only.
    :vartype patient: class: ``trytond.model.fields.Many2One``

    :var uuid: SHA-1 Hash of the PatientID tag (0010,0020) and their
               StudyInstanceUID tag
        (0020,000d). Read-only and Required.
    :vartype uuid: class: ``trytond.model.fields.Char``

    :var description: Description of the study conducted. Read-only.
    :vartype description: class: ``trytond.model.fields.Char``

    :var date: Date on which the study was conducted. Read-only.
    :vartype date: class: ``trytond.model.fields.Date``

    :var ident: ID of a study based on the Study ID DICOM Tag. Read-only.
    :vartype ident: class: ``trytond.model.fields.Char``

    :var institution: Institution at which the study was conducted. Read-only.
    :vartype institution: class: ``trytond.model.fields.Char``

    :var ref_phys: The referring physician. Read-only.
    :vartype ref_phys: class: ``trytond.model.fields.Char``

    :var req_phys: The requesting physician. Read-only.
    :vartype req_phys: class: ``trytond.model.fields.Char``

    :var server: Server on which the study is located. Read-only.
    :vartype server: class: ``trytond.model.fields.Many2One``

    :var ohif_viewer_link: Link to study in OHIF Viewer.
    :vartype link: class: ``trytond.model.fields.Char``

    :var stone_viewer_link: Link to study in Stone Viewer.
    :vartype link: class: ``trytond.model.fields.Char``

    :var orthanc_explorer_link: Link to study in Orthanc Explorer.
    :vartype link: class: ``trytond.model.fields.Char``

    :var imaging_test: Corresponding request from GNU Health HMIS.
    :vartype imaging_test: class: ``trytond.model.fields.Many2One``
    """

    __name__ = "gnuhealth.orthanc.study"

    patient = fields.Many2One(
        "gnuhealth.orthanc.patient", "Patient", readonly=True)

    uuid = fields.Char("UUID", readonly=True, required=True)
    description = fields.Char("Description", readonly=True)
    date = fields.Date("Date", readonly=True)
    ident = fields.Char("ID", readonly=True)
    instance_uid = fields.Char("InstanceUID", readonly=True)
    requested_procedure_id = fields.Char(
        "RequestedProcedureID", readonly=True
    )
    merge_id = fields.Char(
        "Merge ID", readonly=True,
        help="Test result merge id, with it help, "
        "gnuhealth test result and orthanc study can be merged."
    )
    institution = fields.Char(
        "Institution", readonly=True,
        help="Imaging center where study was undertaken"
    )
    ref_phys = fields.Char("Referring Physician", readonly=True)
    req_phys = fields.Char("Requesting Physician", readonly=True)
    server = fields.Many2One(
        "gnuhealth.orthanc.config", "Server", readonly=True)

    ohif_viewer_link = fields.Function(
        fields.Char(
            "OHIF Viewer", help="Link to study in OHIF Viewer."),
        "get_ohif_viewer_link")

    stone_viewer_link = fields.Function(
        fields.Char(
            "Stone Viewer", help="Link to study in Stone Viewer."),
        "get_stone_viewer_link")

    orthanc_explorer_link = fields.Function(
        fields.Char(
            "Orthanc Explorer", help="Link to study in Orthanc Explorer."),
        "get_orthanc_explorer_link")

    def get_ohif_viewer_link(self, name):
        """
        Return a link to the Orthanc study with the specified uuid in the
        OHIF viewer.

        :param name: Label of the study to get the link for.
        :type name: str

        :return: URL to the Orthanc study in OHIF viewer.
        :rtype: str
        """

        pre = "".join([self.server.domain.rstrip("/"), "/"])
        add = "ohif/viewer?url=../studies/{}/ohif-dicom-json".format(
            self.uuid)
        return urljoin(pre, add)

    def get_stone_viewer_link(self, name):
        """
        Return a link to the Orthanc study with the specified uuid in the
        Stone Viewer.

        :param name: Label of the study to get the link for.
        :type name: str

        :return: URL to the Orthanc study in Stone Viewer.
        :rtype: str
        """

        pre = "".join([self.server.domain.rstrip("/"), "/"])
        add = "stone-webviewer/index.html?study={}".format(
            self.instance_uid)
        return urljoin(pre, add)

    def get_orthanc_explorer_link(self, name):
        """
        Return a link to the Orthanc study with the specified uuid in the
        Orthanc explorer.

        :param name: Label of the study to get the link for.
        :type name: str

        :return: URL to the Orthanc study in the Orthanc Explorer.
        :rtype: str
        """

        pre = "".join([self.server.domain.rstrip("/"), "/"])
        add = "app/explorer.html#study?uuid={}".format(self.uuid)
        return urljoin(pre, add)

    imaging_test = fields.Many2One("gnuhealth.imaging.test.result", "Study")

    @classmethod
    def __setup__(cls):
        """
        Set up the ``OrthancStudy`` class for database access.

        This method is a class method that initializes various
        properties and constraints of the ``OrthancStudy`` model.
        It sets up a SQL constraint to ensure that the ``server`` and
        ``uuid`` columns are unique.
        """

        super().__setup__()
        t = cls.__table__()
        cls._sql_constraints = [
            (
                "uuid_unique",
                Unique(t, t.server, t.uuid),
                "UUID must be unique for a given server",
            )
        ]

    def get_rec_name(self, name):
        """
        Return name of actual study.

        :param name: The name of the record.
        :type name: str

        :return: A string representing the display name of the record.
        :rtype: str

        .. note:: This method follows the Tryton Syntax.
            It is the getter function for the field ``rec_name``.
        .. seealso:: classmethod: ``ModelStorage.get_rec_name` from
            class: ``trytond.model.ModelStorage``
        """

        return ": ".join((self.ident or self.uuid, self.description or ""))

    @classmethod
    def get_info_from_dicom(cls, studies, server):
        """
        Extract study  information from DICOM data for writing to database.

        :param studies: List of DICOM data for studies.
        :type studies: list

        :return: List of dictionaries with study information.
        :rtype: list
        """

        data = []

        for study in studies:
            try:
                date = datetime.strptime(
                    study["MainDicomTags"]["StudyDate"], "%Y%m%d"
                ).date()
            except Exception:
                logger.exception(
                    "Invalid date format. Please provide the date in "
                    "the format %Y%m%d"
                )
                date = None
            try:
                description = \
                    study["MainDicomTags"]["RequestedProcedureDescription"]
            except KeyError:
                logger.warning("No description provided")
                description = None

            entry = {
                "parent_patient": study["ParentPatient"],
                "uuid": study["ID"],
                "description": description,
                "date": date,
                "ident": study.get("MainDicomTags").get("StudyID"),
                "instance_uid": study.get("MainDicomTags").get(
                    "StudyInstanceUID"),
                "requested_procedure_id": study.get("MainDicomTags").get(
                    "RequestedProcedureID"),
                "institution": study.get("MainDicomTags").get(
                    "InstitutionName"),
                "ref_phys": study.get("MainDicomTags").get(
                    "ReferringPhysicianName"
                ),
                "req_phys": study.get(
                    "MainDicomTags").get("RequestingPhysician")
            }

            entry['merge_id'] = cls.get_merge_id(entry, server)

            data.append(entry)

        return data

    @classmethod
    def get_merge_id(cls, entry, server):
        prefix = gnuhealth_org_root

        # In most situations, we use 'StudyInstanceUID' to store merge
        # id.
        if (entry['instance_uid'] or '').startswith(prefix):
            return entry['instance_uid']

        # XXX: for imaging workstation's bugs, sometimes, we use other
        # study tags instead of 'StudyInstanceUID' to store merge id.
        for (k, v) in entry.items():
            if isinstance(v, str) and v.startswith(prefix):
                return v

        # XXX: for imaging workstation's bugs, sometimes, we use
        # 'PatientID' tag to store merge id.
        Patient = Pool().get("gnuhealth.orthanc.patient")
        patient = Patient.search(
            [("uuid", "=", entry["parent_patient"]),
             ("server", "=", server)],
            limit=1)[0]
        if patient:
            if patient.ident:
                if patient.ident.startswith(prefix):
                    return patient.ident

    @classmethod
    def update_studies(cls, studies, server):
        """
        Update studies  with new information from DICOM files.

        :param studies: A list of studies data in DICOM format.
        :type studies: list

        :param server: The server to update the studies on.
        :type server: str
        """

        entries = cls.get_info_from_dicom(studies, server)
        updates = []
        for entry in entries:
            try:
                study = cls.search(
                    [("uuid", "=", entry["uuid"]),
                        ("server", "=", server)], limit=1
                )[0]

                result = cls.find_test_result(entry)

                study.description = entry["description"]
                study.date = entry["date"]
                study.ident = entry["ident"]
                study.instance_uid = entry["instance_uid"]
                study.merge_id = entry["merge_id"]
                study.institution = entry["institution"]
                study.ref_phys = entry["ref_phys"]
                study.req_phys = entry["req_phys"]
                if result:
                    study.imaging_test = result.id
                updates.append(study)
                logger.info("Updating study {}".format(entry["uuid"]))
            except IndexError:
                continue
                logger.warning(
                    "Unable to update study {}".format(entry["uuid"]))
        cls.save(updates)

    @classmethod
    def find_test_result(cls, entry):
        if entry and entry["merge_id"] and len(entry["merge_id"]) > 0:
            Result = Pool().get('gnuhealth.imaging.test.result')
            result = Result.search(
                [("merge_id", "=", entry["merge_id"])],
                limit=1)
            return (result and result[0])

    @classmethod
    def create_studies(cls, studies, server):
        """
        Create studies with information from DICOM files.

        :param studies: A list of studies data in DICOM format.
        :type studies: list

        :param server: The server to update the patients on.
        :type server: str
        """

        pool = Pool()
        Patient = pool.get("gnuhealth.orthanc.patient")

        entries = cls.get_info_from_dicom(studies, server)
        for entry in entries:
            try:
                patient = Patient.search(
                    [("uuid", "=",
                      entry["parent_patient"]), ("server", "=", server)],
                    limit=1,
                )[0]
            except IndexError:
                patient = None
                logger.warning(
                    "No parent patient found for study {}".format(entry["ID"])
                )
            entry.pop("parent_patient")  # remove non-model entry
            entry["server"] = server
            entry["patient"] = patient
            result = cls.find_test_result(entry)
            if result:
                entry["imaging_test"] = result.id

        cls.create(entries)


class TestResult(metaclass=PoolMeta):
    __name__ = "gnuhealth.imaging.test.result"

    """
    Adds Orthanc imaging studies to imaging test result.

    :param ModelSQL: Inherit from the Tryton ModelSQL class for SQL
                     database operations.
    :type ModelSQL: class: ``trytond.model.ModelSQL``

    :param ModelView: Inherit from the Tryton ModelView class for user
                      interface operations.
    :type ModelView: class: ``trytond.model.ModelView``

    :var __name__: The unique name ``gnuhealth.imaging.test.result``
                   of the model.
    :vartype __name__: str
    """

    studies = fields.One2Many(
        "gnuhealth.orthanc.study", "imaging_test", "Orthanc studies",
        readonly=True
    )


class Patient(metaclass=PoolMeta):
    __name__ = "gnuhealth.patient"

    """
    Adds Orthanc patients to the main patient data.

    :param ModelSQL: Inherit from the Tryton ModelSQL class for SQL
                     database operations.
    :type ModelSQL: class: ``trytond.model.ModelSQL``

    :param ModelView: Inherit from the Tryton ModelView class for user
                      interface operations.
    :type ModelView: class: ``trytond.model.ModelView``

    :var __name__: The unique name ``gnuhealth.patient`` of the model.
    :vartype __name__: str
    """

    orthanc_patients = fields.One2Many(
        "gnuhealth.orthanc.patient", "patient", "Orthanc patients"
    )

    orthanc_studies = fields.One2Many(
        'gnuhealth.imaging_orthanc.study',
        'patient', 'Orthanc Study')
