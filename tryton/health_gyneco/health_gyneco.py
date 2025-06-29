# SPDX-FileCopyrightText: 2008-2025 Luis Falcón <falcon@gnuhealth.org>
# SPDX-FileCopyrightText: 2011-2025 GNU Solidario <health@gnusolidario.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

#########################################################################
#   Hospital Management Information System (HMIS) component of the      #
#                       GNU Health project                              #
#                   https://www.gnuhealth.org                           #
#########################################################################
#                         HEALTH GYNECO package                         #
#                    health_gyneco.py: main module                      #
#########################################################################
import datetime
from dateutil.relativedelta import relativedelta
from trytond.model import ModelView, ModelSQL, fields, Unique
from trytond.pyson import Eval, Not, Bool, Equal
from trytond.pool import Pool, PoolMeta
from trytond.transaction import Transaction
from sql import Table
from sql.aggregate import Count
from trytond.modules.health.core import get_health_professional, \
    get_institution
from trytond.i18n import gettext

from .exceptions import PatientAlreadyPregnant


__all__ = [
    'PatientPregnancy', 'PregnancyResult', 'PrenatalEvaluation',
    'PuerperiumMonitor', 'Perinatal', 'PerinatalMonitor', 'GnuHealthPatient',
    'PatientMenstrualHistory', 'PatientMammographyHistory',
    'PatientPAPHistory', 'PatientColposcopyHistory']


class PatientPregnancy(ModelSQL, ModelView):
    'Patient Pregnancy'
    __name__ = 'gnuhealth.patient.pregnancy'

    # Show paient age at the moment of LMP
    def patient_age_at_pregnancy(self, name):
        if (self.patient.dob and self.lmp):
            rdelta = relativedelta(self.lmp, self.patient.dob)
            years = str(rdelta.years)
            return years
        else:
            return None

    patient = fields.Many2One(
        'gnuhealth.patient', 'Patient', required=True,
        domain=[('party.gender', '=', 'f')])

    gravida = fields.Integer(
        '#', required=True, help="Pregnancy number")

    computed_age = fields.Function(
        fields.Char(
            'Age',
            help="Computed patient age at the moment of LMP"),
        'patient_age_at_pregnancy')

    warning = fields.Boolean(
        'Warn', help='Check this box if this is pregancy'
        ' is or was NOT normal')
    warning_icon = fields.Function(fields.Char(
        'Pregnancy warning icon'), 'get_warn_icon')
    # reverse attribute deprecated in GH 5.0
    # Use the 'current_pregnancy' attribute for different states
    reverse = fields.Boolean(
        'Past', help="Past pregnancy.It will calculate the LMP "
        "from the delivery date and the gestational weeks. "
        "Set this field when the "
        "pregnancy information is referred by the patient, "
        "as a history taking procedure. Keep in mind "
        "that the reverse pregnancy data is subjective.",
    )
    reverse_weeks = fields.Integer(
        "Gest. Weeks", help="Number of weeks at "
        "the end of pregnancy.",
        states={
            'required': Not(Bool(Eval('current_pregnancy'))),
        }
    )

    lmp = fields.Date(
        'LMP', help="Last Menstrual Period",
        states={'readonly': Not(Bool(Eval('current_pregnancy'))),
                'required': Bool(Eval('current_pregnancy')),
                })

    pdd = fields.Function(
        fields.Date('Due Date', help='Pregnancy Due Date'),
        'get_pregnancy_data')

    prenatal_evaluations = fields.One2Many(
        'gnuhealth.patient.prenatal.evaluation', 'pregnancy',
        'Prenatal Evaluations')
    perinatal = fields.One2Many(
        'gnuhealth.perinatal', 'pregnancy', 'Perinatal Info')
    puerperium_monitor = fields.One2Many(
        'gnuhealth.puerperium.monitor',
        'pregnancy', 'Puerperium monitor')
    pregnancy_result = fields.One2Many(
        'gnuhealth.pregnancy.result', 'pregnancy', 'Result',
        states={
            'readonly': Bool(Eval('current_pregnancy')),
        })

    current_pregnancy = fields.Boolean(
        'Current',
        help='Set the field if the patient is currently pregnant')

    fetuses = fields.Integer('Fetuses', required=True)
    monozygotic = fields.Boolean('Monozygotic')
    pregnancy_end_result = fields.Selection([
        (None, ''),
        ('live_birth', 'Live birth'),
        ('abortion', 'Abortion'),
        ('stillbirth', 'Stillbirth'),
        ('status_unknown', 'Status unknown'),
    ], 'Result', sort=False,
        states={
            'required': Not(Bool(Eval('current_pregnancy'))),
    })
    pregnancy_end_date = fields.DateTime(
        'End',
        states={
            'readonly': Bool(Eval('current_pregnancy')),
            'required': Not(Bool(Eval('current_pregnancy'))),
        })
    bba = fields.Boolean(
        'BBA', help="Born Before Arrival",
        states={
            'readonly': Bool(Eval('current_pregnancy')),
        })
    home_birth = fields.Boolean(
        'Home Birth', help="Home Birth",
        states={
            'readonly': Bool(Eval('current_pregnancy')),
        })

    pregnancy_current_week = fields.Function(fields.Integer(
        'Week #', help='Current week'), 'get_pregnancy_data')
    iugr = fields.Selection([
        (None, ''),
        ('symmetric', 'Symmetric'),
        ('assymetric', 'Asymmetric'),
    ], 'IUGR', sort=False)

    institution = fields.Many2One(
        'gnuhealth.institution', 'Institution',
        help="Health center where this initial obstetric record was created")

    healthprof = fields.Many2One(
        'gnuhealth.healthprofessional', 'Health Prof', readonly=True,
        help="Health Professional who created this initial obstetric record")

    gravidae = fields.Function(
        fields.Integer(
            'Pregnancies',
            help="Number of pregnancies, computed from Obstetric history"),
        'patient_obstetric_info')
    premature = fields.Function(
        fields.Integer(
            'Premature',
            help="Preterm < 37 wks live births"), 'patient_obstetric_info')
    abortions = fields.Function(
        fields.Integer('Abortions'),
        'patient_obstetric_info')
    stillbirths = fields.Function(
        fields.Integer('Stillbirths'), 'patient_obstetric_info')

    blood_type = fields.Function(fields.Selection([
        (None, ''),
        ('A', 'A'),
        ('B', 'B'),
        ('AB', 'AB'),
        ('O', 'O'),
    ], 'Blood Type', sort=False),
        'patient_blood_info')

    rh = fields.Function(fields.Selection([
        (None, ''),
        ('+', '+'),
        ('-', '-'),
    ], 'Rh'),
        'patient_blood_info')

    hb = fields.Function(fields.Selection([
        (None, ''),
        ('aa', 'AA'),
        ('as', 'AS'),
        ('ss', 'SS'),
    ], 'Hb'),
        'patient_blood_info')

    notes = fields.Text("Notes")

    # Retrieve the info from the patient current GPA status
    def patient_obstetric_info(self, name):
        if (name == "gravidae"):
            return self.patient.gravida
        if (name == "premature"):
            return self.patient.premature
        if (name == "abortions"):
            return self.patient.abortions
        if (name == "stillbirths"):
            return self.patient.stillbirths

    # Retrieve Blood type and Rh and Hemoglobin
    def patient_blood_info(self, name):
        if (name == "blood_type"):
            return self.patient.blood_type
        if (name == "rh"):
            return self.patient.rh
        if (name == "hb"):
            return self.patient.hb

    # Show the values from patient upon entering the history
    @fields.depends(
        'patient',
        '_parent_patient.gravida',
        '_parent_patient.premature',
        '_parent_patient.abortions',
        '_parent_patient.stillbirths',
        '_parent_patient.blood_type',
        '_parent_patient.rh',
        '_parent_patient.hb')
    def on_change_patient(self):
        # Obsterics info
        self.gravidae = self.patient and self.patient.gravida
        self.premature = self.patient and self.patient.premature
        self.abortions = self.patient and self.patient.abortions
        self.stillbirths = self.patient and self.patient.stillbirths
        # Rh
        self.blood_type = self.patient and self.patient.blood_type
        self.rh = self.patient and self.patient.rh
        # Hb
        self.hb = self.patient and self.patient.hb

    @fields.depends('current_pregnancy', 'pregnancy_end_date', 'lmp')
    def on_change_pregnancy_end_date(self):
        '''Calculates the gestational weeks at the end of pregnancy
            based on the delivery date
            and the LMP when the setting the delivery date
            It works when LMP and pregnancy end date are set.
        '''
        if self.pregnancy_end_date and self.lmp:
            gestational_age = datetime.datetime.date(
                self.pregnancy_end_date) - self.lmp
            self.reverse_weeks = int((gestational_age.days) / 7)

    @classmethod
    def validate(cls, pregnancies):
        super(PatientPregnancy, cls).validate(pregnancies)
        for pregnancy in pregnancies:
            pregnancy.check_patient_current_pregnancy()

    def check_patient_current_pregnancy(self):
        ''' Check for only one current pregnancy in the patient '''
        pregnancy = Table('gnuhealth_patient_pregnancy')
        cursor = Transaction().connection.cursor()
        patient_id = int(self.patient.id)
        cursor.execute(*pregnancy.select(Count(pregnancy.patient),
                       where=(pregnancy.current_pregnancy == 'true') &
            (pregnancy.patient == patient_id)))

        records = cursor.fetchone()[0]
        if records > 1:
            raise PatientAlreadyPregnant(
                gettext('health_gyneco.msg_patient_already_pregnant'))

    @staticmethod
    def default_current_pregnancy():
        """ By default, GH will record the obstetric history of the
            patient. If we want to enter the information for the current
            pregnancy, we set the current_pregnancy field
        """
        return False

    @staticmethod
    def default_institution():
        return get_institution()

    @staticmethod
    def default_healthprof():
        return get_health_professional()

    @fields.depends('reverse_weeks', 'pregnancy_end_date')
    def on_change_with_lmp(self):
        '''
        Calculates the estimate on Last Menstrual Period
        using the reverse input method, taking the
        end of pregnancy date and number of weeks
        '''
        if (self.reverse_weeks and self.pregnancy_end_date):
            estimated_lmp = datetime.datetime.date(
                self.pregnancy_end_date -
                datetime.timedelta(self.reverse_weeks * 7))

            return estimated_lmp

    def get_pregnancy_data(self, name):
        """ Calculate the Pregnancy Due Date and the Number of
        weeks at the end of pregnancy when using the Last Menstrual
        Period parameter.
        It's not calculated when using the reverse input method
        """
        if (self.lmp):
            if name == 'pdd':
                return self.lmp + datetime.timedelta(days=280)
            if name == 'pregnancy_current_week':
                if self.current_pregnancy:
                    today = datetime.date.today()
                    weeks = int(((today - self.lmp).days) / 7)
                    return weeks
                if self.reverse_weeks:
                    return self.reverse_weeks

                    gestational_age = datetime.datetime.date(
                        self.pregnancy_end_date) - self.lmp
                    return int((gestational_age.days) / 7)
                else:
                    return 0

    def get_warn_icon(self, name):
        if self.warning:
            return 'gnuhealth-warning'

    @classmethod
    def search_rec_name(cls, name, clause):
        """ Include searching by the newborn
        """
        if clause[1].startswith('!') or clause[1].startswith('not '):
            bool_op = 'AND'
        else:
            bool_op = 'OR'
        return [bool_op,
                ('pregnancy_result.newborn',) + tuple(clause[1:]),
                ]

    @classmethod
    def __register__(cls, module):
        table_h = cls.__table_handler__(module)

        # Migration from 4.4: rename name to patient
        if (table_h.column_exist('name')
                and not table_h.column_exist('patient')):
            table_h.column_rename('name', 'patient')

        super().__register__(module)
        table_h = cls.__table_handler__(module)

    @classmethod
    def __setup__(cls):
        super(PatientPregnancy, cls).__setup__()
        t = cls.__table__()
        cls._sql_constraints += [
            ('gravida_uniq', Unique(t, t.patient, t.gravida),
             'This pregnancy code for this patient already exists'),
        ]
        cls._order.insert(0, ('lmp', 'DESC'))


class PrenatalEvaluation(ModelSQL, ModelView):
    'Prenatal and Antenatal Evaluations'
    __name__ = 'gnuhealth.patient.prenatal.evaluation'

    pregnancy = fields.Many2One(
        'gnuhealth.patient.pregnancy', 'Patient Pregnancy')
    evaluation = fields.Many2One(
        'gnuhealth.patient.evaluation',
        'Patient Evaluation', readonly=True)
    evaluation_date = fields.DateTime('Date', required=True)
    gestational_weeks = fields.Function(
        fields.Integer('Gestational Weeks'),
        'get_patient_evaluation_data')
    gestational_days = fields.Function(
        fields.Integer('Gestational days'),
        'get_patient_evaluation_data')
    hypertension = fields.Boolean(
        'Hypertension', help='Check this box if the'
        ' mother has hypertension')
    preeclampsia = fields.Boolean(
        'Preeclampsia', help='Check this box if the'
        ' mother has pre-eclampsia')
    overweight = fields.Boolean(
        'Overweight', help='Check this box if the'
        ' mother is overweight or obesity')
    diabetes = fields.Boolean(
        'Diabetes', help='Check this box if the mother'
        ' has glucose intolerance or diabetes')
    invasive_placentation = fields.Selection([
        (None, ''),
        ('normal', 'Normal decidua'),
        ('accreta', 'Accreta'),
        ('increta', 'Increta'),
        ('percreta', 'Percreta'),
    ], 'Placentation', sort=False)
    placenta_previa = fields.Boolean('Placenta Previa')
    vasa_previa = fields.Boolean('Vasa Previa')
    fundal_height = fields.Integer(
        'Fundal Height',
        help="Distance between the symphysis pubis and the uterine fundus "
        "(S-FD) in cm")
    fetus_heart_rate = fields.Integer(
        'Fetus heart rate', help='Fetus heart'
        ' rate')
    efw = fields.Integer('EFW', help="Estimated Fetal Weight")
    fetal_bpd = fields.Integer('BPD', help="Fetal Biparietal Diameter")
    fetal_ac = fields.Integer('AC', help="Fetal Abdominal Circumference")
    fetal_hc = fields.Integer('HC', help="Fetal Head Circumference")
    fetal_fl = fields.Integer('FL', help="Fetal Femur Length")
    oligohydramnios = fields.Boolean('Oligohydramnios')
    polihydramnios = fields.Boolean('Polihydramnios')
    iugr = fields.Boolean('IUGR', help="Intra Uterine Growth Restriction")

    urinary_activity_signs = fields.Boolean(
        "SUA",
        help="Signs of Urinary System Activity")

    digestive_activity_signs = fields.Boolean(
        "SDA",
        help="Signs of Digestive System Activity")

    notes = fields.Text("Notes")

    institution = fields.Many2One('gnuhealth.institution', 'Institution')

    healthprof = fields.Many2One(
        'gnuhealth.healthprofessional', 'Health Prof', readonly=True,
        help="Health Professional in charge, or that who entered the "
        "information in the system.")

    @staticmethod
    def default_institution():
        return get_institution()

    @staticmethod
    def default_healthprof():
        return get_health_professional()

    def get_patient_evaluation_data(self, name):
        if name == 'gestational_weeks':
            gestational_age = datetime.datetime.date(self.evaluation_date) - \
                self.pregnancy.lmp
            return int((gestational_age.days) / 7)
        if name == 'gestational_days':
            gestational_age = datetime.datetime.date(self.evaluation_date) - \
                self.pregnancy.lmp
            return gestational_age.days

    @classmethod
    def __register__(cls, module):
        table_h = cls.__table_handler__(module)

        # Migration from 4.4: rename name to pregnancy
        if (table_h.column_exist('name')
                and not table_h.column_exist('pregnancy')):
            table_h.column_rename('name', 'pregnancy')

        super().__register__(module)
        table_h = cls.__table_handler__(module)


class PuerperiumMonitor(ModelSQL, ModelView):
    'Puerperium Monitor'
    __name__ = 'gnuhealth.puerperium.monitor'

    pregnancy = fields.Many2One(
        'gnuhealth.patient.pregnancy', 'Patient Pregnancy')
    date = fields.DateTime('Date and Time', required=True)
    # Deprecated in 1.6.4 All the clinical information will be taken at the
    # main evaluation.
    # systolic / diastolic / frequency / temperature
    systolic = fields.Integer('Systolic Pressure')
    diastolic = fields.Integer('Diastolic Pressure')
    frequency = fields.Integer('Heart Frequency')
    temperature = fields.Float('Temperature')
    lochia_amount = fields.Selection([
        (None, ''),
        ('n', 'normal'),
        ('e', 'abundant'),
        ('h', 'hemorrhage'),
    ], 'Lochia amount', sort=False)
    lochia_color = fields.Selection([
        (None, ''),
        ('r', 'rubra'),
        ('s', 'serosa'),
        ('a', 'alba'),
    ], 'Lochia color', sort=False)
    lochia_odor = fields.Selection([
        (None, ''),
        ('n', 'normal'),
        ('o', 'offensive'),
    ], 'Lochia odor', sort=False)
    uterus_involution = fields.Integer(
        'Fundal Height',
        help="Distance between the symphysis pubis and the uterine fundus "
        "(S-FD) in cm")

    institution = fields.Many2One('gnuhealth.institution', 'Institution')

    healthprof = fields.Many2One(
        'gnuhealth.healthprofessional', 'Health Prof', readonly=True,
        help="Health Professional in charge, or that who entered the "
        "information in the system.")

    @staticmethod
    def default_institution():
        return get_institution()

    @staticmethod
    def default_healthprof():
        return get_health_professional()

    @classmethod
    def __register__(cls, module):
        table_h = cls.__table_handler__(module)

        # Migration from 4.4: rename name to pregnancy
        if (table_h.column_exist('name')
                and not table_h.column_exist('pregnancy')):
            table_h.column_rename('name', 'pregnancy')

        super().__register__(module)
        table_h = cls.__table_handler__(module)


class Perinatal(ModelSQL, ModelView):
    'Perinatal Information'
    __name__ = 'gnuhealth.perinatal'

    pregnancy = fields.Many2One(
        'gnuhealth.patient.pregnancy', 'Patient Pregnancy')
    admission_code = fields.Char('Code')
    # 1.6.4 Gravida number and abortion information go now in the pregnancy
    # header. It will be calculated as a function if needed
    gravida_number = fields.Integer('Gravida #')
    # Deprecated. Use End of Pregnancy as a general concept in the pregnancy
    # model
    # Abortion / Stillbirth / Live Birth
    abortion = fields.Boolean('Abortion')
    stillbirth = fields.Boolean('Stillbirth')
    admission_date = fields.DateTime(
        'Admission',
        help="Date when she was admitted to give birth", required=True)
    # Prenatal evaluations deprecated in 1.6.4. Will be computed automatically
    prenatal_evaluations = fields.Integer(
        'Prenatal evaluations',
        help="Number of visits to the doctor during pregnancy")
    start_labor_mode = fields.Selection([
        (None, ''),
        ('v', 'Vaginal - Spontaneous'),
        ('ve', 'Vaginal - Vacuum Extraction'),
        ('vf', 'Vaginal - Forceps Extraction'),
        ('c', 'C-section'),
    ], 'Delivery mode', sort=False)
    gestational_weeks = fields.Function(
        fields.Integer('Gestational wks'),
        'get_perinatal_information')
    gestational_days = fields.Integer('Days')
    fetus_presentation = fields.Selection([
        (None, ''),
        ('cephalic', 'Cephalic'),
        ('breech', 'Breech'),
        ('shoulder', 'Shoulder'),
    ], 'Fetus Presentation', sort=False)
    dystocia = fields.Boolean('Dystocia')
    placenta_incomplete = fields.Boolean(
        'Incomplete', help='Incomplete Placenta')
    placenta_retained = fields.Boolean('Retained', help='Retained Placenta')
    abruptio_placentae = fields.Boolean(
        'Abruptio Placentae',
        help='Abruptio Placentae')
    episiotomy = fields.Boolean('Episiotomy')
    # Vaginal tearing and forceps variables are deprecated in 1.6.4.
    # They are included in laceration and delivery mode respectively
    vaginal_tearing = fields.Boolean('Vaginal tearing')
    forceps = fields.Boolean('Forceps')
    monitoring = fields.One2Many(
        'gnuhealth.perinatal.monitor', 'perinatal',
        'Monitors')
    laceration = fields.Selection([
        (None, ''),
        ('perineal', 'Perineal'),
        ('vaginal', 'Vaginal'),
        ('cervical', 'Cervical'),
        ('broad_ligament', 'Broad Ligament'),
        ('vulvar', 'Vulvar'),
        ('rectal', 'Rectal'),
        ('bladder', 'Bladder'),
        ('urethral', 'Urethral'),
    ], 'Lacerations', sort=False)
    hematoma = fields.Selection([
        (None, ''),
        ('vaginal', 'Vaginal'),
        ('vulvar', 'Vulvar'),
        ('retroperitoneal', 'Retroperitoneal'),
    ], 'Hematoma', sort=False)
    notes = fields.Text('Notes')

    institution = fields.Many2One('gnuhealth.institution', 'Institution')

    healthprof = fields.Many2One(
        'gnuhealth.healthprofessional', 'Health Prof', readonly=True,
        help="Health Professional in charge, or that who entered the "
        "information in the system.")

    @staticmethod
    def default_institution():
        return get_institution()

    @staticmethod
    def default_healthprof():
        return get_health_professional()

    def get_perinatal_information(self, name):
        if name == 'gestational_weeks':
            gestational_age = datetime.datetime.date(self.admission_date) - \
                self.pregnancy.lmp
            return int((gestational_age.days) / 7)

    @classmethod
    def __register__(cls, module):
        table_h = cls.__table_handler__(module)

        # Migration from 4.4: rename name to pregnancy
        if (table_h.column_exist('name')
                and not table_h.column_exist('pregnancy')):
            table_h.column_rename('name', 'pregnancy')

        super().__register__(module)
        table_h = cls.__table_handler__(module)


class PerinatalMonitor(ModelSQL, ModelView):
    'Perinatal Monitor'
    __name__ = 'gnuhealth.perinatal.monitor'

    perinatal = fields.Many2One(
        'gnuhealth.perinatal',
        'Patient Perinatal Evaluation')
    date = fields.DateTime('Date and Time')
    systolic = fields.Integer('Systolic Pressure')
    diastolic = fields.Integer('Diastolic Pressure')
    contractions = fields.Integer('Contractions')
    frequency = fields.Integer('Mother\'s Heart Frequency')
    dilation = fields.Integer('Cervix dilation')
    f_frequency = fields.Integer('Fetus Heart Frequency')
    meconium = fields.Boolean('Meconium')
    bleeding = fields.Boolean('Bleeding')
    fundal_height = fields.Integer('Fundal Height')
    fetus_position = fields.Selection([
        (None, ''),
        ('o', 'Occiput / Cephalic Posterior'),
        ('fb', 'Frank Breech'),
        ('cb', 'Complete Breech'),
        ('t', 'Transverse Lie'),
        ('flb', 'Footling Breech'),
    ], 'Fetus Position', sort=False)

    @classmethod
    def __register__(cls, module):
        table_h = cls.__table_handler__(module)

        # Migration from 4.4: rename name to perinatal
        if (table_h.column_exist('name')
                and not table_h.column_exist('perinatal')):
            table_h.column_rename('name', 'perinatal')

        super().__register__(module)
        table_h = cls.__table_handler__(module)


class PregnancyResult(ModelSQL, ModelView):
    'Pregnancy Result'
    __name__ = 'gnuhealth.pregnancy.result'

    pregnancy = fields.Many2One(
        'gnuhealth.patient.pregnancy', 'Patient Pregnancy')

    result = fields.Selection([
        (None, ''),
        ('live_birth', 'Live birth'),
        ('abortion', 'Abortion'),
        ('stillbirth', 'Stillbirth'),
        ('status_unknown', 'Status unknown'),
    ], 'Result', sort=False)

    newborn = fields.Many2One(
        'party.party', 'Newborn',
        domain=[
            ('is_person', '=', True),
            ('dob', '=', Eval('dob')),
            ],
        depends=['pregnancy', 'dob'])

    dob = fields.Function(fields.Date('Date of birth'), 'get_dob')
    delivery_mode = fields.Selection([
        (None, ''),
        ('v', 'Vaginal - Spontaneous'),
        ('ve', 'Vaginal - Vacuum Extraction'),
        ('vf', 'Vaginal - Forceps Extraction'),
        ('c', 'C-section'),
    ], 'Delivery mode', sort=False)

    labor_time = fields.Integer(
        'Labor time', help="Total labor time in hours passive + active")

    short_comment = fields.Char(
        'Comments', help="Short extra information")

    def get_dob(self, name):
        if self.pregnancy and self.pregnancy.pregnancy_end_date:
            return self.pregnancy.pregnancy_end_date.date()

    # Retrieve date of birth upon entering the pregnancy
    @fields.depends(
        'pregnancy', '_parent_pregnancy.pregnancy_end_date')
    def on_change_pregnancy(self):
        if self.pregnancy and self.pregnancy.pregnancy_end_date:
            return self.pregnancy.pregnancy_end_date.date()

    # Get the baby date of birth from pregnancy end date
    @fields.depends(
        'result', 'pregnancy', '_parent_pregnancy.pregnancy_end_date')
    def on_change_result(self):
        if (self.pregnancy):
            self.dob = self.pregnancy.pregnancy_end_date.date()

    @classmethod
    def __setup__(cls):
        super(PregnancyResult, cls).__setup__()
        t = cls.__table__()
        cls._sql_constraints += [
            ('newborn_uniq', Unique(t, t.newborn),
             'Our records show that the newborn is from another pregnancy'),
        ]


class GnuHealthPatient(metaclass=PoolMeta):

    """Add to the Medical patient_data class (gnuhealth.patient) the
      gynecological and obstetric fields.
    """
    __name__ = 'gnuhealth.patient'

    currently_pregnant = fields.Function(
        fields.Boolean('Pregnant'),
        'get_pregnancy_info')
    fertile = fields.Boolean(
        'Fertile',
        help="Check if patient is in fertile age")
    menarche = fields.Integer('Menarche age')
    menopausal = fields.Boolean('Menopausal')
    menopause = fields.Integer('Menopause age')
    mammography = fields.Boolean(
        'Mammography',
        help="Check if the patient does periodic mammographys")
    mammography_last = fields.Date(
        'Last mammography',
        help="Enter the date of the last mammography")
    breast_self_examination = fields.Boolean(
        'Breast self-examination',
        help="Check if patient does and knows how to self examine her breasts")
    pap_test = fields.Boolean(
        'PAP test',
        help="Check if patient does periodic cytologic pelvic smear screening")
    pap_test_last = fields.Date(
        'Last PAP test',
        help="Enter the date of the last Papanicolau test")
    colposcopy = fields.Boolean(
        'Colposcopy',
        help="Check if the patient has done a colposcopy exam")
    colposcopy_last = fields.Date(
        'Last colposcopy',
        help="Enter the date of the last colposcopy")
    # From version 2.6 Gravida, premature, abortions and stillbirths are now
    # functional fields, computed from the obstetric information
    gravida = fields.Function(fields.Integer(
        'Pregnancies',
        help="Number of pregnancies, computed from Obstetric history"),
        'patient_obstetric_info')
    premature = fields.Function(fields.Integer(
        'Premature',
        help="Preterm < 37 wks live births"), 'patient_obstetric_info')

    abortions = fields.Function(
        fields.Integer('Abortions'),
        'patient_obstetric_info')
    stillbirths = fields.Function(
        fields.Integer('Stillbirths'),
        'patient_obstetric_info')

    full_term = fields.Integer('Full Term', help="Full term pregnancies")
    # GPA Deprecated in 1.6.4. It will be used as a function or report from the
    # other fields
    #    gpa = fields.Char('GPA',
    #        help="Gravida, Para, Abortus Notation. For example G4P3A1 : 4 "
    #        "Pregnancies, 3 viable and 1 abortion")
    # Deprecated. The born alive number will be calculated from pregnancies -
    # abortions - stillbirths
    #    born_alive = fields.Integer('Born Alive')
    # Deceased in 1st week or after 2nd weeks are deprecated since 1.6.4 .
    # The information will be retrieved from the neonatal or infant record
    #    deaths_1st_week = fields.Integer('Deceased during 1st week',
    #        help="Number of babies that die in the first week")
    #    deaths_2nd_week = fields.Integer('Deceased after 2nd week',
    #        help="Number of babies that die after the second week")
    # Perinatal Deprecated since 1.6.4 - Included in the obstetric history
    #    perinatal = fields.One2Many('gnuhealth.perinatal', 'name',
    #        'Perinatal Info')
    menstrual_history = fields.One2Many(
        'gnuhealth.patient.menstrual_history',
        'patient', 'Menstrual History')
    mammography_history = fields.One2Many(
        'gnuhealth.patient.mammography_history',
        'patient', 'Mammography History',
        states={'invisible': Not(Bool(Eval('mammography')))},
    )
    pap_history = fields.One2Many(
        'gnuhealth.patient.pap_history', 'patient',
        'PAP smear History',
        states={'invisible': Not(Bool(Eval('pap_test')))},
    )
    colposcopy_history = fields.One2Many(
        'gnuhealth.patient.colposcopy_history', 'patient',
        'Colposcopy History',
        states={'invisible': Not(Bool(Eval('colposcopy')))},
    )
    pregnancy_history = fields.One2Many(
        'gnuhealth.patient.pregnancy', 'patient',
        'Pregnancies')

    def get_pregnancy_info(self, name):
        if name == 'currently_pregnant':
            for pregnancy_history in self.pregnancy_history:
                if pregnancy_history.current_pregnancy:
                    return True
        return False

    def patient_obstetric_info(self, name):
        ''' Return the number of pregnancies, perterm,
        abortion and stillbirths '''

        counter = 0
        pregnancies = len(self.pregnancy_history)
        if (name == "gravida"):
            return pregnancies

        if (name == "premature"):
            prematures = 0
            while counter < pregnancies:
                result = self.pregnancy_history[counter].pregnancy_end_result
                preg_weeks = self.pregnancy_history[counter].reverse_weeks
                if (result == "live_birth" and preg_weeks):
                    if preg_weeks < 37:
                        prematures = prematures + 1
                counter = counter + 1
            return prematures

        if (name == "abortions"):
            abortions = 0
            while counter < pregnancies:
                result = self.pregnancy_history[counter].pregnancy_end_result
                if (result == "abortion"):
                    abortions = abortions + 1
                counter = counter + 1

            return abortions

        if (name == "stillbirths"):
            stillbirths = 0
            while counter < pregnancies:
                result = self.pregnancy_history[counter].pregnancy_end_result
                if (result == "stillbirth"):
                    stillbirths = stillbirths + 1
                counter = counter + 1
            return stillbirths

    @classmethod
    def view_attributes(cls):
        return super(GnuHealthPatient, cls).view_attributes() + [
            ('//page[@id="page_gyneco_obs"]', 'states', {
                'invisible': Equal(Eval('biological_sex'), 'm'),
            })]


class PatientMenstrualHistory(ModelSQL, ModelView):
    'Menstrual History'
    __name__ = 'gnuhealth.patient.menstrual_history'

    patient = fields.Many2One(
        'gnuhealth.patient', 'Patient', readonly=True, required=True)
    evaluation = fields.Many2One(
        'gnuhealth.patient.evaluation', 'Evaluation',
        domain=[('patient', '=', Eval('patient'))],
        depends=['patient'])
    evaluation_date = fields.Date(
        'Date', help="Evaluation Date",
        required=True)
    lmp = fields.Date('LMP', help="Last Menstrual Period", required=True)
    lmp_length = fields.Integer('Length', required=True)
    is_regular = fields.Boolean('Regular')
    dysmenorrhea = fields.Boolean('Dysmenorrhea')
    frequency = fields.Selection([
        ('amenorrhea', 'amenorrhea'),
        ('oligomenorrhea', 'oligomenorrhea'),
        ('eumenorrhea', 'eumenorrhea'),
        ('polymenorrhea', 'polymenorrhea'),
    ], 'frequency', sort=False)
    volume = fields.Selection([
        ('hypomenorrhea', 'hypomenorrhea'),
        ('normal', 'normal'),
        ('menorrhagia', 'menorrhagia'),
    ], 'volume', sort=False)

    institution = fields.Many2One('gnuhealth.institution', 'Institution')

    healthprof = fields.Many2One(
        'gnuhealth.healthprofessional', 'Reviewed', readonly=True,
        help="Health Professional who reviewed the information")

    @staticmethod
    def default_institution():
        return get_institution()

    @staticmethod
    def default_healthprof():
        return get_health_professional()

    @staticmethod
    def default_evaluation_date():
        return Pool().get('ir.date').today()

    @staticmethod
    def default_frequency():
        return 'eumenorrhea'

    @staticmethod
    def default_volume():
        return 'normal'

    @classmethod
    def __register__(cls, module):
        table_h = cls.__table_handler__(module)

        # Migration from 4.4: rename name to patient
        if (table_h.column_exist('name')
                and not table_h.column_exist('patient')):
            table_h.column_rename('name', 'patient')

        super().__register__(module)
        table_h = cls.__table_handler__(module)


class PatientMammographyHistory(ModelSQL, ModelView):
    'Mammography History'
    __name__ = 'gnuhealth.patient.mammography_history'

    patient = fields.Many2One(
        'gnuhealth.patient', 'Patient', readonly=True, required=True)
    evaluation = fields.Many2One(
        'gnuhealth.patient.evaluation', 'Evaluation',
        domain=[('patient', '=', Eval('patient'))],
        depends=['patient'])
    evaluation_date = fields.Date('Date', help="Date", required=True)
    last_mammography = fields.Date('Previous', help="Last Mammography")
    result = fields.Selection([
        (None, ''),
        ('normal', 'normal'),
        ('abnormal', 'abnormal'),
    ], 'result',
        help="Please check the lab test results if the module is "
        "installed", sort=False)
    comments = fields.Char('Remarks')

    institution = fields.Many2One('gnuhealth.institution', 'Institution')

    healthprof = fields.Many2One(
        'gnuhealth.healthprofessional', 'Reviewed', readonly=True,
        help="Health Professional who last reviewed the test")

    @staticmethod
    def default_institution():
        return get_institution()

    @staticmethod
    def default_healthprof():
        return get_health_professional()

    @staticmethod
    def default_evaluation_date():
        return Pool().get('ir.date').today()

    @staticmethod
    def default_last_mammography():
        return Pool().get('ir.date').today()

    @classmethod
    def __register__(cls, module):
        table_h = cls.__table_handler__(module)

        # Migration from 4.4: rename name to patient
        if (table_h.column_exist('name')
                and not table_h.column_exist('patient')):
            table_h.column_rename('name', 'patient')

        super().__register__(module)
        table_h = cls.__table_handler__(module)


class PatientPAPHistory(ModelSQL, ModelView):
    'PAP Test History'
    __name__ = 'gnuhealth.patient.pap_history'

    patient = fields.Many2One(
        'gnuhealth.patient', 'Patient', readonly=True, required=True)
    evaluation = fields.Many2One(
        'gnuhealth.patient.evaluation', 'Evaluation',
        domain=[('patient', '=', Eval('patient'))],
        depends=['patient'])
    evaluation_date = fields.Date('Date', help="Date", required=True)
    last_pap = fields.Date('Previous', help="Last Papanicolau")
    result = fields.Selection([
        (None, ''),
        ('negative', 'Negative'),
        ('c1', 'ASC-US'),
        ('c2', 'ASC-H'),
        ('g1', 'ASG'),
        ('c3', 'LSIL'),
        ('c4', 'HSIL'),
        ('g4', 'AIS'),
    ], 'result', help="Please check the lab results if the module is "
        "installed", sort=False)
    comments = fields.Char('Remarks')

    institution = fields.Many2One('gnuhealth.institution', 'Institution')

    healthprof = fields.Many2One(
        'gnuhealth.healthprofessional', 'Reviewed', readonly=True,
        help="Health Professional who last reviewed the test")

    @staticmethod
    def default_institution():
        return get_institution()

    @staticmethod
    def default_healthprof():
        return get_health_professional()

    @staticmethod
    def default_evaluation_date():
        return Pool().get('ir.date').today()

    @staticmethod
    def default_last_pap():
        return Pool().get('ir.date').today()

    @classmethod
    def __register__(cls, module):
        table_h = cls.__table_handler__(module)

        # Migration from 4.4: rename name to patient
        if (table_h.column_exist('name')
                and not table_h.column_exist('patient')):
            table_h.column_rename('name', 'patient')

        super().__register__(module)
        table_h = cls.__table_handler__(module)


class PatientColposcopyHistory(ModelSQL, ModelView):
    'Colposcopy History'
    __name__ = 'gnuhealth.patient.colposcopy_history'

    patient = fields.Many2One(
        'gnuhealth.patient', 'Patient', readonly=True, required=True)
    evaluation = fields.Many2One(
        'gnuhealth.patient.evaluation', 'Evaluation',
        domain=[('patient', '=', Eval('patient'))],
        depends=['patient'])
    evaluation_date = fields.Date('Date', help="Date", required=True)
    last_colposcopy = fields.Date('Previous', help="Last colposcopy")
    result = fields.Selection([
        (None, ''),
        ('normal', 'normal'),
        ('abnormal', 'abnormal'),
    ], 'result',
        help="Please check the lab test results if the module is "
        "installed", sort=False)
    comments = fields.Char('Remarks')

    institution = fields.Many2One('gnuhealth.institution', 'Institution')

    healthprof = fields.Many2One(
        'gnuhealth.healthprofessional', 'Reviewed', readonly=True,
        help="Health Professional who last reviewed the test")

    @staticmethod
    def default_institution():
        return get_institution()

    @staticmethod
    def default_healthprof():
        return get_health_professional()

    @staticmethod
    def default_evaluation_date():
        return Pool().get('ir.date').today()

    @staticmethod
    def default_last_colposcopy():
        return Pool().get('ir.date').today()

    @classmethod
    def __register__(cls, module):
        table_h = cls.__table_handler__(module)

        # Migration from 4.4: rename name to patient
        if (table_h.column_exist('name')
                and not table_h.column_exist('patient')):
            table_h.column_rename('name', 'patient')

        super().__register__(module)
        table_h = cls.__table_handler__(module)
