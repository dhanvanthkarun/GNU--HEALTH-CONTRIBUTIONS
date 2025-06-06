# SPDX-FileCopyrightText: 2008-2025 Luis Falcón <falcon@gnuhealth.org>
# SPDX-FileCopyrightText: 2011-2025 GNU Solidario <health@gnusolidario.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#########################################################################
#   Hospital Management Information System (HMIS) component of the      #
#                       GNU Health project                              #
#                   https://www.gnuhealth.org                           #
#########################################################################
#                           HEALTH package                              #
#                __init__.py: Package declaration file                  #
#########################################################################

from trytond.pool import Pool
from trytond.report import Report
from . import health
from . import sequences
from . import wizard
from . import report
from . import country


def register():
    Pool.register(
        country.Subdivision,
        health.OperationalArea,
        health.OperationalSector,
        health.DomiciliaryUnit,
        health.FederationCountryConfig,
        health.Occupation,
        health.Ethnicity,
        health.BirthCertificate,
        health.DeathCertificate,
        health.Party,
        health.ContactMechanism,
        health.PersonName,
        health.PartyAddress,
        health.DrugDoseUnits,
        health.MedicationFrequency,
        health.DrugForm,
        health.DrugRoute,
        health.MedicalSpecialty,
        health.HealthInstitution,
        health.HealthInstitutionSpecialties,
        health.HealthInstitutionOperationalSector,
        health.HealthInstitutionO2M,
        health.HospitalBuilding,
        health.HospitalUnit,
        health.HospitalOR,
        health.HospitalWard,
        health.HospitalBed,
        health.HealthProfessional,
        health.HealthProfessionalSpecialties,
        health.Family,
        health.FamilyMember,
        health.FamilyDiseases,
        health.MedicamentCategory,
        health.Medicament,
        health.ImmunizationSchedule,
        health.ImmunizationScheduleLine,
        health.ImmunizationScheduleDose,
        health.PathologyCategory,
        health.PathologyGroup,
        health.Pathology,
        health.DiseaseMembers,
        health.BirthCertExtraInfo,
        health.DeathCertExtraInfo,
        health.DeathUnderlyingCondition,
        health.ProcedureCode,
        health.InsurancePlan,
        health.Insurance,
        health.AlternativePersonID,
        health.Product,
        health.PatientData,
        health.PatientDiseaseInfo,
        health.Appointment,
        health.AppointmentReport,
        health.OpenAppointmentReportStart,
        health.PatientPrescriptionOrder,
        health.PrescriptionLine,
        health.PatientMedication,
        health.PatientVaccination,
        health.PatientProcedure,
        health.PatientEvaluation,
        health.Directions,
        health.SecondaryCondition,
        health.DiagnosticHypothesis,
        health.SignsAndSymptoms,
        health.PatientECG,
        health.ProductTemplate,
        health.PageOfLife,
        health.ProceduresConfig,
        health.Commands,
        health.Modules,
        health.Help,
        health.OnlineDocument,
        wizard.wizard_check_immunization_status.CheckImmunizationStatusInit,
        sequences.GnuHealthSequences,
        sequences.PatientSequence,
        sequences.PatientEvaluationSequence,
        sequences.AppointmentSequence,
        sequences.PrescriptionSequence,
        module='health', type_='model')

    Pool.register(
        health.OpenAppointmentReport,
        wizard.wizard_update_patient_disease_info.UpdatePatientDiseaseInfo,
        wizard.wizard_appointment_evaluation.CreateAppointmentEvaluation,
        wizard.wizard_check_immunization_status.CheckImmunizationStatus,
        module='health', type_='wizard')

    Pool.register(
        report.immunization_status_report.ImmunizationStatusReport,
        module='health', type_='report')

    Pool.register_mixin(
        report.health_report.ReportDateAndTimeMixin, Report,
        module='health')

    Pool.register_mixin(
        report.health_report.ReportImageToolMixin, Report,
        module='health')

    Pool.register_mixin(
        report.health_report.ReportGettextMixin, Report,
        module='health')
