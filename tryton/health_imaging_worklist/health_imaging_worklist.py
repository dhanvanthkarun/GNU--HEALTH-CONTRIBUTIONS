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
#                         HEALTH IMAGING WORKLIST package               #
#                     health_imaging_worklist.py: main module           #
#########################################################################

"""
Worklist feature of health_imaging.

This module let health_imaging support worklist feature.
"""

from trytond.model import ModelView, ModelSQL, fields
from trytond.pyson import Eval, Not, Bool
from trytond.pool import Pool, PoolMeta
from trytond.modules.health.core import (get_institution,
                                         compute_age_from_dates,
                                         parse_compute_age)

from genshi.template import NewTextTemplate
from pydicom.uid import generate_uid

import logging
import json

__all__ = [
    "WorklistTemplate",
    "ImagingTestRequest",
    "ImagingTest",
    "TestResult",
]

logger = logging.getLogger(__name__)

# XXX: Maybe we should find a better org root string for
# gnuhealth, or let org root string configable.
gnuhealth_org_root = '1.2.836.0.1.3240043.7.198.'


class WorklistTemplate(ModelSQL, ModelView):
    """Worklist Template"""
    __name__ = "gnuhealth.imaging_worklist.worklist_template"
    _rec_name = "name"

    name = fields.Char(
        "Name", required=True,
        help="Worklist template name")

    template_type = fields.Selection([
        ('dump2dcm', 'dump2dcm'),
        ('json', 'json'),
    ], 'Template Type', sort=False)

    template = fields.Text(
        "Template", required=True,
        help="Genshi syntax template used to create worklist text, "
        "if template type is dump2dcm, worklist wl file can be generated "
        "by dump2dcm command of dcmtk. "
        "if template type is json, worklist wl file can be generated "
        "from json by tool like python-orthanc-tools.")

    charset = fields.Char(
        'Charset',
        help='This field is used to store SpecificCharacterSet tag '
        '(0008,0005) of worklist, for example: ISO_IR 100, ISO_IR 192,'
        ' GBK ...')

    comment = fields.Text('Comment')

    @staticmethod
    def default_charset():
        return 'IS0_IR 192'

    @staticmethod
    def default_template_type():
        return 'dump2dcm'

    @classmethod
    def default_template(cls, **abc):
        template = """\
{% if template_type=='dump2dcm' %}\\
(0008,0005) SH [$SpecificCharacterSet]
(0008,0201) SH [$TimezoneOffsetFromUTC]
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
    (0040,0001) AE [$ScheduledStationAETitle]
    (0040,0002) DA [$ScheduledProcedureStepStartDate]
    (0040,0003) TM [$ScheduledProcedureStepStartTime]
  (fffe,e00d) na (ItemDelimitationItem)
(fffe,e0dd) na (SequenceDelimitationItem)
{% end %}\\
\\
{% if template_type=='json' %}\\
{
    "SpecificCharacterSet": "$SpecificCharacterSet",
    "TimezoneOffsetFromUTC": "$TimezoneOffsetFromUTC",
    "AccessionNumber": "$AccessionNumber",
    "RequestedProcedureID": "$RequestedProcedureID",
    "StudyInstanceUID": "$StudyInstanceUID",
    "PatientName": "$PatientName",
    "PatientID": "$PatientID",
    "PatientAge": "$PatientAge",
    "PatientBirthDate": "$PatientBirthDate",
    "PatientSex": "$PatientSex",
    "RequestingPhysician": "$RequestingPhysician",
    "RequestingService": "$RequestingService",
    "ReferringPhysicianName": "$ReferringPhysicianName",
    "InstitutionName": "$InstitutionName",
    "RequestedProcedureDescription": "$RequestedProcedureDescription",
    "Modality": "$Modality",
    "ScheduledStationAETitle": "$ScheduledStationAETitle",
    "ScheduledProcedureStepStartDate": "$ScheduledProcedureStepStartDate",
    "ScheduledProcedureStepStartTime": "$ScheduledProcedureStepStartTime",
    "ScheduledProcedureStepID": "$ScheduledProcedureStepID"
}
{% end %}\
"""
        return template


class ImagingTestRequest(metaclass=PoolMeta):
    __name__ = 'gnuhealth.imaging.test.request'

    computed_age = fields.Function(fields.Char(
        'Age',
        help="Computed patient age at image request."),
        'patient_age_at_imaging_request')

    def patient_age_at_imaging_request(self, name):
        if (self.patient.party.dob and self.date):
            return compute_age_from_dates(
                self.patient.party.dob, None, None, None, 'age',
                self.date.date())

    merge_id = fields.Char("Merge ID")

    @staticmethod
    def default_merge_id():
        # Use DICOM UID format, for most situation, merge id is used
        # as StudyInstanceUID.
        return generate_uid(gnuhealth_org_root)

    show_worklist_text = fields.Boolean('Worklist Preview')

    @staticmethod
    def default_show_worklist_text():
        return False

    worklist_status = fields.Selection([
        ('todo', 'Todo'),
        ('done', 'Done'),
        ('canceled', 'Canceled'),
    ], 'Worklist Status', sort=False,
        help="Worklist processing status.")

    @staticmethod
    def default_worklist_status():
        return 'todo'

    worklist_text = fields.Function(
        fields.Text("Worklist text",
                    states={'invisible': Not(
                        Bool(Eval('show_worklist_text')))}),
        'get_worklist_text')

    def get_worklist_text(self, name):
        template = self.get_worklist_template()
        template_type = self.get_worklist_template_type()
        if template:
            data = self.get_worklist_template_data()
            data = {k: self.quote_template_value(v, template_type)
                    for (k, v) in data.items()}
            tmpl = NewTextTemplate(template)
            text = str(tmpl.generate(**data))
            return text
        else:
            return ''

    @classmethod
    def quote_template_value(cls, value, template_type):
        if isinstance(value, str):
            if template_type == 'json':
                value = json.dumps(value, ensure_ascii=False)[1:][:-1]
            elif template_type == 'dump2dcm':
                value = value.replace('\n', ' ')

        return value

    def get_worklist_template(self):
        template = (
            self.requested_test.imaging_worklist_template and
            self.requested_test.imaging_worklist_template.template)
        return template

    def get_worklist_template_type(self):
        template_type = (
            self.requested_test.imaging_worklist_template and
            self.requested_test.imaging_worklist_template.template_type)
        return template_type

    def get_worklist_template_data(self):
        data = {
            # We can not use 'self' as key name, so use 'my'
            # instead.
            'my': self,
            'template_type': self.get_worklist_template_type(),
            'MergeID': self.merge_id or '',
            'SpecificCharacterSet': self.getDicomSpecificCharacterSet(),
            'AccessionNumber': self.getDicomAccessionNumber(),
            'RequestedProcedureID': self.getDicomRequestedProcedureID(),
            'StudyInstanceUID': self.getDicomStudyInstanceUID(),
            'PatientName': self.getDicomPatientName(),
            'PatientID': self.getDicomPatientID(),
            'PatientAge': self.getDicomPatientAge(),
            'PatientBirthDate': self.getDicomPatientBirthDate(),
            'PatientSex': self.getDicomPatientSex(),
            'RequestingPhysician': self.getDicomRequestingPhysician(),
            'RequestingService': self.getDicomRequestingService(),
            'InstitutionName': self.getDicomInstitutionName(),
            'Modality': self.getDicomModality(),
            'ReferringPhysicianName':
            self.getDicomReferringPhysicianName(),
            'RequestedProcedureDescription':
            self.getDicomRequestedProcedureDescription(),
            'ScheduledStationAETitle':
            self.getDicomScheduledStationAETitle(),
            'ScheduledProcedureStepStartDate':
            self.getDicomScheduledProcedureStepStartDate(),
            'ScheduledProcedureStepStartTime':
            self.getDicomScheduledProcedureStepStartTime(),
            'ScheduledProcedureStepID':
            self.getDicomScheduledProcedureStepID(),
            'TimezoneOffsetFromUTC':
            self.getDicomTimezoneOffsetFromUTC(),
        }
        return data

    def getDicomSpecificCharacterSet(self):
        charset = (
            self.requested_test.imaging_worklist_template and
            self.requested_test.imaging_worklist_template.charset)
        return charset

    def getDicomAccessionNumber(self):
        return self.request or ''

    def getDicomRequestedProcedureID(self):
        return self.request_line or ''

    def getDicomStudyInstanceUID(self):
        return self.merge_id or ''

    def getDicomPatientName(self):
        name = (self.format_dicom_person_name(self.patient.party.id)
                or (self.patient and self.patient.rec_name) or '')
        return name

    def format_dicom_person_name(self, person_id):
        Pname = Pool().get('gnuhealth.person_name')

        try:
            officialname = Pname.search(
                [("party", "=", person_id), ("use", "=", 'official')])[0]
        except BaseException:
            officialname = None

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
        dob = self.patient and self.patient.party.dob
        if dob:
            return dob.strftime('%Y%m%d')

    def getDicomPatientAge(self):
        age_str = self.computed_age
        if age_str:
            year, month, day = parse_compute_age(age_str)

            # Handle y, m, d = None
            if year is None:
                year = -1
            if month is None:
                month = -1
            if day is None:
                day = -1

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

    def getDicomRequestingPhysician(self):
        """
        Returns the health professional who requests  the test
        """
        name = (self.format_dicom_person_name(self.doctor.party.id)
                or (self.doctor and self.doctor.rec_name) or '')
        return name

    def getDicomRequestingService(self):
        """
        Returns the specialty of the physician associated to the test
        as the Service
        """
        name = ''
        if (self.doctor.main_specialty):
            name = self.doctor.main_specialty.rec_name
        return name

    def getDicomReferringPhysicianName(self):
        """
        Returns the health professional who sent / derived the patient
        to this unit
        """

        name = (self.format_dicom_person_name(self.doctor.party.id)
                or (self.doctor and self.doctor.rec_name) or '')
        return name

    def getDicomInstitutionName(self):
        # Return the name (string) of the institution
        institution_id = get_institution()
        if institution_id:
            institution = \
                Pool().get('gnuhealth.institution')(institution_id)
            return institution.rec_name
        else:
            return ''

    def getDicomRequestedProcedureDescription(self):
        test = self.requested_test and self.requested_test.rec_name or ''
        return test

    def getDicomScheduledStationAETitle(self):
        aetitle = self.requested_test.aetitle or ''
        return aetitle

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

    def getDicomScheduledProcedureStepID(self):
        # FIXME: how to get proper value of this tag from gnuhealth?
        # request number is enough?
        return self.request or ''

    def getDicomTimezoneOffsetFromUTC(self):
        # Datetimes get from gnuhealth are UTC datetimes, so we need
        # set dicom tag (0008,0201) 'Timezone Offset From UTC' to
        # '+0000'.
        return '+0000'

    def getDicomModality(self):
        test_type = (self.requested_test.test_type and
                     self.requested_test.test_type.code or '')
        return test_type


class ImagingTest(metaclass=PoolMeta):
    __name__ = 'gnuhealth.imaging.test'

    aetitle = fields.Char(
        "AETitle",
        help="AETitle string, used as (0040,0001) "
        "ScheduledStationAETitle tag in worklist template."
    )

    # NOTE: health_orthanc has 'worklist_template' field, so we use
    # 'imaging_worklist_template' instead, which let database upgrade
    # a bit easier.
    imaging_worklist_template = fields.Many2One(
        "gnuhealth.imaging_worklist.worklist_template", "Worklist template"
    )


class TestResult(metaclass=PoolMeta):
    __name__ = "gnuhealth.imaging.test.result"

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

        return super(TestResult, cls).create(vlist)
