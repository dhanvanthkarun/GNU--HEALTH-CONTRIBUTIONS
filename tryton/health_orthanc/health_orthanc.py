# SPDX-FileCopyrightText: 2019-2022 Chris Zimmerman <chris@teffalump.com>
# SPDX-FileCopyrightText: 2021-2023 Luis Falcón <falcon@gnuhealth.org>
# SPDX-FileCopyrightText: 2021-2023 GNU Solidario <health@gnusolidario.org>
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

from trytond.model import ModelView, ModelSQL, Workflow, fields, Unique
from trytond.pyson import Eval, Not, Bool, And, Or
from trytond.pool import Pool
from trytond.transaction import Transaction
from trytond.modules.health.core import get_institution

from beren import Orthanc as RestClient
from requests.auth import HTTPBasicAuth as auth
from datetime import datetime
from urllib.parse import urljoin
from genshi.template import TextTemplate
from pydicom.uid import generate_uid

import logging
import pendulum

__all__ = [
    "OrthancWorklistTemplate",
    "OrthancServerConfig",
    "OrthancPatient",
    "OrthancStudy",
    "ImagingTestRequest",
    "ImagingTest",
    "Patient",
    "TestResult",
]

logger = logging.getLogger(__name__)


class OrthancWorklistTemplate(ModelSQL, ModelView):
    """Orthanc Worklist Template"""
    __name__ = "gnuhealth.orthanc.worklist.template"
    _rec_name = "name"

    name = fields.Char(
        "Name", required=True,
        help="Worklist template name")

    template = fields.Text(
        "Template", required=True, 
        help="Genshi syntax template used to create worklist text, "
        "with dump2dcm command of dcmtk help, worklist text file can "
        "be converted to a .wl file.")

    comment = fields.Text('Comment')

    @staticmethod
    def default_template():
        template = """\
(0020,000d) UI [$StudyInstanceUID]
(0040,1001) SH [$RequestedProcedureID]
(0010,0010) PN [$PatientName]
(0010,0020) LO [$PatientID]
(0010,0030) DA [$PatientBirthDate]
(0010,0040) CS [$PatientSex]
(0032,1032) PN [$RequestingPhysician]
(0008,0080) LO [$InstitutionName]
"""
        return template


class OrthancServerConfig(ModelSQL, ModelView):
    """Orthanc server details"""

    __name__ = "gnuhealth.orthanc.config"
    _rec_name = "label"

    label = fields.Char(
        "Label", required=True, help="Label for server (eg., remote1)")

    domain = fields.Char(
        "URL", required=True, help="The full URL of the Orthanc server")

    user = fields.Char(
        "Username", required=True, help="Username for Orthanc REST server")

    password = fields.Char(
        "Password", required=True, help="Password for Orthanc REST server")

    last = fields.BigInteger(
        "Last Index", readonly=True, help="Index of last change")

    sync_time = fields.DateTime(
        "Sync Time", readonly=True, help="Time of last server sync")

    validated = fields.Boolean(
        "Validated", help="Whether the server details have been "
        "successfully checked")

    since_sync = fields.Function(
        fields.TimeDelta("Since last sync", help="Time since last sync"),
        "get_since_sync",)

    since_sync_readable = fields.Function(
        fields.Char("Since last sync", help="Time since last sync"),
        "get_since_sync_readable",
    )
    patients = fields.One2Many(
        "gnuhealth.orthanc.patient", "server", "Patients")

    studies = fields.One2Many("gnuhealth.orthanc.study", "server", "Studies")
    link = fields.Function(
        fields.Char(
            "URL",
            help="Link to server in Orthanc Explorer"), "get_link")

    def get_link(self, name):
        pre = "".join([self.domain.rstrip("/"), "/"])
        add = "app/explorer.html"
        return urljoin(pre, add)

    use_stone_viewer = fields.Boolean(
        "Use Stone Viewer", 
        help="Use Stone Web Viewer")

    @staticmethod
    def default_use_stone_viewer():
        return False

    use_osimis_viewer = fields.Boolean(
        "Use Osimis Viewer", 
        help="Use Osimis Web Viewer")

    @staticmethod
    def default_use_osimis_viewer():
        return False

    @classmethod
    def __setup__(cls):
        super().__setup__()
        t = cls.__table__()
        cls._sql_constraints = [
            ("label_unique", Unique(t, t.label), "The label must be unique.")
        ]
        cls._buttons.update({"do_sync": {}})

    @classmethod
    @ModelView.button
    def do_sync(cls, servers):
        cls.sync(servers)

    @classmethod
    def sync(cls, servers=None):
        """Sync from changes endpoint"""

        pool = Pool()
        patient = pool.get("gnuhealth.orthanc.patient")
        study = pool.get("gnuhealth.orthanc.study")

        if not servers:
            servers = cls.search([("domain", "!=", None),
                                  ("validated", "=", True)])

        logger.info("Starting sync")
        for server in servers:
            if not server.validated:
                continue
            logger.info("Getting new changes for <{}>".format(server.label))
            orthanc = RestClient(server.domain,
                                 auth=auth(server.user, server.password))
            curr = server.last
            new_patients = set()
            update_patients = set()
            new_studies = set()
            update_studies = set()

            while True:
                try:
                    changes = orthanc.get_changes(since=curr)
                except:
                    server.validated = False
                    logger.exception(
                        "Invalid details for <{}>".format(server.label))
                    break
                for change in changes["Changes"]:
                    type_ = change["ChangeType"]
                    if type_ == "NewStudy":
                        new_studies.add(change["ID"])
                    elif type_ == "StableStudy":
                        update_studies.add(change["ID"])
                    elif type_ == "NewPatient":
                        new_patients.add(change["ID"])
                    elif type_ == "StablePatient":
                        update_patients.add(change["ID"])
                    else:
                        pass
                curr = changes["Last"]

                if changes["Done"] is True:
                    logger.info("<{}> at newest change".format(server.label))
                    break

            update_patients -= new_patients
            update_studies -= new_studies
            if new_patients:
                patient.create_patients(
                    [orthanc.get_patient(p) for p in new_patients], server
                )
            if update_patients:
                patient.update_patients(
                    [orthanc.get_patient(p) for p in update_patients], server
                )
            if new_studies:
                study.create_studies(
                    [orthanc.get_study(s) for s in new_studies], server
                )
            if update_studies:
                study.update_studies(
                    [orthanc.get_study(s) for s in update_studies], server
                )
            server.last = curr
            server.sync_time = datetime.now()
            logger.info(
                f"\n\nOrthanc server synchronization summary "
                f"from {server.label} :\n"
                f"Patients: New: {len(new_patients)} | "
                f"Updated: {len(update_patients)}\n"
                f"Studies: New: {len(new_studies)} |"
                f"Updated: {len(update_studies)}\n"
                 )
            
        cls.save(servers)

    @staticmethod
    def quick_check(domain, user, password):
        """Validate the server details"""

        try:
            orthanc = RestClient(domain, auth=auth(user, password))
            orthanc.get_changes(last=True)
        except:
            return False
        else:
            return True

    @fields.depends("domain", "user", "password")
    def on_change_with_validated(self):
        return self.quick_check(self.domain, self.user, self.password)

    def get_since_sync(self, name):
        return datetime.now() - self.sync_time

    def get_since_sync_readable(self, name):
        try:
            d = pendulum.now() - pendulum.instance(self.sync_time)
            return d.in_words(Transaction().language)
        except:
            return ""


class OrthancPatient(ModelSQL, ModelView):
    """Orthanc patient information"""

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
        pre = "".join([self.server.domain.rstrip("/"), "/"])
        add = "app/explorer.html#patient?uuid={}".format(self.uuid)
        return urljoin(pre, add)

    @classmethod
    def __setup__(cls):
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
        """Extract information for writing to database"""

        data = []
        for patient in patients:
            try:
                bd = datetime.strptime(
                    patient["MainDicomTags"]["PatientBirthDate"], "%Y%m%d"
                ).date()
            except:
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
        """Update patients"""

        entries = cls.get_info_from_dicom(patients)
        updates = []
        for entry in entries:
            try:
                patient = cls.search(
                    [("uuid", "=", entry["uuid"]),
                     ("server", "=", server)], limit=1
                )[0]
                patient.name = entry["name"]
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
                    except:
                        pass
                updates.append(patient)
                logger.info("Updating patient {}".format(entry["uuid"]))
            except:
                continue
                logger.warning("Unable to update patient {}".
                               format(entry["uuid"]))
        cls.save(updates)

    @classmethod
    def create_patients(cls, patients, server):
        """Create patients"""

        pool = Pool()
        Patient = pool.get("gnuhealth.patient")

        entries = cls.get_info_from_dicom(patients)
        for entry in entries:
            try:
                g_patient = Patient.search(
                    [("puid", "=", entry["ident"])], limit=1)[0]
                logger.info("Matching PUID found for {}".format(entry["uuid"]))
            except:
                g_patient = None
            entry["server"] = server
            entry["patient"] = g_patient
        cls.create(entries)


class OrthancStudy(ModelSQL, ModelView):
    """Orthanc study"""

    __name__ = "gnuhealth.orthanc.study"

    patient = fields.Many2One(
        "gnuhealth.orthanc.patient", "Patient", readonly=True)

    uuid = fields.Char("UUID", readonly=True, required=True)
    description = fields.Char("Description", readonly=True)
    date = fields.Date("Date", readonly=True)
    ident = fields.Char("ID", readonly=True)
    instance_uid = fields.Char("InstanceUID", readonly=True)
    institution = fields.Char(
        "Institution", readonly=True,
        help="Imaging center where study was undertaken"
    )
    ref_phys = fields.Char("Referring Physician", readonly=True)
    req_phys = fields.Char("Requesting Physician", readonly=True)
    server = fields.Many2One(
        "gnuhealth.orthanc.config", "Server", readonly=True)

    link = fields.Function(
        fields.Char(
            "URL", help="Link to study in Orthanc Explorer"), "get_link")

    imaging_test = fields.Many2One("gnuhealth.imaging.test.result", "Study")

    def get_link(self, name):
        pre = "".join([self.server.domain.rstrip("/"), "/"])
        if self.server.use_stone_viewer:
            add = "stone-webviewer/index.html?study={}".format(self.instance_uid)
        elif self.server.use_osimis_viewer:
            add = "osimis-viewer/app/index.html?study={}".format(self.uuid)
        else:
            add = "app/explorer.html#study?uuid={}".format(self.uuid)
        return urljoin(pre, add)

    @classmethod
    def __setup__(cls):
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
        return ": ".join((self.ident or self.uuid, self.description or ""))

    @staticmethod
    def get_info_from_dicom(studies):
        """Extract information for writing to database"""

        data = []

        for study in studies:
            try:
                date = datetime.strptime(
                    study["MainDicomTags"]["StudyDate"], "%Y%m%d"
                ).date()
            except:
                date = None
            try:
                description = \
                    study["MainDicomTags"]["RequestedProcedureDescription"]
            except:
                description = None
            data.append(
                {
                    "parent_patient": study["ParentPatient"],
                    "uuid": study["ID"],
                    "description": description,
                    "date": date,
                    "ident": study.get("MainDicomTags").get("StudyID"),
                    "instance_uid": study.get("MainDicomTags").get(
                        "StudyInstanceUID"),
                    "requested_procedure_id": study.get(
                        "MainDicomTags").get("RequestedProcedureID"),
                    "institution": study.get("MainDicomTags").get(
                        "InstitutionName"),
                    "ref_phys": study.get("MainDicomTags").get(
                        "ReferringPhysicianName"
                    ),
                    "req_phys": study.get(
                        "MainDicomTags").get("RequestingPhysician"),
                }
            )
        return data

    @classmethod
    def update_studies(cls, studies, server):
        """Update studies"""

        entries = cls.get_info_from_dicom(studies)
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
                study.institution = entry["institution"]
                study.ref_phys = entry["ref_phys"]
                study.req_phys = entry["req_phys"]
                if result:
                    study.imaging_test = result.id
                updates.append(study)
                logger.info("Updating study {}".format(entry["uuid"]))
            except:
                continue
                logger.warning(
                    "Unable to update study {}".format(entry["uuid"]))
        cls.save(updates)

    @classmethod
    def find_test_result(cls, entry):
        if entry and len(entry["instance_uid"]) > 0:
            Result = Pool.get('gnuhealth.imaging.test.result')
            result = Result.search(
                [("request.instance_uid", "=", entry["instance_uid"])],
                limit=1)[0]
            return result

    @classmethod
    def create_studies(cls, studies, server):
        """Create studies"""

        pool = Pool()
        Patient = pool.get("gnuhealth.orthanc.patient")

        entries = cls.get_info_from_dicom(studies)
        for entry in entries:
            try:
                patient = Patient.search(
                    [("uuid", "=",
                      entry["parent_patient"]), ("server", "=", server)],
                    limit=1,
                )[0]
            except:
                patient = None
                logger.warning(
                    "No parent patient found for study {}".format(entry["ID"])
                )
            entry.pop("parent_patient")  # remove non-model entry
            entry["server"] = server
            entry["patient"] = patient
        cls.create(entries)


class ImagingTestRequest(Workflow, ModelSQL, ModelView):
    'Medical Imaging Study Request'
    __name__ = 'gnuhealth.imaging.test.request'

    instance_uid = fields.Char("InstanceUID")

    @staticmethod
    def default_instance_uid():
        # XXX: Maybe we should find a better org root string for
        # gnuhealth, or let org root string configable.
        gnuhealth_org_root = '1.2.836.0.1.3240043.7.198.'
        return generate_uid(gnuhealth_org_root)

    show_worklist_text = fields.Boolean('Worklist')
    
    @staticmethod
    def default_show_worklist_text():
        return False

    worklist_text = fields.Function(
        fields.Text("Worklist text",
                    states={'invisible': Not(Bool(Eval('show_worklist_text')))}),
        'get_worklist_text')

    def get_worklist_text(self, name):
        template = self.requested_test.worklist_template.template
        if template:
            data = {
                # We can not use 'self' as key name, so use 'my'
                # instead.
                'my':                    self,
                'StudyInstanceUID':      self.getDicomStudyInstanceUID(),
                'RequestedProcedureID':  self.getDicomRequestedProcedureID(),
                'PatientName':           self.getDicomPatientName(),
                'PatientID':             self.getDicomPatientID(),
                'PatientBirthDate':      self.getDicomPatientBirthDate(),
                'PatientSex':            self.getDicomPatientSex(),
                'RequestingPhysician':   self.getDicomRequestingPhysician(),
                'InstitutionName':       self.getDicomInstitutionName(),
            }
            tmpl = TextTemplate(template)
            text = str(tmpl.generate(**data))
            return text
        else:
            return ''

    def getDicomStudyInstanceUID(self):
        return self.instance_uid or ''

    def getDicomRequestedProcedureID(self):
        return self.request or ''

    def getDicomPatientName(self):
        name = (self.format_dicom_person_name(self.patient.name.id)
                or (self.patient and self.patient.rec_name ) or '') 
        return name

    def format_dicom_person_name(self, person_id):
        Pname = Pool().get('gnuhealth.person_name')
        officialname = Pname.search(
            [("party", "=", person_id), ("use", "=", 'official')])[0]

        if officialname:
            family = officialname.family or ''
            given = officialname.given or ''
            # gnuhealth.person_name do not support middle name.
            middle = ''
            prefix = officialname.prefix or ''
            suffix = officialname.suffix or ''
            name = "^".join([family, given, middle, prefix, suffix]).rstrip('^')
            return name
    
    def getDicomPatientID(self):
        return self.patient and self.patient.puid or ''
    
    def getDicomPatientBirthDate(self):
        dob = self.patient and self.patient.name.dob
        if dob:
            return str(dob).replace('-', '')
    
    def getDicomPatientSex(self):
        sex = self.patient and self.patient.gender
        if sex == 'f':
            return 'F'
        elif sex == 'm':
            return 'M'
        else:
            return "O"

    def getDicomRequestingPhysician(self):
        name = (self.format_dicom_person_name(self.doctor.name.id)
                or (self.doctor and self.doctor.rec_name) or '')
        return name

    def getDicomInstitutionName(self):
        institution = get_institution()
        return institution and institution.rec_name or ''


class ImagingTest(ModelSQL, ModelView):
    'Medical Imaging Study'
    __name__ = 'gnuhealth.imaging.test'

    worklist_template = fields.Many2One(
        "gnuhealth.orthanc.worklist.template", "Worklist template"
    )


class TestResult(ModelSQL, ModelView):
    """Add Orthanc imaging studies to imaging test result"""

    __name__ = "gnuhealth.imaging.test.result"

    studies = fields.One2Many(
        "gnuhealth.orthanc.study", "imaging_test", "Orthanc studies", readonly=True
    )

    @classmethod
    def create(cls, vlist):
        Request = Pool().get('gnuhealth.imaging.test.request')
        vlist = [x.copy() for x in vlist]

        for values in vlist:
            request = Request.search(
                [("request", "=", values['order'])], limit=1)[0]

            studies = cls.find_orthanc_studies(request)

            if studies:
                values['studies'] = [('add', [x.id for x in studies])]
            
        return super(TestResult, cls).create(vlist)

    @classmethod
    def find_orthanc_studies(cls, request):
        if request and len(request.instance_uid) > 0:
            Study = Pool().get('gnuhealth.orthanc.study')
            studies = Study.search(
                [("instance_uid", "=", request.instance_uid)])
            return studies


class Patient(ModelSQL, ModelView):
    """Add Orthanc patient(s) to the main patient data"""

    __name__ = "gnuhealth.patient"

    orthanc_patients = fields.One2Many(
        "gnuhealth.orthanc.patient", "patient", "Orthanc patients"
    )
