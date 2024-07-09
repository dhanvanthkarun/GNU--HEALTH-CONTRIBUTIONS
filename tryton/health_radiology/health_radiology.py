
# SPDX-FileCopyrightText:  2024 - Wei Zhao <wei.zhao@uclouvain.be>
# SPDX-License-Identifier: GPL-3.0-or-later

#########################################################################
#   Hospital Management Information System (HMIS) component of the      #
#                       GNU Health project                              #
#                   https://www.gnuhealth.org                           #
#########################################################################
#                     HEALTH RADIOLOGY package                          #
#                   health_radiology.py: Main module                    #
#########################################################################

from urllib.parse import urljoin
import logging
from trytond.model import ModelView, ModelSQL, fields, Unique
from trytond.pool import PoolMeta, Pool
from trytond.exceptions import UserError
from pyorthanc import Orthanc
from lxml import etree

__all__ = [
    'PatientData',
    'PatientOrthancStudy',
    'StudySeries',
    'SeriesInstances']

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

#
# The GNU Health patient with his image data stored on the orthanc server.
#


class PatientData (metaclass=PoolMeta):
    __name__ = 'gnuhealth.patient'

    radiology_studies = fields.One2Many(
        'gnuhealth.radiology.study', 'patient', 'Study')

#
# The image study data. One patient can have multiple studies.
# In one study, there are several series with different modalities
# (CT, MRI, PET, RTStruct, RTPlan..)
#


class PatientOrthancStudy(ModelSQL, ModelView):
    'Patient Orthanc Study'
    __name__ = "gnuhealth.radiology.study"

    patient = fields.Many2One(
        'gnuhealth.patient', 'Patient',
        select=True, help='Patient Name',
        readonly=False)

    date = fields.Char('Date', required=False, readonly=True)

    patient_name = fields.Char(
        'Orthanc Patient',
        required=True, readonly=True)

    study_instance_UID = fields.Char(
        'Study UID',
        required=True, readonly=True)

    orthanc_UID = fields.Char(
        'Orthanc UID',
        readonly=True, required=True)

    institution = fields.Char('Institution', readonly=True)
    performing_physician_name = fields.Char('Physician', readonly=True)

    series = fields.One2Many(
        'gnuhealth.radiology.study_series',
        'study', 'Study Series')

    server = fields.Char('Server', readonly=True, required=True)

    ohif_viewer_link = fields.Function(
        fields.Char(
            "OHIF Viewer",
            help="Link to Orthanc OHIF Viewer"),
        "get_ohif_viewer_link")

    stone_viewer_link = fields.Function(
        fields.Char(
            "Stone Viewer",
            help="Link to Orthanc Stone Viewer"),
        "get_stone_viewer_link")

    gnu_patient_name = fields.Function(
        fields.Char('Health Patient'),
        "get_gnu_patient")

    notes = fields.Text(
        "Study notes",
        help='Extra Information',
        readonly=False)

    @classmethod
    def __setup__(cls):
        # Setup the patient orthanc study class with additional buttons
        # for deleting a study and selecting a viewer.
        super(PatientOrthancStudy, cls).__setup__()
        t = cls.__table__()
        cls._buttons.update({
            'delete_study': {}
        })

        cls._sql_constraints = [
            ('studyUID_unique', Unique(t, t.study_instance_UID, t.server),
             ("There is already a study with the same UID. "
              "Use the \"Get New studies\" action to get "
              "the latest list of studies from the Orthanc servers "
              "to see whether there is already a study with the same UID."))  # noqa E501
        ]

        cls._order.insert(0, ('patient_name', 'ASC'))

    def get_gnu_patient(self, name):
        """
        Retrieves the GNU patient with the given name.

        Parameters:
            name (str): The name of the patient to retrieve.

        Returns:
            str or None: The name of the patient if found, None otherwise.
        """
        if self.patient is None:
            return None
        else:
            return self.patient.rec_name

    def get_ohif_viewer_link(self, name):
        """
        Get the link for the OHIF viewer and study, based on the server,
        study_instance_UID, and orthanc_UID.
        """
        pre = "".join([self.server.rstrip("/"), "/"])
        url = urljoin(pre, (
            'ohif/viewer?url=../studies/' +
            f'{self.orthanc_UID}/ohif-dicom-json'))  # noqa E501
        return url

    def get_stone_viewer_link(self, name):
        """
        Get the link for the stone viewer and study, based on the
        server and study instance UID.  # noqa E501
        """
        pre = "".join([self.server.rstrip("/"), "/"])
        url = urljoin(pre, (
            'stone-webviewer/index.html?' +
            f'study={self.study_instance_UID}'))  # noqa E501
        return url

    @classmethod
    @ModelView.button
    def delete_study(cls, records):
        """
        Method to delete a study record from Orthanc server.
        :param records: List of study records to be deleted
        :return: 'reload' if the operation is successful
        :raises: UserError if there is an issue with the Orthanc server
        """
        records_to_delete = []
        try:
            Config = Pool().get('gnuhealth.radiology.orthanc_server_config')
            servers = Config.search([])
            for record in records:
                for conf_server in servers:
                    if conf_server.domain == record.server:
                        client = Orthanc(
                            url=conf_server.domain,
                            username=conf_server.user,
                            password=conf_server.password,
                            return_raw_response=True)
                        response = client.delete_studies_id(record.orthanc_UID)
                        if (200 <= response.status_code < 300 or
                                response.status_code == 404):
                            records_to_delete.append(record)
                        else:
                            raise UserError(
                                'Orthanc server returned HTTP code '
                                f'{response.status_code}, '
                                f'with content {response.text}',
                                description=(
                                    "Unable to delete Orthanc study. "
                                    "It may no longer exist or "
                                    "the Orthanc server "
                                    "could be in read-only mode."
                                    "Please review your "
                                    "Orthanc server configuration."))
        except Exception as exception:
            logger.error(
                'Delete Orthanc study exception: %s',
                exception,
                exc_info=True)
            raise UserError(str(exception))
        finally:
            cls.delete(records_to_delete)
            return 'reload'

    @classmethod
    def get_new_studies(cls):
        # Update the studies from the Orthanc server,
        # processing changes to studies, series, and instances.
        try:
            pool = Pool()
            Config = pool.get('gnuhealth.radiology.orthanc_server_config')
            server_configs = Config.search([])
            for server_config in server_configs:
                client = Orthanc(
                    url=server_config.domain,
                    username=server_config.user,
                    password=server_config.password)

                # get changes
                last_changed_index = (
                    server_config.last_changed_index
                    if server_config.last_changed_index is not None else -1)   # noqa E501

                new_changes = client.get_changes(
                    {"since": last_changed_index, "limit": 100000})  # noqa E501

                # process changes to studies
                new_orthanc_studyIDs = [
                    s['ID'] for s in new_changes['Changes']
                    if s['ChangeType'] == 'NewStudy'
                    or s['ChangeType'] == 'StableStudy']  # noqa E501

                cls.create_or_update_studies_from_orthanc(
                    client, server_config.domain,
                    new_orthanc_studyIDs)  # noqa E501

                # process changes to series
                new_orthanc_series_ids = [
                    s['ID'] for s in new_changes['Changes']
                    if s['ChangeType'] == 'NewSeries'
                    or s['ChangeType'] == 'StableSeries']  # noqa E501

                cls.create_or_update_series_from_orthanc(
                    client, server_config.domain,
                    new_orthanc_series_ids)  # noqa E501

                # process changes to instances
                new_orthanc_instance_ids = [
                    s['ID'] for s in new_changes['Changes']
                    if s['ChangeType'] == 'NewInstance'
                    or s['ChangeType'] == 'StableInstance']  # noqa E501

                cls.create_or_update_instances_from_orthanc(
                    client, server_config.domain,
                    new_orthanc_instance_ids)  # noqa E501

                # remember last processed change
                server_config.last_changed_index = new_changes['Last']
                Config.save([server_config])
        except Exception as exception:
            raise UserError(
                str(exception),
                description="Failed to get new changes, "
                "please check the Orthanc server")

    @classmethod
    def create_or_update_studies_from_orthanc(cls, client, server, orthanc_study_ids):  # noqa E501
        """
        Create or update radiology studies from Orthanc server "
        "based on the provided study IDs.
        """
        pool = Pool()
        Study = pool.get('gnuhealth.radiology.study')
        for orthanc_study_id in orthanc_study_ids:
            orthanc_study = client.get_studies_id(orthanc_study_id)
            dicom_tags = orthanc_study['MainDicomTags']
            patient_main_dicom_tags = orthanc_study['PatientMainDicomTags']
            study_values = {}

            # Create or update?
            gh_study = Study.search(
                [('study_instance_UID', '=',
                  dicom_tags['StudyInstanceUID']),
                 ('server', '=', server)])

            if len(gh_study) == 0:
                study_values['patient'] = None

                study_values['date'] = (
                    dicom_tags['StudyDate']
                    if 'StudyDate' in dicom_tags else "")  # noqa E501

                study_values['study_instance_UID'] = dicom_tags['StudyInstanceUID']  # noqa E501
                study_values['orthanc_UID'] = orthanc_study['ID']

                study_values['patient_name'] = (
                    patient_main_dicom_tags['PatientName']
                    if 'PatientName' in patient_main_dicom_tags else "")  # noqa E501

                study_values['institution'] = (
                    dicom_tags['InstitutionName']
                    if 'InstitutionName' in dicom_tags else "")  # noqa E501

                study_values['performing_physician_name'] = (
                    dicom_tags['ReferringPhysicianName']
                    if 'ReferringPhysicianName' else "")  # noqa E501

                study_values['server'] = server
                Study.create([study_values])
            else:
                # DICOM studies are immutable. Only the internal Orthanc ID can
                # change.
                study_values['orthanc_UID'] = orthanc_study['ID']
                Study.write(gh_study, study_values)

    @classmethod
    def create_or_update_series_from_orthanc(cls, client, server, orthanc_seriesIDs):  # noqa E501
        """
        Create or update series from Orthanc "
        "in the radiology study and series models.
        """

        pool = Pool()
        Study = pool.get('gnuhealth.radiology.study')
        Series = pool.get('gnuhealth.radiology.study_series')
        for orthanc_seriesID in orthanc_seriesIDs:
            orthanc_series = client.get_series_id(orthanc_seriesID)
            dicom_tags = orthanc_series['MainDicomTags']
            series_values = {}

            # Create or update?
            gh_series = Series.search(
                [('series_UID', '=', dicom_tags['SeriesInstanceUID']),
                 ('server', '=', server)])  # noqa E501

            if len(gh_series) == 0:
                series_values['modality'] = (
                    dicom_tags['Modality']
                    if 'Modality' in dicom_tags else "")  # noqa E501

                series_values['series_UID'] = dicom_tags['SeriesInstanceUID']
                series_values['orthanc_UID'] = orthanc_series['ID']

                series_values['series_description'] = (
                    dicom_tags['SeriesDescription']
                    if 'SeriesDescription' in dicom_tags else "")  # noqa E501

                series_values['series_number'] = (
                    dicom_tags['SeriesNumber']
                    if 'SeriesNumber' in dicom_tags else "")  # noqa E501

                gh_study = Study.search(
                    [('orthanc_UID', '=', orthanc_series['ParentStudy']),
                     ('server', '=', server)])  # noqa E501  # noqa E501

                if len(gh_study) == 0:
                    raise UserError(
                        "The study with the given Orthanc ID " +
                        "does not exist in the gnuhealth database")  # noqa E501

                Study.write(
                    gh_study, {
                        'series': [
                            ('create', [series_values])]})
            else:
                # DICOM series are immutable. Only the internal Orthanc ID can
                # change.
                series_values['orthanc_UID'] = orthanc_series['ID']
                Series.write(gh_series, series_values)

    @classmethod
    def create_or_update_instances_from_orthanc(
            cls, client, server, orthanc_instance_ids):
        """
        Create or update instances from Orthanc in the GNU Health system.
        """
        pool = Pool()
        Series = pool.get('gnuhealth.radiology.study_series')
        IInst = pool.get('gnuhealth.radiology.series_instances')
        for orthanc_instance_id in orthanc_instance_ids:
            orthanc_instance = client.get_instances_id(orthanc_instance_id)
            dicom_tags = orthanc_instance['MainDicomTags']
            instance_values = {}

            # Create or update?
            gh_instance = IInst.search(
                [('sop_instance_UID', '=', dicom_tags['SOPInstanceUID']),
                 ('server', '=', server)])  # noqa E501

            if len(gh_instance) == 0:
                instance_values['sop_instance_UID'] = dicom_tags['SOPInstanceUID']  # noqa E501
                instance_values['orthanc_UID'] = orthanc_instance['ID']

                if ('InstanceNumber' in dicom_tags
                    and dicom_tags['InstanceNumber'] != ""
                    and dicom_tags['InstanceNumber'] != None):  # noqa E501
                    instance_values['instance_number'] = int(
                        float(dicom_tags['InstanceNumber']))  # noqa E501
                else:
                    instance_values['instance_number'] = 0

                instance_values['image_position_patient'] = (
                    dicom_tags['ImagePositionPatient']
                    if 'ImagePositionPatient' in dicom_tags else "")  # noqa E501

                gh_series = Series.search(
                    [('orthanc_UID', '=', orthanc_instance['ParentSeries']),
                     ('server', '=', server)])  # noqa E501

                if len(gh_series) == 0:
                    raise UserError(
                        "The series with the given Orthanc ID "
                        "does not exist in the gnuhealth database")

                Series.write(gh_series, {'instances': [('create', [instance_values])]})  # noqa E501
            else:
                # DICOM instances are immutable. Only the internal Orthanc ID
                # can change.
                instance_values['orthanc_UID'] = orthanc_instance['ID']
                IInst.write(gh_instance, instance_values)

    @classmethod
    def full_synchronize(cls):
        """
        Updates the studies in the gnuhealth database by "
        "fetching the studies from the Orthanc servers.
        This class method fetches all the studies that are "
        "already in the gnuhealth database and compares them
        with the studies from the Orthanc servers. It then creates new studies
        in the gnuhealth database if there are any studies in the Orthanc
        servers that are not already present in the gnuhealth database.
        """
        try:
            pool = Pool()
            Study = pool.get('gnuhealth.radiology.study')
            Series = pool.get('gnuhealth.radiology.study_series')
            # IInst = pool.get('gnuhealth.radiology.series_instances')

            # Get all studies that are already in gnuhealth
            gh_studies = Study.search([])
            # Get studies from Orthanc servers
            Config = pool.get('gnuhealth.radiology.orthanc_server_config')
            servers = Config.search([])
            for server in servers:
                client = Orthanc(
                    url=server.domain,
                    username=server.user,
                    password=server.password)
                orthanc_studies = client.get_studies({'expand': True})
                for orthanc_study in orthanc_studies:
                    # Create study in gnuhealth if it does not exist
                    dicom_tags = orthanc_study['MainDicomTags']
                    gh_study = [
                        s for s in gh_studies
                        if s.study_instance_UID == dicom_tags[
                                'StudyInstanceUID']
                        and s.server == server.domain]  # noqa E501
                    if len(gh_study) == 0:
                        dicom_tags = orthanc_study['MainDicomTags']
                        patient_main_dicomTags = orthanc_study['PatientMainDicomTags']  # noqa E501
                        study_values = {}
                        study_values['patient'] = None

                        study_values['date'] = (
                            dicom_tags['StudyDate']
                            if 'StudyDate' in dicom_tags else "")  # noqa E501

                        study_values['study_instance_UID'] = dicom_tags['StudyInstanceUID']  # noqa E501
                        study_values['orthanc_UID'] = orthanc_study['ID']

                        study_values['patient_name'] = (
                            patient_main_dicomTags['PatientName']
                            if 'PatientName' in patient_main_dicomTags else "")  # noqa E501

                        study_values['institution'] = (
                            dicom_tags['InstitutionName']
                            if 'InstitutionName' in dicom_tags else "")  # noqa E501

                        study_values['performing_physician_name'] = (
                            dicom_tags['ReferringPhysicianName']
                            if 'ReferringPhysicianName' else "")  # noqa E501

                        study_values['server'] = server.domain
                        logger.error("Creating study")
                        gh_study = Study.create([study_values])
                    gh_study = gh_study[0]

                    orthanc_seriesIDs = orthanc_study['Series']
                    for orthanc_seriesID in orthanc_seriesIDs:
                        orthanc_series = client.get_series_id(orthanc_seriesID)
                        # Create series in gnuhealth if it does not exist
                        gh_series = [
                            s for s in gh_study.series
                            if s.orthanc_UID == orthanc_seriesID]
                        if len(gh_series) == 0:
                            series_values = {}
                            series_main_dicomTags = orthanc_series['MainDicomTags']  # noqa E501

                            series_values['modality'] = (
                                series_main_dicomTags['Modality']
                                if 'Modality' in series_main_dicomTags else "")  # noqa E501

                            series_values['series_UID'] = series_main_dicomTags['SeriesInstanceUID']  # noqa E501
                            series_values['orthanc_UID'] = orthanc_series['ID']

                            series_values['series_description'] = (
                                series_main_dicomTags['SeriesDescription']
                                if 'SeriesDescription' in series_main_dicomTags else "")  # noqa E501

                            series_values['series_number'] = (
                                series_main_dicomTags['SeriesNumber']
                                if 'SeriesNumber' in series_main_dicomTags else "")  # noqa E501

                            series_values['study'] = gh_study
                            logger.error("Creating series")
                            gh_series = Series.create([series_values])
                            Study.write(
                                [gh_study], {
                                    'series': [
                                        ('add', [
                                            gh_series[0].id])]})
                        gh_series = gh_series[0]

                        instance_values_to_create = []
                        for orthanc_instanceID in orthanc_series['Instances']:
                            # Create instance in gnuhealth if it does not exist
                            gh_instance = [s for s in gh_series.instances
                                           if s.orthanc_UID == orthanc_instanceID]  # noqa E501
                            if len(gh_instance) == 0:
                                orthanc_instance = client.get_instances_id(orthanc_instanceID)  # noqa E501
                                instance_values = {}
                                instance_main_dicomTags = orthanc_instance['MainDicomTags']  # noqa E501
                                instance_values['sop_instance_UID'] = instance_main_dicomTags['SOPInstanceUID']  # noqa E501
                                instance_values['orthanc_UID'] = orthanc_instance['ID']  # noqa E501
                                if ('InstanceNumber' in instance_main_dicomTags
                                    and instance_main_dicomTags[
                                        'InstanceNumber'] != ''
                                    and instance_main_dicomTags['InstanceNumber'] is not None):  # noqa E501
                                    instance_values['instance_number'] = int(
                                        float(instance_main_dicomTags['InstanceNumber']))  # noqa E501
                                else:
                                    instance_values['instance_number'] = 0
                                instance_values['image_position_patient'] = (
                                    instance_main_dicomTags[
                                        'ImagePositionPatient']
                                    if 'ImagePositionPatient' in instance_main_dicomTags else "")  # noqa E501
                                instance_values_to_create.append(instance_values)  # noqa E501
                        logger.error(
                            "Creating " +
                            str(len(instance_values_to_create)) +
                            " instances")
                        Series.write(
                            [gh_series], {
                                'instances': [
                                    ('create', instance_values_to_create)]})
        except Exception as exception:
            raise UserError(
                str(exception),
                description="Failed to update studies, "
                "pleasecheck the Orthanc server")


class StudySeries(ModelSQL, ModelView):
    'Study Series'
    __name__ = 'gnuhealth.radiology.study_series'

    study = fields.Many2One(
        'gnuhealth.radiology.study', 'Study',
        help='Patient study series',
        readonly=True,
        required=True,
        ondelete='CASCADE')

    orthanc_UID = fields.Char('Orthanc UID', readonly=True, required=True)
    series_number = fields.Char('Series No.', readonly=True)

    series_description = fields.Char(
        'Description',
        readonly=True, required=False)  # noqa E501

    series_UID = fields.Char('Series UID', readonly=True, required=True)
    modality = fields.Char('Modality', required=True, readonly=True)

    server = fields.Function(
        fields.Char(
            "Server",
            readonly=True, required=True),
        "get_study_server",
        searcher='search_study_server')

    stone_viewer_link = fields.Function(
        fields.Char(
            "Stone Viewer",
            help="Link to Orthanc Stone Viewer"),
        "get_stone_viewer_link")

    notes = fields.Text(
        "Series notes",
        help='Extra Information',
        readonly=False)

    instances = fields.One2Many(
        'gnuhealth.radiology.series_instances',
        'series',
        'Series Instance')

    @classmethod
    def __setup__(cls):
        """
        A description of the entire function, "
        "its parameters, and its return types.
        """
        super(StudySeries, cls).__setup__()
        cls._buttons.update({
            'delete_series': {},
        })

    def get_stone_viewer_link(self, name):
        """
        Get the link for the stone viewer and study, based on the
        server and study instance UID.  # noqa E501
        """
        # https://orthanc.uclouvain.be/demo/stone-webviewer/index.html?study=1.2.840.113745.101000.1008000.38179.6792.6324567&series=1.3.12.2.1107.5.1.4.36085.2.0.517109821292363

        pre = "".join([self.server.rstrip("/"), "/"])

        url = urljoin(pre, (
            'stone-webviewer/index.html?' +
            f'study={self.study.study_instance_UID}' +
            f'&series={self.series_UID}'))  # noqa E501

        return url

    def get_study_server(self, name):
        """
        Get the study server.

        Parameters:
            name (str): The name of the study.

        Returns:
            study_server: The server for the given study.
        """
        return self.study.server

    @classmethod
    def search_study_server(cls, name, clause):
        """
        Perform a search on the study server "
        "based on the provided name and clause.
        """
        res = []
        value = clause[2]
        res.append(('study.server', clause[1], value))
        return res

    def get_study_patient(self, name):
        """
        Returns the name of the patient associated with the given study.

        Parameters:
            name (str): The name of the study.

        Returns:
            str: The name of the patient associated with the study.
        """
        return self.study.patient.name

    @classmethod
    def delete(cls, seriess):
        """
        Delete a list of series and their associated studies "
        "if they have no more series.
        """
        studies = [s.study for s in seriess]
        # call original delete
        super(StudySeries, cls).delete(seriess)
        # if the study has no more series, delete the study, too
        Study = Pool().get('gnuhealth.radiology.study')
        for study in studies:
            if study and ((study.series is None) or len(study.series) == 0):
                Study.delete([study])

    @classmethod
    @ModelView.button
    def delete_series(cls, records):
        """
        A class method to delete series from the Orthanc server.
        Takes a list of records as input.
        Returns 'reload' on successful deletion.
        Raises UserError on failure with an appropriate error message.
        """
        records_to_delete = []
        try:
            Config = Pool().get('gnuhealth.radiology.orthanc_server_config')
            servers = Config.search([])
            for record in records:
                for conf_server in servers:
                    if (conf_server.domain == record.study.server):
                        client = Orthanc(
                            url=conf_server.domain,
                            username=conf_server.user,
                            password=conf_server.password,
                            return_raw_response=True)

                        response = client.delete_series_id(record.orthanc_UID)
                        if (200 <= response.status_code < 300 or
                                response.status_code == 404):
                            records_to_delete.append(record)
                        else:
                            raise UserError(
                                'Orthanc server returned HTTP code'
                                f'{response.status_code}, '
                                f'with content {response.text}',
                                description=(
                                    "Unable to delete Orthanc study"
                                    " series. It may no longer exist or"  # noqa E501
                                    " the Orthanc server could be in "
                                    "read-only mode. "
                                    "Please review your "
                                    "Orthanc server configuration."))
        except Exception as exception:
            logger.error(
                'Delete study series exception: %s',
                exception,
                exc_info=True)
            raise UserError(str(exception))
        finally:
            cls.delete(records_to_delete)
        return 'reload'
#
# All instances in the series of patient's image study.
#


class SeriesInstances(ModelSQL, ModelView):
    'Series Instance'
    __name__ = 'gnuhealth.radiology.series_instances'

    series = fields.Many2One(
        'gnuhealth.radiology.study_series',
        'Series',
        help='Study series instance',
        readonly=True,
        required=True,
        ondelete='CASCADE')

    sop_instance_UID = fields.Char(
        'SOP Instance UID',
        readonly=True,
        required=True)

    orthanc_UID = fields.Char('Orthanc UID', readonly=True, required=True)

    instance_number = fields.Integer(
        'Instance Number',
        readonly=True,
        required=False)

    image_position_patient = fields.Char(
        'Image Position', readonly=True, required=False)

    server = fields.Function(
        fields.Char(
            "Server",
            readonly=True,
            required=True),
        "get_study_server",
        searcher="search_study_server")

    image = fields.Function(
        fields.Binary("Image"),
        'get_image',
        loading='lazy')

    @classmethod
    def __setup__(cls):
        """
        Set up the SeriesInstances class.
        """
        super(SeriesInstances, cls).__setup__()

        cls._order.insert(0, ('instance_number', 'ASC'))

    def get_study_server(self, name):
        """
        Get the study server for a given name.

        :param name: The name of the study.
        :return: The server associated with the study.
        """
        return self.series.server

    @classmethod
    def search_study_server(cls, name, clause):
        """
        A class method that searches the study server "
        "based on a given name and clause.
        """
        res = []
        value = clause[2]
        res.append(('series.server', clause[1], value))
        return res

    def get_image(self, name):
        """
        A method to retrieve an image from an Orthanc server.

        :return: The image data in PNG format if successful, None otherwise.
        """
        try:
            Config = Pool().get('gnuhealth.radiology.orthanc_server_config')
            servers = Config.search([])
            for conf_server in servers:
                if conf_server.domain == self.server:
                    logger.error(conf_server.domain)
                    client = Orthanc(
                        url=conf_server.domain,
                        username=conf_server.user,
                        password=conf_server.password,
                        return_raw_response=True)
                    response = client.get_instances_id_frames_frame_rendered(
                        0, self.orthanc_UID, headers={'Accept': 'image/png'})
                    if 200 <= response.status_code < 300:
                        image_data = response.read()
                        return image_data
                    else:
                        raise UserError(
                            "Orthanc server returned HTTP code"
                            f"{response.status_code},"
                            f" with content {response.text}")
            return None
        except Exception as exception:
            logger.error('Get image of instance: %s', exception, exc_info=True)
            return None
