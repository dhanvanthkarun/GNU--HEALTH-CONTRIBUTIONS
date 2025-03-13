#!/usr/bin/env python

# SPDX-FileCopyrightText: 2008-2024 Luis Falcón <falcon@gnuhealth.org>
# SPDX-FileCopyrightText: 2011-2024 GNU Solidario <health@gnusolidario.org>

# SPDX-License-Identifier: GPL-3.0-or-later

#########################################################################
#   Hospital Management Information System (HMIS) component of the      #
#                       GNU Health project                              #
#                   https://www.gnuhealth.org                           #
#########################################################################
#                     HEALTH LAB package                                #
#                health_lab.py: main module                             #
#########################################################################
from datetime import datetime
from trytond.model import ModelView, ModelSQL, fields, Unique
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval, Not, Bool
from trytond.modules.health.core import (get_health_professional,
                                         get_age_for_comparison)

import re

try:
    from PIL import Image
except ImportError:
    Image = None


__all__ = [
    'PatientData', 'TestType', 'Lab',
    'GnuHealthLabTestUnits', 'GnuHealthTestCritearea',
    'GnuHealthPatientLabTest', 'PatientHealthCondition']


class PatientData(metaclass=PoolMeta):
    __name__ = 'gnuhealth.patient'

    lab_test_ids = fields.One2Many(
        'gnuhealth.patient.lab.test', 'patient_id',
        'Lab Tests Required')


class TestType(ModelSQL, ModelView):
    'Type of Lab test'
    __name__ = 'gnuhealth.lab.test_type'

    name = fields.Char(
        'Test',
        help="Test type, eg X-Ray, hemogram,biopsy...", required=True,
        translate=True)
    code = fields.Char(
        'Code',
        help="Short name - code for the test", required=True)

    specimen_type = fields.Char(
        'Specimen',
        help='Specimen type, for example: '
        'whole blood, plasma, urine or feces ...',
        translate=True)

    info = fields.Text('Description')
    product_id = fields.Many2One('product.product', 'Service', required=True)
    critearea = fields.One2Many(
        'gnuhealth.lab.test.critearea', 'test_type_id',
        'Test Cases')

    gender = fields.Selection([
        (None, ''),
        ('m', 'Male'),
        ('f', 'Female'),
    ], 'Gender')

    @staticmethod
    def default_gender():
        return None

    min_age = fields.Float(
        "Min age",
        help='Min age year, '
        '(years x 365 + months x 30.5 + days) / 365')

    @staticmethod
    def default_min_age():
        return 0

    max_age = fields.Float(
        "Max age",
        help='Max age year, '
        '(years x 365 + months x 30.5 + days) / 365')

    @staticmethod
    def default_max_age():
        return 150

    age_range = fields.Function(
        fields.Char('Age range'), 'get_age_range')

    def get_age_range(self, name):
        min_age = self.min_age
        max_age = self.max_age
        if min_age is not None and max_age is not None:
            if min_age is None:
                min_age = 0
            if max_age is None:
                max_age = 150
            return str(min_age) + "-" + str(max_age)

    category = fields.Selection([
        (None, ''),
        ('hematology', 'Hematology Testing'),
        ('fluid_excreta', 'Body Fluid and Excreta Examination'),
        ('biochemical', 'Biochemical Testing'),
        ('immunological', 'Immunological Testing'),
        ('microbiological', 'Microbiological Testing'),
        ('molecular_biology', 'Molecular Biology Testing'),
        ('chromosome_genetic', 'Chromosome and Genetic Disease Detection'),
        ('others', 'Others'),
    ], 'Category', sort=False)

    @staticmethod
    def default_category():
        return None

    report_style = fields.Selection([
        ('tbl_h_r_u_nr',
         'Table with result, unit and normal_range columns'),
        ('tbl_h_r_nr', 'Table with result and normal_range columns'),
        ('tbl_h_r', 'Table with result column'),
        ('tbl_nh_r', 'Table with result column (no header)'),
        ('tbl_nh_r_img',
         'Table with result column and inline images (no header)'),
        ('no_tbl', 'Do not use table'),
        ('do_not_show', 'Do not show in report'),
    ], 'Report style', sort=False)

    @staticmethod
    def default_report_style():
        return 'tbl_h_r_nr'

    tags = fields.Char(
        'Tags', help='Tags of test type, which can be used in '
        'if directive of report template file, '
        'tags use letters and numbers, separated by colon.')

    # Mostly used in report template file.
    def all_tags(self):
        tags = self.tags.split(':')
        return tags.sort()

    # Mostly used in report template file.
    def has_tag(self, tag):
        tags = self.tags.split(':')
        return (tag in tags)

    active = fields.Boolean('Active')

    @staticmethod
    def default_active():
        return True

    @classmethod
    def __setup__(cls):
        super(TestType, cls).__setup__()
        t = cls.__table__()
        cls._sql_constraints = [
            ('code_uniq', Unique(t, t.name),
             'The Lab Test code must be unique')
        ]

        cls._order.insert(0, ('category', 'ASC'))
        cls._order.insert(1, ('name', 'ASC'))
        cls._order.insert(2, ('gender', 'ASC'))
        cls._order.insert(3, ('min_age', 'ASC'))
        cls._order.insert(4, ('max_age', 'ASC'))
        cls._order.insert(4, ('tags', 'ASC'))

    @classmethod
    def check_xml_record(cls, records, values):
        return True

    @classmethod
    def search_rec_name(cls, name, clause):
        """ Search for the full name and the code """
        field = None
        for field in ('name', 'code'):
            tests = cls.search([(field,) + tuple(clause[1:])], limit=1)
            if tests:
                break
        if tests:
            return [(field,) + tuple(clause[1:])]
        return [(cls._rec_name,) + tuple(clause[1:])]

    @classmethod
    def write(cls, test_types, values):
        for test_type in test_types:
            if values.get('tags') != '':
                tags = values.get('tags', '').split(':')
                tags = [re.sub(r'[^\w_@#%]', '', tag) for tag in tags]
                tags = sorted(set([tag for tag in tags if tag != '']))
                values['tags'] = ":".join(tags)
        return super(TestType, cls).write(test_types, values)


class Lab(ModelSQL, ModelView):
    'Patient Lab Test Results'
    __name__ = 'gnuhealth.lab'

    name = fields.Char('ID', help="Lab result ID", readonly=True)
    test = fields.Many2One(
        'gnuhealth.lab.test_type', 'Test type',
        help="Lab test type", required=True)
    source_type = fields.Selection([
        ('patient', 'Patient'),
        ('other_source', 'Other')
    ], 'Source',
        help='Sample source type.',
        sort=False)
    source_type_str = source_type.translated('source_type')

    patient = fields.Many2One(
        'gnuhealth.patient', 'Patient',
        states={'invisible': (Eval('source_type') != 'patient')},
        help="Patient")

    other_source = fields.Char(
        'Other',
        states={
            'invisible': (
                Eval('source_type') != 'other_source')},
        help="Other sample source.")
    source_name = fields.Function(
        fields.Text('Source name'), 'get_source_name')

    def get_source_name(self, name=None, with_puid=False, with_gender=False):
        if self.is_patient():
            pname = (self.patient
                     and self.patient.rec_name
                     or '')
            puid_str = (with_puid
                        and self.patient
                        and f' ({self.patient.puid})'
                        or '')
            gender_str = (with_gender
                          and self.patient
                          and f' [{self.patient.gender_str}]'
                          or '')
            return pname + puid_str + gender_str
        else:
            return (self.other_source or '')

    specimen_type = fields.Char(
        'Specimen',
        help='Specimen type, for example: '
        'whole blood, plasma, urine or feces ...')

    pathologist = fields.Many2One(
        'gnuhealth.healthprofessional', 'Pathologist',
        help="Pathologist")
    requestor = fields.Many2One(
        'gnuhealth.healthprofessional', 'Health Prof',
        help="Doctor who requested the test")
    results = fields.Text('Results')
    images = fields.One2Many('ir.attachment', 'resource', 'Images')

    # Mostly used in report template.
    def has_image_comments(self):
        return (True in [img.description != '' and
                         img.description != 'From GNU Health camera' and
                         img.description is not None for img in self.images])

    diagnosis = fields.Text('Diagnosis')
    critearea = fields.One2Many(
        'gnuhealth.lab.test.critearea',
        'gnuhealth_lab_id', 'Lab Test Critearea')

    # Mostly used in report template.
    def has_critearea_remarks(self):
        return (True in [c.remarks != '' and
                         c.remarks is not None for c in self.critearea])

    date_requested = fields.DateTime(
        'Request Date', required=True)
    date_analysis = fields.DateTime('Analysis Date')
    request_order = fields.Integer('Order', readonly=True)

    pathology = fields.Many2One(
        'gnuhealth.pathology', 'Pathology',
        help='Pathology confirmed / associated to this lab test.')

    analytes_summary = fields.Function(
        fields.Text('Summary'), 'get_analytes_summary')

    def get_analytes_summary(self, name):
        summ = ""
        for analyte in self.critearea:
            if analyte.result or analyte.result_text:
                res = ""
                res_text = ""
                if analyte.result_text:
                    res_text = analyte.result_text
                if analyte.result:
                    unit = (analyte.units
                            and analyte.units.name
                            or '')
                    res = str(analyte.result) + f' ({unit})  '
                summ = summ + analyte.rec_name + "  " + \
                    res + res_text + "\n"
        return summ

    @classmethod
    def __setup__(cls):
        super(Lab, cls).__setup__()
        t = cls.__table__()
        cls._sql_constraints = [
            ('id_uniq', Unique(t, t.name),
             'The test ID code must be unique')
        ]
        cls._order.insert(0, ('date_requested', 'DESC'))
        cls._buttons.update({'complete_criteareas': {}})

    @staticmethod
    def default_date_requested():
        return datetime.now()

    @staticmethod
    def default_date_analysis():
        return datetime.now()

    @staticmethod
    def default_source_type():
        return 'patient'

    @classmethod
    def generate_code(cls, **pattern):
        Config = Pool().get('gnuhealth.sequences')
        config = Config(1)
        sequence = config.get_multivalue(
            'lab_test_sequence', **pattern)
        if sequence:
            return sequence.get()

    @classmethod
    def create(cls, vlist):
        vlist = [x.copy() for x in vlist]
        for values in vlist:
            if not values.get('name'):
                values['name'] = cls.generate_code()

        return super(Lab, cls).create(vlist)

    @classmethod
    def search_rec_name(cls, name, clause):
        if clause[1].startswith('!') or clause[1].startswith('not '):
            bool_op = 'AND'
        else:
            bool_op = 'OR'
        return [
            bool_op,
            ('patient', ) + tuple(clause[1:]),
            ('name', ) + tuple(clause[1:]),
        ]

    @classmethod
    @ModelView.button
    def complete_criteareas(cls, labs):
        pool = Pool()
        Critearea = pool.get('gnuhealth.lab.test.critearea')

        lab = labs[0]
        test_cases = []

        for critearea in (lab and lab.test and lab.test.critearea):
            test_cases.append({
                'gnuhealth_lab_id': lab.id,
                'name': critearea.name,
                'code': critearea.code,
                'test_method': critearea.test_method,
                'sequence': critearea.sequence,
                'limits_verified': critearea.limits_verified,
                'lower_limit': critearea.lower_limit,
                'upper_limit': critearea.upper_limit,
                'normal_range': critearea.normal_range,
                "to_integer": critearea.to_integer,
                'units': critearea.units and critearea.units.id})

        if test_cases:
            Critearea.create(test_cases)

    def is_patient(self):
        return (self.source_type == 'patient')

    def is_other_source(self):
        return (self.source_type == 'other_source')

    def find_images(self, critearea_code):
        pool = Pool()
        Attachment = pool.get('ir.attachment')

        images = None
        if critearea_code:
            # We will search images which description include string:
            # '<<critearea_code>>'.
            search_str = '%<<' + critearea_code + '>>%'
            images = Attachment.search(
                [('resource', '=', self),
                 ('description', 'like', search_str)])

        return images


class GnuHealthLabTestUnits(ModelSQL, ModelView):
    'Lab Test Units'
    __name__ = 'gnuhealth.lab.test.units'

    name = fields.Char(
        'Unit', translate=True)

    code = fields.Char(
        'Code', translate=False)

    @classmethod
    def __setup__(cls):
        super(GnuHealthLabTestUnits, cls).__setup__()
        t = cls.__table__()
        cls._sql_constraints = [
            ('name_uniq', Unique(t, t.name),
             'The Unit name must be unique')
        ]

    @classmethod
    def check_xml_record(cls, records, values):
        return True


class GnuHealthTestCritearea(ModelSQL, ModelView):
    'Lab Test Critearea'
    __name__ = 'gnuhealth.lab.test.critearea'

    name = fields.Char(
        'Analyte', required=True, translate=True)

    test_method = fields.Char(
        'Method',
        help='Test method, for example: Real-time PCR ...',
        translate=True)

    excluded = fields.Boolean(
        'Excluded', help='Select this option when'
        ' this analyte is excluded from the test')
    result = fields.Float('Value')

    to_integer = fields.Boolean(
        'To integer',
        help='Convert result value to interger in report.')

    result_text = fields.Text(
        'Result - Text',
        help='Non-numeric results. For '
        'example qualitative values, morphological, colors ...')
    remarks = fields.Text('Remarks')
    normal_range = fields.Text('Reference', translate=True)
    lower_limit = fields.Float('Lower Limit')
    upper_limit = fields.Float('Upper Limit')
    limits_verified = fields.Boolean(
        'Limits verified',
        help='The upper and lower limits have been verified again, '
        'sometimes limits will depend on other indicators of the patient, '
        'such as: age, pregnancy status, etc, so it is very importent to '
        'verify them, because warning status depend on limits values.')
    warning = fields.Boolean(
        'Warn', help='Warns the patient about this '
        ' analyte result'
        ' It is useful to contextualize the result to each patient status '
        ' like age, sex, comorbidities, ...')
    units = fields.Many2One('gnuhealth.lab.test.units', 'Units')
    test_type_id = fields.Many2One(
        'gnuhealth.lab.test_type', 'Test type')
    gnuhealth_lab_id = fields.Many2One(
        'gnuhealth.lab', 'Test Cases')
    sequence = fields.Integer('Sequence')

    # code field is mainly used by interface script, for example:
    # gnuhealth_csv_lab_interface.py in example directory.
    ##
    # sequence field is not suitable for interface script, for it may
    # be changed by user for sort reason, when it changed, interface
    # script can not find error. for example: when a criterea
    # sequence is changed from 1 to 2 for sort reason. if interface
    # script do not update, it will run no error and push wrong
    # value.
    ##
    # name field is not suitable for interface stript too, for it
    # will be changed when user use different languages.
    code = fields.Char(
        'Code', translate=False,
        help="Lab test critearea code, "
        "mainly used by lab interface script.")

    # Show the warning icon if warning is active on the analyte line
    lab_warning_icon = fields.Function(fields.Char(
        'Lab Warning Icon'),
        'get_lab_warning_icon')

    def get_lab_warning_icon(self, name):
        if (self.warning):
            return 'gnuhealth-warning'

    # Use by template
    def get_report_result(self, unit=True, normal_range=True):
        if (self.result is not None):
            if self.to_integer:
                result = str(int(self.result))
            else:
                result = str(self.result)
        else:
            result = ''

        if (self.result is not None) and unit and self.units:
            unit = " " + self.units.name
        else:
            unit = ''

        if (self.result is not None) and normal_range and self.normal_range:
            normal_range = " (" + self.normal_range + ")"
        else:
            normal_range = ''

        if (self.result is not None) and self.result_text:
            result_text = '\n{' + self.result_text + '}'
        elif self.result_text:
            result_text = self.result_text
        else:
            result_text = ''

        return result + unit + normal_range + result_text

    @classmethod
    def __setup__(cls):
        super(GnuHealthTestCritearea, cls).__setup__()
        cls._order.insert(0, ('sequence', 'ASC'))

    @staticmethod
    def default_to_integer():
        return False

    @staticmethod
    def default_sequence():
        return 1

    @staticmethod
    def default_excluded():
        return False

    @staticmethod
    def default_limits_verified():
        return True

    @fields.depends('result', 'lower_limit', 'upper_limit')
    def on_change_with_warning(self):
        normal = True

        # Note: do not use 'if (self.result)' code style in here, for
        # in python: 0.0 = False

        # lower_limit < x < upper_limit
        if (self.result is not None
            and self.lower_limit is not None
                and self.upper_limit is not None):
            normal = (self.lower_limit < self.result < self.upper_limit)
        # lower_limit < x, At least lower_limit
        elif (self.result is not None
              and self.lower_limit is not None
              and self.upper_limit is None):
            normal = (self.lower_limit < self.result)
        # x < upper_limit, Up to upper_limit
        elif (self.result is not None
              and self.lower_limit is None
              and self.upper_limit is not None):
            normal = (self.result < self.upper_limit)
        else:
            normal = True

        return (not normal)

    @classmethod
    def check_xml_record(cls, records, values):
        return True


class GnuHealthPatientLabTest(ModelSQL, ModelView):
    'Lab Test Request'
    __name__ = 'gnuhealth.patient.lab.test'

    test_type = fields.Many2One(
        'gnuhealth.lab.test_type', 'Test Type',
        required=True)
    date = fields.DateTime('Date')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('tested', 'Tested'),
        ('ordered', 'Ordered'),
        ('cancel', 'Cancel'),
    ], 'State', readonly=True)
    source_type = fields.Selection([
        ('patient', 'Patient'),
        ('other_source', 'Other')
    ], 'Source',
        help='Sample source type.',
        sort=False)

    patient_id = fields.Many2One(
        'gnuhealth.patient', 'Patient',
        states={'invisible': (Eval('source_type') != 'patient')})

    other_source = fields.Char(
        'Other',
        states={
            'invisible': (
                Eval('source_type') != 'other_source')},
        help="Other sample source.")
    source_name = fields.Function(
        fields.Text('Source name'), 'get_source_name')

    gender_str = fields.Char(
        'Gender', readonly=True,
        states={'invisible': (Eval('source_type') != 'patient')})

    age_num = fields.Float(
        'Age Num',
        digits=(3, 3), readonly=True,
        help='Age year number, '
        '(years x 365 + months x 30.5 + days) / 365',
        states={'invisible': (Eval('source_type') != 'patient')})

    specimen_type = fields.Char(
        'Specimen',
        help='Specimen type, for example: '
        'whole blood, plasma, urine or feces ...')

    doctor_id = fields.Many2One(
        'gnuhealth.healthprofessional', 'Health Prof',
        help="Health professional who requests the lab test.")
    context = fields.Many2One(
        'gnuhealth.pathology', 'Context',
        help="Health context for this order. It can be a suspected or"
             " existing health condition, a regular health checkup, ...")

    comment = fields.Text('Additional Information')
    request = fields.Integer('Order', readonly=True)
    urgent = fields.Boolean('Urgent')

    def get_source_name(self, name):
        if self.is_patient():
            return self.patient_id and self.patient_id.rec_name or ''
        else:
            return (self.other_source or '')

    @staticmethod
    def default_date():
        return datetime.now()

    @staticmethod
    def default_source_type():
        return 'patient'

    @staticmethod
    def default_state():
        return 'draft'

    @staticmethod
    def default_doctor_id():
        return get_health_professional()

    @classmethod
    def generate_code(cls, **pattern):
        Config = Pool().get('gnuhealth.sequences')
        config = Config(1)
        sequence = config.get_multivalue(
            'lab_request_sequence', **pattern)
        if sequence:
            return sequence.get()

    # Update age_num and gender_str based on the patient_id
    @fields.depends('patient_id')
    def on_change_patient_id(self):
        if (self.patient_id):
            self.gender_str = self.patient_id.gender_str
            self.age_num = get_age_for_comparison(
                self.patient_id.age, type='y')
        else:
            self.gender_str = None
            self.age_num = None

    @classmethod
    def create(cls, vlist):
        vlist = [x.copy() for x in vlist]
        for values in vlist:
            if not values.get('request'):
                values['request'] = cls.generate_code()

        return super(GnuHealthPatientLabTest, cls).create(vlist)

    @classmethod
    def copy(cls, tests, default=None):
        if default is None:
            default = {}
        default = default.copy()
        default['request'] = None
        default['date'] = cls.default_date()
        return super(GnuHealthPatientLabTest, cls).copy(
            tests, default=default)

    def is_patient(self):
        return (self.source_type == 'patient')

    def is_other_source(self):
        return (self.source_type == 'other_source')

    @classmethod
    def __setup__(cls):
        super(GnuHealthPatientLabTest, cls).__setup__()
        cls._order.insert(0, ('date', 'DESC'))
        cls._order.insert(1, ('request', 'DESC'))
        cls._order.insert(2, ('test_type', 'ASC'))

    @classmethod
    def __register__(cls, module):
        table_h = cls.__table_handler__(module)

        # Migration from 4.4: rename name to test_type
        if (table_h.column_exist('name')
                and not table_h.column_exist('test_type')):
            table_h.column_rename('name', 'test_type')

        super().__register__(module)
        table_h = cls.__table_handler__(module)


class PatientHealthCondition(metaclass=PoolMeta):
    __name__ = 'gnuhealth.patient.disease'

    # Adds lab confirmed and the link to the test to the
    # Patient health Condition

    lab_confirmed = fields.Boolean(
        'Lab Confirmed', help='Confirmed by'
        ' laboratory test')

    lab_test = fields.Many2One(
        'gnuhealth.lab', 'Lab Test',
        domain=[('patient', '=', Eval('name'))], depends=['name'],
        states={'invisible': Not(Bool(Eval('lab_confirmed')))},
        help='Lab test that confirmed the condition')
