
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
from trytond.i18n import gettext
from trytond.model import ModelView, ModelSQL, fields, Unique
from trytond.pool import PoolMeta, Pool
from trytond.exceptions import UserError
from pyorthanc import Orthanc
from lxml import etree

# from trytond.modules.health.core import get_health_professional

__all__ = ['PatientData', 'PatientOrthancStudy', 'ImagingStudySeries', 'ImagingSeriesInstances']

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
            subelem = etree.SubElement(widgets, '{http://relaxng.org/ns/structure/1.0}value')
            subelem.text = 'dicombinary'
        return rng
    
#
# The GNU Health patient with his image data stored on the orthanc server.
#
class PatientData (metaclass=PoolMeta):
    __name__ = 'gnuhealth.patient'
    
    imagingStudies = fields.One2Many(
        'gnuhealth.imaging.imagingStudy', 'patient', 'Study')  

#
# The image study data. One patient can have multiple studies.
# In one study, there are several series with different modalities (CT, MRI, PET, RTStruct, RTPlan..)
#
class PatientOrthancStudy(ModelSQL, ModelView):
    'Patient Orthanc Study'
    __name__ = "gnuhealth.imaging.imagingStudy"
    
    patient = fields.Many2One('gnuhealth.patient', 'Patient', select=True, help='Patient Name', readonly=False) 
    date = fields.Char('Date', required=False, readonly=True)
    patientName = fields.Char('Orthanc Patient', required=True, readonly=True)
    studyInstanceUID = fields.Char('Study UID', required=True, readonly=True)
    orthancUID = fields.Char('Orthanc UID', readonly=True, required=True)
    institution = fields.Char('Institution', readonly=True)
    performingPhysicianName = fields.Char('Physician', readonly=True)
    series = fields.One2Many('gnuhealth.imaging.imagingStudySeries', 'study', 'Study Series')
    server = fields.Char('Server', readonly=True, required=True)
    viewerName = fields.Selection([('stone-webviewer', 'StoneView'), ('OHIF-viewer', 'OHIF Viewer')], 'Viewer', sort=False)
    link = fields.Function(fields.Char(
        "URL",
        help="Link to Orthanc Explorer"), "get_link")
    gnuPatientName = fields.Function(fields.Char('Health Patient'), "get_gnu_patient")
    notes= fields.Text("Study notes", help='Extra Information', readonly=False)
    
    @classmethod
    def __setup__(cls):
        """
        Setup the PatientOrthancStudy class with additional buttons for deleting a study and selecting a viewer.
        """
        super(PatientOrthancStudy, cls).__setup__()
        t = cls.__table__()
        cls._buttons.update({
            'delete_study': {}
        })
        
        cls._buttons.update({
            'select_viewer': {}
        })
        
        cls._sql_constraints = [
            ('studyUID_unique', Unique(t, t.studyInstanceUID, t.server), "The studyInstanceUID must be unique")
        ]

    @classmethod
    @ModelView.button
    def select_viewer(cls, studies):
        """
        Selects the viewer for the given studies.

        Parameters:
            studies (list): A list of study objects.

        Returns:
            str: The action to be taken after selecting the viewer.
        """
        for st in studies:
            if st.viewerName == 'stone-webviewer':
                newViewerName = 'OHIF-viewer'
            else:
                newViewerName = 'stone-webviewer'   
            cls.write([st], {'viewerName': newViewerName})
        return 'reload'
    
    @fields.depends("viewerName")
    def on_change_with_link(self):
        """
        This function is a decorator that depends on the "viewerName" field. It is triggered when the value of the "viewerName" field changes.

        Parameters:
            self (object): The instance of the class.
        
        Returns:
            str: The link generated by the "get_link" method with a None parameter.
        """
        return self.get_link(None)
        
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
        
    def get_link(self, name):
        """
        Get the link for the specified viewer and study, based on the server, viewerName, studyInstanceUID, and orthancUID.

        Parameters:
            name (str): The name of the viewer.

        Returns:
            str: The generated URL for the specified viewer and study.
        """
        # Example fro stone-web
        # https://orthanc.uclouvain.be/demo/stone-webviewer/index.html?study=1.2.840.113745.101000.1008000.38179.6792.6324567
        
        # Example for ohif viewer: with ID
        # https://orthanc.uclouvain.be/demo/ohif/viewer?url=../studies/6b9e19d9-62094390-5f9ddb01-4a191ae7-9766b715/ohif-dicom-json
        
        pre = "".join([self.server.rstrip("/"), "/"])
        url = ""
        if self.viewerName == 'stone-webviewer':
            url =  urljoin(pre, f'{self.viewerName}/index.html?study={self.studyInstanceUID}')
        elif self.viewerName == 'OHIF-viewer': 
            url =  urljoin(pre, f'ohif/viewer?url=../studies/{self.orthancUID}/ohif-dicom-json')
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
            Config = Pool().get('gnuhealth.orthanc.configServer')
            servers = Config.search([])
            for record in records:
                for confServer in servers:        
                    if confServer.domain == record.server:
                        client = Orthanc(url=confServer.domain,
                                         username=confServer.user, password=confServer.password, return_raw_response=True)
                        response = client.delete_studies_id(record.orthancUID)
                        if 200<=response.status_code<300 or response.status_code==404:
                            records_to_delete.append(record)
                        else:
                            raise UserError(f'Orthanc server returned HTTP code {response.status_code}, with content {response.text}', description="Unable to delete Orthanc study. It may no longer exist or the Orthanc server could be in read-only mode. Please review your Orthanc server configuration.")
        except Exception as exception:
            logger.error('Delete Orthanc study exception: %s', exception, exc_info=True)
            raise UserError(str(exception))
        finally:
            cls.delete(records_to_delete)
            return 'reload'

    @classmethod
    def get_new_studies(cls):
        """
        Update the studies from the Orthanc server, processing changes to studies, series, and instances.
        """
        
        try:
            pool = Pool()
            Config = pool.get('gnuhealth.orthanc.configServer')
            serverConfigs = Config.search([])
            for serverConfig in serverConfigs:
                client = Orthanc(url=serverConfig.domain, username=serverConfig.user, password=serverConfig.password)
                # get changes
                lastChangedIndex = serverConfig.lastChangedIndex if serverConfig.lastChangedIndex is not None else -1
                newChanges = client.get_changes({"since":lastChangedIndex, "limit": 100000})
                # process changes to studies
                newOrthancStudyIDs = [s['ID'] for s in newChanges['Changes'] if s['ChangeType'] == 'NewStudy' or s['ChangeType'] == 'StableStudy']
                cls.createOrUpdateStudiesFromOrthanc(client, serverConfig.domain, newOrthancStudyIDs)
                # process changes to series
                newOrthancSeriesIDs = [s['ID'] for s in newChanges['Changes'] if s['ChangeType'] == 'NewSeries' or s['ChangeType'] == 'StableSeries']
                cls.createOrUpdateSeriesFromOrthanc(client, serverConfig.domain, newOrthancSeriesIDs)
                # process changes to instances
                newOrthancInstanceIDs = [s['ID'] for s in newChanges['Changes'] if s['ChangeType'] == 'NewInstance' or s['ChangeType'] == 'StableInstance']
                cls.createOrUpdateInstancesFromOrthanc(client, serverConfig.domain, newOrthancInstanceIDs)
                # remember last processed change
                serverConfig.lastChangedIndex = newChanges['Last']
                Config.save([serverConfig])
        except Exception as exception:
            raise UserError(str(exception), description="Failed to get new changes, please check the Orthanc server") 

    @classmethod
    def createOrUpdateStudiesFromOrthanc(cls, client, server, orthancStudyIDs):
        """
        Create or update imaging studies from Orthanc server based on the provided study IDs.
        
        :param client: The Orthanc client object used to communicate with the server.
        :param server: The server name where the studies will be created or updated.
        :param orthancStudyIDs: List of study IDs from Orthanc server to process.
        :return: None
        """
        pool = Pool()
        IStu = pool.get('gnuhealth.imaging.imagingStudy')
        for orthancStudyID in orthancStudyIDs:
            orthancStudy = client.get_studies_id(orthancStudyID)
            dicomTags = orthancStudy['MainDicomTags']          
            patientMainDicomTags = orthancStudy['PatientMainDicomTags']
            studyValues = {}
            # Create or update?
            ghStudy = IStu.search([('studyInstanceUID', '=', dicomTags['StudyInstanceUID']), ('server', '=', server)])
            if len(ghStudy) == 0:
                studyValues['patient'] = None
                studyValues['date'] = dicomTags['StudyDate'] if 'StudyDate' in dicomTags else ""
                studyValues['studyInstanceUID'] = dicomTags['StudyInstanceUID']
                studyValues['orthancUID'] = orthancStudy['ID']
                studyValues['patientName'] = patientMainDicomTags['PatientName'] if 'PatientName' in patientMainDicomTags else ""
                studyValues['institution'] = dicomTags['InstitutionName'] if 'InstitutionName' in dicomTags else ""
                studyValues['performingPhysicianName'] = dicomTags['ReferringPhysicianName'] if 'ReferringPhysicianName' else ""
                studyValues['viewerName'] = 'stone-webviewer'
                studyValues['server'] = server
                IStu.create([studyValues])
            else:
                # DICOM studies are immutable. Only the internal Orthanc ID can change.
                studyValues['orthancUID'] = orthancStudy['ID']
                IStu.write(ghStudy, studyValues)          
    
    @classmethod
    def createOrUpdateSeriesFromOrthanc(cls, client, server, orthancSeriesIDs):
        """
        Create or update series from Orthanc in the imaging study and series models.

        :param client: The Orthanc client
        :param server: The server identifier
        :param orthancSeriesIDs: The list of Orthanc series IDs
        :return: None
        """

        pool = Pool()
        IStu = pool.get('gnuhealth.imaging.imagingStudy')
        ISer = pool.get('gnuhealth.imaging.imagingStudySeries')
        for orthancSeriesID in orthancSeriesIDs:
            orthancSeries = client.get_series_id(orthancSeriesID)
            dicomTags = orthancSeries['MainDicomTags']
            seriesValues = {}
            # Create or update?
            ghSeries = ISer.search([('seriesUID', '=', dicomTags['SeriesInstanceUID']), ('server', '=', server)])
            if len(ghSeries) == 0:
                seriesValues['modality'] = dicomTags['Modality'] if 'Modality' in dicomTags else ""
                seriesValues['seriesUID'] = dicomTags['SeriesInstanceUID']
                seriesValues['orthancUID'] = orthancSeries['ID']
                seriesValues['seriesDescription'] = dicomTags['SeriesDescription'] if 'SeriesDescription' in dicomTags else ""
                seriesValues['seriesNumber'] = dicomTags['SeriesNumber'] if 'SeriesNumber' in dicomTags else ""
                seriesValues['viewerName'] = 'stone-webviewer'
                ghStudy = IStu.search([('orthancUID', '=', orthancSeries['ParentStudy']), ('server', '=', server)])
                if len(ghStudy) == 0:
                    raise UserError("The study with the given Orthanc ID does not exist in the gnuhealth database")
                IStu.write(ghStudy, {'series': [('create', [seriesValues])]})
            else:
                # DICOM series are immutable. Only the internal Orthanc ID can change.
                seriesValues['orthancUID'] = orthancSeries['ID']
                ISer.write(ghSeries, seriesValues)

    @classmethod
    def createOrUpdateInstancesFromOrthanc(cls, client, server, orthancInstanceIDs):
        """
        Create or update instances from Orthanc in the GNU Health system.
        
        :param cls: The class itself
        :param client: The Orthanc client
        :param server: The GNU Health server
        :param orthancInstanceIDs: List of Orthanc instance IDs to create or update
        
        :return: None
        """
        pool = Pool()
        ISer = pool.get('gnuhealth.imaging.imagingStudySeries')
        IInst = pool.get('gnuhealth.imaging.imagingSeriesInstances')
        for orthancInstanceID in orthancInstanceIDs:
            orthancInstance = client.get_instances_id(orthancInstanceID)
            dicomTags = orthancInstance['MainDicomTags']
            instanceValues = {}
            # Create or update?
            ghInstance = IInst.search([('sopInstanceUID', '=', dicomTags['SOPInstanceUID']), ('server', '=', server)])
            if len(ghInstance) == 0:
                instanceValues['sopInstanceUID'] = dicomTags['SOPInstanceUID']
                instanceValues['orthancUID'] = orthancInstance['ID']
                instanceValues['instanceNumber'] = dicomTags['InstanceNumber'] if 'InstanceNumber' in dicomTags else ""
                instanceValues['imagePositionPatient'] = dicomTags['ImagePositionPatient'] if 'ImagePositionPatient' in dicomTags else ""
                ghSeries = ISer.search([('orthancUID', '=', orthancInstance['ParentSeries']), ('server', '=', server)])
                if len(ghSeries) == 0:
                    raise UserError("The series with the given Orthanc ID does not exist in the gnuhealth database")
                ISer.write(ghSeries, {'instances': [('create', [instanceValues])]})
            else:
                # DICOM instances are immutable. Only the internal Orthanc ID can change.
                instanceValues['orthancUID'] = orthancInstance['ID']
                IInst.write(ghInstance, instanceValues)
                
    @classmethod
    def full_synchronize(cls):
        """
        Updates the studies in the gnuhealth database by fetching the studies from the Orthanc servers.
        
        This class method fetches all the studies that are already in the gnuhealth database and compares them with the studies from the Orthanc servers. It then creates new studies in the gnuhealth database if there are any studies in the Orthanc servers that are not already present in the gnuhealth database.
        
        Parameters:
            None
        
        Returns:
            None
        
        Raises:
            UserError: If an exception occurs during the update process.
        """
        try:                        
            pool = Pool()
            IStu = pool.get('gnuhealth.imaging.imagingStudy')
            ISer = pool.get('gnuhealth.imaging.imagingStudySeries')
            IInst = pool.get('gnuhealth.imaging.imagingSeriesInstances')
            
            # Get all studies that are already in gnuhealth
            ghStudies = IStu.search([])
            # Get studies from Orthanc servers
            Config = pool.get('gnuhealth.orthanc.configServer')
            servers = Config.search([])
            imagingStudies = []
            for server in servers:
                client = Orthanc(url=server.domain, username=server.user, password=server.password)
                orthancStudies = client.get_studies({'expand':True})
                for orthancStudy in orthancStudies:
                    # Create study in gnuhealth if it does not exist
                    dicomTags = orthancStudy['MainDicomTags']
                    ghStudy = [s for s in ghStudies if s.studyInstanceUID == dicomTags['StudyInstanceUID'] and s.server == server.domain]
                    if len(ghStudy) == 0:                       
                        dicomTags = orthancStudy['MainDicomTags']
                        patientMainDicomTags = orthancStudy['PatientMainDicomTags']
                        studyValues = {}    
                        studyValues['patient'] = None
                        studyValues['date'] = dicomTags['StudyDate'] if 'StudyDate' in dicomTags else ""
                        studyValues['studyInstanceUID'] = dicomTags['StudyInstanceUID']
                        studyValues['orthancUID'] = orthancStudy['ID']
                        studyValues['patientName'] = patientMainDicomTags['PatientName'] if 'PatientName' in patientMainDicomTags else ""
                        studyValues['institution'] = dicomTags['InstitutionName'] if 'InstitutionName' in dicomTags else ""
                        studyValues['performingPhysicianName'] = dicomTags['ReferringPhysicianName'] if 'ReferringPhysicianName' else ""
                        studyValues['viewerName'] = 'stone-webviewer'
                        studyValues['server'] = server.domain
                        logger.error("Creating study")
                        ghStudy = IStu.create([studyValues])
                    ghStudy = ghStudy[0]
                    
                    orthancSeriesIDs = orthancStudy['Series']
                    for orthancSeriesID in orthancSeriesIDs:
                        orthancSeries = client.get_series_id(orthancSeriesID)
                        # Create series in gnuhealth if it does not exist
                        ghSeries = [s for s in ghStudy.series if s.orthancUID == orthancSeriesID]
                        if len(ghSeries) == 0:
                            seriesValues = {}
                            seriesMainDicomTags = orthancSeries['MainDicomTags']
                            seriesValues['modality'] = seriesMainDicomTags['Modality'] if 'Modality' in seriesMainDicomTags else ""
                            seriesValues['seriesUID'] = seriesMainDicomTags['SeriesInstanceUID']
                            seriesValues['orthancUID'] = orthancSeries['ID']
                            seriesValues['seriesDescription'] = seriesMainDicomTags['SeriesDescription'] if 'SeriesDescription' in seriesMainDicomTags else ""
                            seriesValues['seriesNumber'] = seriesMainDicomTags['SeriesNumber'] if 'SeriesNumber' in seriesMainDicomTags else ""
                            seriesValues['viewerName'] = 'stone-webviewer'
                            seriesValues['study'] = ghStudy
                            logger.error("Creating series")
                            ghSeries = ISer.create([seriesValues])                          
                            IStu.write([ghStudy], {'series': [('add', [ghSeries[0].id])]})
                        ghSeries = ghSeries[0]
                        
                        instanceValuesToCreate = []
                        for orthancInstanceID in orthancSeries['Instances']:
                            # Create instance in gnuhealth if it does not exist
                            ghInstance = [s for s in ghSeries.instances if s.orthancUID == orthancInstanceID]
                            if len(ghInstance)==0:
                                orthancInstance = client.get_instances_id(orthancInstanceID)
                                instanceValues={}
                                instanceMainDicomTags = orthancInstance['MainDicomTags']
                                instanceValues['sopInstanceUID'] = instanceMainDicomTags['SOPInstanceUID']
                                instanceValues['orthancUID'] = orthancInstance['ID']
                                instanceValues['instanceNumber'] = instanceMainDicomTags['InstanceNumber'] if 'InstanceNumber' in instanceMainDicomTags else ""
                                instanceValues['imagePositionPatient'] = instanceMainDicomTags['ImagePositionPatient'] if 'ImagePositionPatient' in instanceMainDicomTags else ""
                                instanceValuesToCreate.append(instanceValues)
                        logger.error("Creating "+str(len(instanceValuesToCreate))+" instances")
                        ISer.write([ghSeries], {'instances': [('create', instanceValuesToCreate)]})
        except Exception as exception:
            raise UserError(str(exception), description="Failed to update imaging studies, pleasecheck the Orthanc server") 
        
class ImagingStudySeries(ModelSQL, ModelView):            
    'Imaging Study Series'
    __name__ = 'gnuhealth.imaging.imagingStudySeries' 
    study = fields.Many2One('gnuhealth.imaging.imagingStudy', 'Study', help='Patient study series', readonly=True, required=True, ondelete='CASCADE')
    orthancUID = fields.Char('Orthanc UID', readonly=True, required=True)
    seriesNumber = fields.Char('Series No.', readonly=True)
    seriesDescription = fields.Char('Description', readonly=True, required=False)
    seriesUID = fields.Char('Series UID', readonly=True, required=True)
    modality = fields.Char('Modality', required=True, readonly=True)
    viewerName = fields.Char("stone-webviewer")
    server = fields.Function(fields.Char("Server", readonly=True, required=True), "get_study_server", searcher='search_study_server')
    link = fields.Function(fields.Char(
        "URL",
        help="Link to the DICOM viewer in Orthanc"), "get_link")
    notes= fields.Text("Series notes", help='Extra Information', readonly=False)
    instances = fields.One2Many('gnuhealth.imaging.imagingSeriesInstances', 'series', 'Series instance')
    
    @classmethod
    def __setup__(cls):
        """
        A description of the entire function, its parameters, and its return types.
        """
        super(ImagingStudySeries, cls).__setup__()
        cls._buttons.update({
            'delete_series': {},
        })
        
    @fields.depends("viewerName")
    def on_change_with_link(self):
        """
        This function is a decorator that depends on the "viewerName" field. It is triggered when the value of the "viewerName" field changes.

        Parameters:
            self (object): The instance of the class.
        
        Returns:
            str: The link generated by the "get_link" method with a None parameter.
        """
        return self.get_link(None)
    
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
        Perform a search on the study server based on the provided name and clause.
        
        Args:
            name (str): The name to search for.
            clause (tuple): A tuple representing the search clause.
        
        Returns:
            list: A list of tuples containing the search results in the format ('study.server', <clause[1]>, <clause[2]>).
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
        
    def get_link(self, name):
        """
        A function to generate a link based on the viewer name and study/series IDs.
        
        Parameters:
        name (str): The name of the viewer.
        
        Returns:
        str: The generated URL link.
        """
        # Example fro stone-web
        # https://orthanc.uclouvain.be/demo/stone-webviewer/index.html?study=2.16.840.1.113669.632.20.1211.10000357775&series=1.3.46.670589.11.0.0.11.4.2.0.8743.5.5396.2006120114395892620
        
        # Example for orthanc web viewer
        #https://orthanc.uclouvain.be/demo/web-viewer/app/viewer.html?series=b4b79447-c5c2a0c2-89985adf-9656920f-cb0db5de
        
        # Example for local orthanc web viewer?
        # http://localhost:8042//web-viewer/app/viewer.html?series=b4b79447-c5c2a0c2-89985adf-9656920f-cb0db5de
        
        pre = "".join([self.study.server.rstrip("/"), "/"])
        url = ""
        if self.viewerName == 'stone-webviewer':
            url =  urljoin(pre, f'{self.viewerName}/index.html?study={self.study.studyInstanceUID}&series={self.seriesUID}')
        elif self.viewerName == 'web-viewer': 
            url =  urljoin(pre, f'{self.viewerName}/app/viewer.html?series={self.orthancUID}')
        return url
    
    @classmethod
    def delete(cls, seriess):
        """
        Delete a list of series and their associated studies if they have no more series.
        
        :param seriess: list of series to be deleted
        :return: None
        """
        studies = [s.study for s in seriess]
        # call original delete
        super(ImagingStudySeries, cls).delete(seriess)
        # if the study has no more series, delete the study, too
        IStu = Pool().get('gnuhealth.imaging.imagingStudy')
        for study in studies:
            if study and ((study.series is None) or len(study.series)==0):
                IStu.delete([study])

    @classmethod
    @ModelView.button
    def delete_series(cls, records):
        """
        A class method to delete series from the Orthanc server. 
        Takes a list of records as input. 
        Returns 'reload' on successful deletion.
        Raises UserError on failure with an appropriate error message.
        """
        try:
            Config = Pool().get('gnuhealth.orthanc.configServer')
            servers = Config.search([])
            for record in records:
                for confServer in servers:
                    if (confServer.domain == record.study.server):
                        client = Orthanc(url=confServer.domain,     
                                         username=confServer.user, password=confServer.password, return_raw_response=True)
                        
                        response = client.delete_series_id(record.orthancUID)
                        if 200<=response.status_code<300 or response.status_code==404:
                            cls.delete([record])                                         
                        else:
                            raise UserError(f'Orthanc server returned HTTP code {response.status_code}, with content {response.text}', description="Unable to delete Orthanc study series. It may no longer exist or the Orthanc server could be in read-only mode. Please review your Orthanc server configuration.")
                        
            return 'reload'
        except Exception as exception:
            logger.error('Delete Orthanc Series exception: %s', exception, exc_info=True)
            raise UserError(str(exception), description="Unable to delete Orthanc study series. It may no longer exist or the Orthanc server could be in read-only mode. Please review your Orthanc server configuration.")
        return 'reload'
#
# All instances in the series of patient's image study.
#
class ImagingSeriesInstances(ModelSQL, ModelView):
    'Imaging Series Instance'
    __name__ = 'gnuhealth.imaging.imagingSeriesInstances'
    
    _order_name = 'instanceNumber'
    _order = [('instanceNumber', 'DESC')]
    
    series = fields.Many2One('gnuhealth.imaging.imagingStudySeries', 'Series', help='Study series instance', readonly=True, required=True, ondelete='CASCADE')
    sopInstanceUID = fields.Char('SOP Instance UID', readonly=True, required=True)
    orthancUID = fields.Char('Orthanc UID', readonly=True, required=True)
    instanceNumber = fields.Char('Instance Number', readonly=True, required=False)
    imagePositionPatient = fields.Char('Image Position', readonly=True, required=False)
    server = fields.Function(fields.Char("Server", readonly=True, required=True), "get_study_server", searcher="search_study_server")
    image = fields.Function(fields.Binary("Image"), 'get_image', loading='lazy')
    
    @classmethod
    def __setup__(cls):
        """
        Set up the ImagingSeriesInstances class.

        This method is a class method that sets up the ImagingSeriesInstances class. It calls the __setup__ method of the parent class to perform any necessary setup tasks.

        Parameters:
        - cls: The class object.

        Returns:
        None
        """
        super(ImagingSeriesInstances, cls).__setup__()
    
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
        A class method that searches the study server based on a given name and clause.
        
        Parameters:
            name (str): The name to search for.
            clause (list): A list containing the clause information.
        
        Returns:
            list: A list containing tuples with the search results.
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
            Config = Pool().get('gnuhealth.orthanc.configServer')
            servers = Config.search([])
            for confServer in servers:
                if confServer.domain == self.server:
                    logger.error(confServer.domain)
                    client = Orthanc(url=confServer.domain,
                                        username=confServer.user,
                                        password=confServer.password,
                                        return_raw_response=True)
                    response = client.get_instances_id_frames_frame_rendered(0, self.orthancUID, headers={'Accept':'image/png'})
                    if 200<=response.status_code<300:
                        imageData = response.read()
                        return imageData
                    else:
                        raise UserError(f'Orthanc server returned HTTP code {response.status_code}, with content {response.text}')
            return None
        except Exception as exception:
            logger.error('Get image of instance: %s', exception, exc_info=True)
            return None
