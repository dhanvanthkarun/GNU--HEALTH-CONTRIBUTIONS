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
from trytond.pyson import Eval, Not, Bool
from trytond.pool import Pool
from trytond.transaction import Transaction
from trytond.modules.health.core import (get_institution,
                                         compute_age_from_dates,
                                         parse_compute_age)

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

# XXX: Maybe we should find a better org root string for
# gnuhealth, or let org root string configable.
gnuhealth_org_root = '1.2.836.0.1.3240043.7.198.'


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

    dump_file_encoding = fields.Char(
        'Encoding',
        help='Encoding used to save worklist text to dump file '
        'by python script, it should work well with (0008,0005) '
        'dicom tag of worklist template, for example: '
        'if (0008,0005) = [ISO_IR 192], encoding should be "utf-8", '
        'if (0008,0005) = [GBK], encoding should be "gbk". ')

    @staticmethod
    def default_dump_file_encoding():
        return 'utf-8'

    comment = fields.Text('Comment')

    @staticmethod
    def default_template():
        template = """\
(0008,0005) SH [ISO_IR 192]
(0008,0201) SH [+0000]
(0008,0050) SH [$AccessionNumber]
(0040,1001) SH [$RequestedProcedureID]
(0020,000d) UI [$StudyInstanceUID]
(0010,0010) PN [$PatientName]
(0010,0020) LO [$PatientID]
(0010,1010) AS [$PatientAge]
(0010,0030) DA [$PatientBirthDate]
(0010,0040) CS [$PatientSex]
(0032,1032) PN [$RequestingPhysician]
(0032,1033) LO [$RequestingService]
(0008,0090) PN [$ReferringPhysicianName]
(0008,0080) LO [$InstitutionName]
(0032,1060) LO [$RequestedProcedureDescription]
(0040,0100) SQ (Sequence with undefined length)
  (fffe,e000) na (Item with undefined length)
    (0008,0060) CS [$Modality]
    (0040,0001) AE [] # ScheduledStationAETitle
    (0040,0002) DA [$ScheduledProcedureStepStartDate]
    (0040,0003) TM [$ScheduledProcedureStepStartTime]
  (fffe,e00d) na (ItemDelimitationItem)
(fffe,e0dd) na (SequenceDelimitationItem)
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

    link = fields.Function(
        fields.Char(
            "URL", help="Link to study in Orthanc Explorer"), "get_link")

    imaging_test = fields.Many2One("gnuhealth.imaging.test.result", "Study")

    def get_link(self, name):
        pre = "".join([self.server.domain.rstrip("/"), "/"])
        if self.server.use_stone_viewer:
            add = "stone-webviewer/index.html?study={}".format(
                self.instance_uid)
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

    @classmethod
    def get_info_from_dicom(cls, studies, server):
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
            limit=1)
        if patient and patient[0].ident.startswith(prefix):
            return patient.ident

    @classmethod
    def update_studies(cls, studies, server):
        """Update studies"""

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
            except:
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
        """Create studies"""

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
            except:
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


class ImagingTestRequest(Workflow, ModelSQL, ModelView):
    'Medical Imaging Study Request'
    __name__ = 'gnuhealth.imaging.test.request'

    computed_age = fields.Function(fields.Char(
        'Age',
        help="Computed patient age at image request."),
        'patient_age_at_imaging_request')

    def patient_age_at_imaging_request(self, name):
        if (self.patient.name.dob and self.date):
            return compute_age_from_dates(
                self.patient.name.dob, None, None, None, 'age',
                self.date.date())

    merge_id = fields.Char("Merge ID")

    @staticmethod
    def default_merge_id():
        # Use DICOM UID format, for most situation, merge id is used
        # as StudyInstanceUID.
        return generate_uid(gnuhealth_org_root)

    show_worklist_text = fields.Boolean('Worklist')

    @staticmethod
    def default_show_worklist_text():
        return False

    worklist_text = fields.Function(
        fields.Text("Worklist text",
                    states={'invisible': Not(
                        Bool(Eval('show_worklist_text')))}),
        'get_worklist_text')

    def get_worklist_text(self, name):
        template = self.get_worklist_template()
        if template:
            data = self.get_worklist_template_data()
            tmpl = TextTemplate(template)
            text = str(tmpl.generate(**data))
            return text
        else:
            return ''

    def get_worklist_template(self):
        template = (self.requested_test.worklist_template and
                    self.requested_test.worklist_template.template)
        return template

    def get_worklist_template_data(self):
        data = {
            # We can not use 'self' as key name, so use 'my'
            # instead.
            'my':                     self,
            'MergeID':                self.merge_id or '',
            'AccessionNumber':        self.getDicomAccessionNumber(),
            'RequestedProcedureID':   self.getDicomRequestedProcedureID(),
            'StudyInstanceUID':       self.getDicomStudyInstanceUID(),
            'PatientName':            self.getDicomPatientName(),
            'PatientID':              self.getDicomPatientID(),
            'PatientAge':             self.getDicomPatientAge(),
            'PatientBirthDate':       self.getDicomPatientBirthDate(),
            'PatientSex':             self.getDicomPatientSex(),
            'RequestingPhysician':    self.getDicomRequestingPhysician(),
            'RequestingService':      self.getDicomRequestingService(),
            'InstitutionName':        self.getDicomInstitutionName(),
            'Modality':               self.getDicomModality(),
            'ReferringPhysicianName':
            self.getDicomReferringPhysicianName(),
            'RequestedProcedureDescription':
            self.getDicomRequestedProcedureDescription(),
            'ScheduledProcedureStepStartDate':
            self.getDicomScheduledProcedureStepStartDate(),
            'ScheduledProcedureStepStartTime':
            self.getDicomScheduledProcedureStepStartTime(),
        }
        return data

    def getDicomAccessionNumber(self):
        return self.request or ''

    def getDicomRequestedProcedureID(self):
        return self.request_line or ''

    def getDicomStudyInstanceUID(self):
        return self.merge_id or ''

    def getDicomPatientName(self):
        name = (self.format_dicom_person_name(self.patient.name.id)
                or (self.patient and self.patient.rec_name) or '')
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
            name = "^".join([
                family, given, middle, prefix, suffix]).rstrip('^')
            return name

    def getDicomPatientID(self):
        return self.patient and self.patient.puid or ''

    def getDicomPatientBirthDate(self):
        dob = self.patient and self.patient.name.dob
        if dob:
            return dob.strftime('%Y%m%d')

    def getDicomPatientAge(self):
        age_str = self.computed_age
        if age_str:
            year, month, day = parse_compute_age(age_str)

            # Handle y, m, d = None
            year = year or '-1'
            month = month or '-1'
            day = day or '-1'

            if year == 0 and month == 0 and day > 0:
                return f'{day:03}D'
            elif year == 0 and month > 0:
                return f'{month:03}M'
            elif year > 0:
                return f'{year:03}Y'
            else:
                return ''

    def getDicomPatientSex(self):
        sex = self.patient and self.patient.gender
        if sex == 'f':
            return 'F'
        elif sex == 'm':
            return 'M'
        else:
            return "O"

    # XXX: Need help: what is RequestingPhysician in gnuhealth
    # imaging?
    def getDicomRequestingPhysician(self):
        name = (self.format_dicom_person_name(self.doctor.name.id)
                or (self.doctor and self.doctor.rec_name) or '')
        return name

    def getDicomRequestingService(self):
        try:
            name = self.doctor.main_specialty.rec_name
        except:
            name = ''
        return name

    # XXX: Need help: what is ReferringPhysician in gnuhealth imaging?
    def getDicomReferringPhysicianName(self):
        name = (self.format_dicom_person_name(self.doctor.name.id)
                or (self.doctor and self.doctor.rec_name) or '')
        return name

    def getDicomInstitutionName(self):
        institution = get_institution()
        return institution and institution.rec_name or ''

    def getDicomRequestedProcedureDescription(self):
        test = self.requested_test and self.requested_test.rec_name or ''
        return test

    def getDicomScheduledProcedureStepStartDate(self):
        # This is UTC datetime, so we need set dicom tag (0008,0201)
        # 'Timezone Offset From UTC' to '+0000'.
        date = self.date.strftime('%Y%m%d')
        return date

    def getDicomScheduledProcedureStepStartTime(self):
        # This is UTC datetime, so we need set dicom tag (0008,0201)
        # 'Timezone Offset From UTC' to '+0000'.
        time = self.date.strftime('%H%M%S')
        return time

    def getDicomModality(self):
        test_type = (self.requested_test.test_type and 
                    self.requested_test.test_type.code or '')
        return test_type


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
        "gnuhealth.orthanc.study", "imaging_test", "Orthanc studies",
        readonly=True
    )

    merge_id = fields.Char("Merge ID")

    @classmethod
    def create(cls, vlist):
        Request = Pool().get('gnuhealth.imaging.test.request')
        vlist = [x.copy() for x in vlist]

        for values in vlist:
            request = Request.search(
                [("id", "=", values['request'])], limit=1)[0]

            if request:
                values['merge_id'] = request.merge_id or ''

            studies = cls.find_orthanc_studies(request)

            if studies:
                values['studies'] = [('add', [x.id for x in studies])]

        return super(TestResult, cls).create(vlist)

    @classmethod
    def find_orthanc_studies(cls, request):
        if request and len(request.merge_id) > 0:
            Study = Pool().get('gnuhealth.orthanc.study')
            studies = Study.search(
                [("merge_id", "=", request.merge_id)])
            return studies


class Patient(ModelSQL, ModelView):
    """Add Orthanc patient(s) to the main patient data"""

    __name__ = "gnuhealth.patient"

    orthanc_patients = fields.One2Many(
        "gnuhealth.orthanc.patient", "patient", "Orthanc patients"
    )
