.. SPDX-FileCopyrightText:  2024 - Wei Zhao <wei.zhao@uclouvain.be>
..
.. SPDX-License-Identifier: CC-BY-SA-4.0

.. _Radiology:

Orthanc Server Configuration
==============================

The primary function is to establish the connection between Orthanc's DICOM servers and GNU Health. The label of a server is a name that the user can choose to represent the server directly. The domain field contains the full web address (URL) to the Orthanc server. This helps GNU Health to find the correct server to connect to. The user must also provide a username and password to log in to the Orthanc server. 

The image below displays a snapshot of the Orthanc module:

.. image:: /source/image/orthanc-config.png
    :width: 400
    :height: 180
    :align: center
    :alt: GNU Health Orthanc Configuration Module


Configuration
-------------

.. class:: health_orthanc_configuration.OrthancServerConfig(ModelSQL, ModelView)
    
    This class, `OrthancServerConfig`, is used to connect to an Orthanc DICOM server and to check if a connection to the corresponding domain can be established.

    :param ModelSQL: Inherit from the Tryton ModelSQL class for SQL database operations.
    :type ModelSQL: class: ``trytond.model.ModelSQL``

    :param ModelView: Inherit from the Tryton ModelView class for user interface operations.
    :type ModelView: class: ``trytond.model.ModelView``

    Here's a brief description of each method:

    - ``__setup__(cls)``: Set up the class for database access by initializing properties and contstrains, such as ensuring the uniqueness 
        of the ``label`` and ``domain`` fields.

    - ``quick_check(domain, user, password)``: Checks if the server details are correct by attempting to connect to the Orthanc DICOM server with the provided domain.

    - ``on_change_with_validated(self)``: Updates the validated field based on the current server details by calling the ``quick_check`` method with the ``domain``, ``user``, and ``password`` attributes.


Wizard
------

.. class:: health_orthanc_configuration.wizard.AddOrthancInit(ModelView)
  
  This class definition `AddOrthancInit` is a model view for initializing an Orthanc connection.
    
  :param ModelView: Inherit from the Tryton ModelView class for user interface operations.
  :type ModelView: class: ``trytond.model.ModelView``

  - ``label``: Represents the label of the Orthanc server. Must be unique.

  - ``domain``: Represents the full URL of the Orthanc server.

  - ``user``: Represents the username for the Orthanc REST server.

  - ``password``: Represents the password for the Orthanc REST server.


.. class:: health_orthanc_configuration.wizard.ConnectNewOrthancServer(Wizard)
 
  This class, `ConnectNewOrthancServer` defines a wizard for connecting to an Orthanc server. 

  :param Wizard: A finite state machine. 
  :type Wizard: class: ``trytond.wizard.Wizard``

   Here's what each class method does:

  - ``start``: Displays the initial state of the wizard, asking for the label, URL, username, and password of the Orthanc server.

  - ``connect``: Handles the transition when the 'Begin' button is pressed. It attempts to connect to the Orthanc server using the provided credentials. 

  - ``status``: Displays the status of the connection attempt. It includes a 'Close' button.

  - ``transition_connect()``: Connects to the Orthanc servers, handles different exceptions, logs the success or failure of the connection attempt, and return 'status' after completion. 
 
  - ``default_status(fields)``: Generates a default status dictionary based on the provided fields.



Radiology
=========

This section presents the core aspect of the Orthanc integration. It is designed for uploading and updating patient images and for viewing the images using special Orthanc DICOM viewers. The image below displays a snapshot of the radiolgy module:

.. image:: /source/image/radiology-module.png
    :width: 400
    :height: 180
    :align: center
    :alt: GNU Health Radiology Module

Data Models for image data
--------------------------

In this module we have developed three data models to organise image study data according to the DICOM format. These models represent studies, series within studies (such as CT, MR or PET scans) and the individual instances within each series. They represent the relationships between these elements. For example, a single patient may undergo multiple studies, each study may consist of multiple series, and each series may contain multiple instances.


Patient Orthanc Study
^^^^^^^^^^^^^^^^^^^^^

.. class:: health_radiology.PatientOrthancStudy(ModelSQL, ModelView)

    This class, `PatientOrthancStudy`, defines a model for imaging study.

    :param ModelSQL: Inherit from the Tryton ModelSQL class for SQL database operations.
    :type ModelSQL: class: ``trytond.model.ModelSQL``

    :param ModelView: Inherit from the Tryton ModelView class for user interface operations.
    :type ModelView: class: ``trytond.model.ModelView``

    Here's a brief description of each method:
    
    - ``__setup__()``: Sets up the class with additional buttons for deleting a study and selecting a viewer.

    - ``select_viewer()``: Selects a viewer for the given studies.

    - ``on_change_with_link()``: Generates a link based on the viewer name.

    - ``get_gnu_patient()``: Retrieves the GNU patient with the given name.

    - ``get_link()``: Generates a URL for the specified viewer and study.

    - ``delete_study()``: Deletes a study record from the Orthanc server.

    - ``update_studies()``: Updates the studies in the GNU Health database by fetching studies from the Orthanc servers and creating new studies if needed.


Study Series
^^^^^^^^^^^^

.. class:: health_radiology.ImagingStudySeries(ModelSQL, ModelView)

    This class definition is for the ``Imaging Study Series`` in the ``gnuhealth.imaging`` module.

    :param ModelSQL: Inherit from the Tryton ModelSQL class for SQL database operations.
    :type ModelSQL: class: ``trytond.model.ModelSQL``

    :param ModelView: Inherit from the Tryton ModelView class for user interface operations.
    :type ModelView: class: ``trytond.model.ModelView``

    Here's a brief overview of what each class method does:

    - ``__setup__()``: Initializes the class and sets up the buttons.

    - ``on_change_with_link()``: Returns a link generated by the "get_link" method with a None parameter.
    
    - ``get_study_server()``: Retrieves the server for the given study.
    
    - ``get_study_patient()``: Returns the name of the patient associated with the given study.

    - ``get_study_patient()``: Returns the name of the patient associated with the given study.

    - ``delete_series()``: Deletes study series records and handles exceptions.


Series Instances
^^^^^^^^^^^^^^^^

.. class:: health_radiology.ImagingSeriesInstances(ModelSQL, ModelView)
  
  The provided Python code defines a class `ImagingSeriesInstances` which is a SQL and view model for a database table. This class represents instances of imaging studies, typically in the context of radiology.

  :param ModelSQL: Inherit from the Tryton ModelSQL class for SQL database operations.
  :type ModelSQL: class: ``trytond.model.ModelSQL``

  :param ModelView: Inherit from the Tryton ModelView class for user interface operations.
  :type ModelView: class: ``trytond.model.ModelView``
 
  Here's a succinct explanation of its methods:

  - ``__setup__()``: Initializes the class and sets up the buttons.
    
  - ``get_study_server()``: Retrieves the server for the given study.

  - ``get_image()``: A method to retrieve an image from an Orthanc server


Wizard
------
The Tryton wizard is a specific kind of finite state machine utilized within this module. It facilitates tasks such as updating studies, uploading new image data to the server, and deleting existing image data.

Update Image Studies
^^^^^^^^^^^^^^^^^^^^

.. class:: health_radiology.wizard.UpdateStudies(Wizard)
   
   This class definition is a custom Tryton wizard for update patient image studies stored in Orthanc server. 

   :param Wizard: A finite state machine.
   :type Wizard: class: ``trytond.wizard.Wizard``

   Here's what each class method does:

   - ``transition_update()``: Updates imaging studies and returns 'end'.

   - ``end()``: Signals the end of the process and returns the string 'reload'.


Upload Image Data
^^^^^^^^^^^^^^^^^

.. class:: health_radiology.wizard.UploadImageData(Wizard)
    
   This class definition is a custom Tryton wizard for uploading image data. 
   
   :param Wizard: A finite state machine. 
   :type Wizard: class: ``trytond.wizard.Wizard``
    
   Here's what each class method does:

   - ``upload_imageData()``: Uploads the image data to the server and handles exceptions.

   - ``transition_upload()``: Transitions the upload process by uploading the image data and then updating the imaging studies using ``update_studies()``

   - ``end()`` Returns the string 'reload'.

Full Synchronize Studies
^^^^^^^^^^^^^^^^^^^^^^^^

.. class:: health_radiology.wizard.FullSynchronizeStudies(Wizard)

   This class definition is a custom Tryton wizard for full synchronizing studies. It updates the studies in the GNU Health database by fetching studies from the Orthanc servers and creating new studies if needed.
   
   :param Wizard: A finite state machine. 
   :type Wizard: class: ``trytond.wizard.Wizard``
    
   Here's what the class method does:

     - ``full_synchronize()``: Full synchronizes imaging studies.


Get new studies
^^^^^^^^^^^^^^^

This class defines a Tryton wizard that is responsible for updating studies from an Orthanc server by processing changes to studies, series and instances. It retrieves configuration information, fetches changes from the Orthanc server and updates the studies in the GNU Health database. If there is an error in the process, it throws an exception.

Here's what the class method does:
    - ``get_new_studies()``: Retrieves new studies from the Orthanc server and updates the studies in the GNU Health database.


The following shows the outcome of the integration between GNU Health and Orthanc:

.. image:: /source/image/Integration_result.png
    :width: 430
    :height: 440
    :align: center
    :alt: Integration result between GNU Health and Orthanc