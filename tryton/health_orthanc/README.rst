.. SPDX-FileCopyrightText: 2011-2025 GNU Solidario <health@gnusolidario.org>
.. SPDX-FileCopyrightText: 2019-2022 Chris Zimmerman <chris@teffalump.com>
.. SPDX-FileCopyrightText: 2021-2025 Luis Falcón <falcon@gnuhealth.org>
.. SPDX-FileCopyrightText: 2023 Patryk Rosik <p.rosik@stud.uni-hannover.de>
.. SPDX-FileCopyrightText: 2023-2025 Feng Shu <tumashu@163.com>
.. SPDX-FileCopyrightText: 2024-2025 - Wei Zhao <wei.zhao@uclouvain.be>

.. SPDX-License-Identifier: CC-BY-SA-4.0

.. image:: https://www.gnuhealth.org/downloads/artwork/logos/isologo-gnu-health.png

GNU Health Orthanc PACS server integration package
##################################################

This module provides functions for management of medical image data stored on an Orthanc server.

Description
-----------
The document explains how to integrate the DICOM server Orthanc into the hospital information system GNU Health. 
Here is a video showing the new module look like for the end user in the tryton SAO web client: [#f4]_


Installation
------------

1. You need a working GNU Health HIS 5.x server and an Orthanc server. Follow the instructions at [#f1]_ to install 
and setup the GNU Health server on your test system. In the following, we assume that you have followed the instructions
on the website and that your GNU Health server is located in the directory ``/opt/gnuhealth/his``.

2. Activate the modules for the demo database:
   ::
     
     
      trytond-admin -d <db_name> -u health_orthanc --activate-dependencies


3. Install the local Orthanc server and plugins:
   ::


    sudo apt install orthanc

    sudo apt install orthanc-dicomweb

    sudo apt install orthanc-webviewer

    sudo apt install orthanc-wsi


   Download the OHIF viewer ``libOrthancOHIF.so`` in https://orthanc.uclouvain.be/downloads/linux-standard-base/orthanc-ohif/1.2/index.html and copy it in the plugins directory ``/usr/share/orthanc/plugins/``.

   Download the stone web viewer ``libStoneWebViewer.so`` in https://orthanc.uclouvain.be/downloads/linux-standard-base/stone-web-viewer/2.5/index.html and copy it in the plugins directory ``/usr/share/orthanc/plugins/``.

5. We have created a new widget that allows to select and upload multiple DICOM files in the desktop client and web client. The widget is part of the native GNU Health GTK client

    - For the SAO web client: Let's assume you have installed the SAO client in ``/home/gnuhealth/sao`` (see [#f3]_). If there is not already a custom.js file in the web client's directory, you can just copy the widget into the client:
      ::


        cp custom.js /home/gnuhealth/sao


    Otherwise, you have to manually add the content of our custom.js file to the existing file in the SAO client.    

6.  If you are using nginx as proxy:
   
   In file ``/etc/nginx/sites-enabled/GH_HIS_HTTP.conf`` add the following line in the server block.
   ::
      
      
      client_max_body_size 500M;

      proxy_send_timeout 300;

        
   Restart nginx (debian, ubuntu,...):
   ::
   
   
      systemctl restart nginx
   
    .. note:: If you are using ansible to install gnuhealth as described in https://docs.gnuhealth.org/ansible/examples/gnuhealth_server_and_client.html. You have to modify the ansible files to make the above changes permanent.

7. Restart your GNU Health server.

8. Connect to the demo database with the client and open the module ``Configuration/Imaging Orthanc/Orthanc``. Select ``Add Orthanc Server`` to configure the connection to the Orthanc server.

9. Watch the video [#f4]_ to see how to use the ``Health Imaging Orthanc`` module to fetch DICOM studies from the Orthanc server and open medical images.



.. _Imaging Orthanc:

Orthanc Server Configuration
==============================

The primary function is to establish the connection between Orthanc's DICOM servers and GNU Health. The label of a server is a name that the user can choose to represent the server directly. The domain field contains the full web address (URL) to the Orthanc server. This helps GNU Health to find the correct server to connect to. The user must also provide a username and password to log in to the Orthanc server. 


Configuration
-------------

.. class:: health_orthanc_configuration.ServerConfig(ModelSQL, ModelView)
    
    This class, `ServerConfig`, is used to connect to an Orthanc DICOM server and to check if a connection to the corresponding domain can be established.

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

.. class:: health_orthanc_configuration.wizard.add_orthanc_init(ModelView)
  
  This class definition `add_orthanc_init` is a model view for initializing an Orthanc connection.
    
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



Imaging Orthanc
===============

This section presents the core aspect of the Orthanc integration. It is designed for uploading and updating patient images and for viewing the images using special Orthanc DICOM viewers.


Data Models for image data
--------------------------

In this module we have developed three data models to organise image study data according to the DICOM format. These models represent studies, series within studies (such as CT, MR or PET scans) and the individual instances within each series. They represent the relationships between these elements. For example, a single patient may undergo multiple studies, each study may consist of multiple series, and each series may contain multiple instances.


Patient Orthanc Study
---------------------



.. class:: health_imaging_orthanc.PatientOrthancStudy(ModelSQL, ModelView)

    This class, `PatientOrthancStudy`, defines a model for the Orthanc study.

    :param ModelSQL: Inherit from the Tryton ModelSQL class for SQL database operations.
    :type ModelSQL: class: ``trytond.model.ModelSQL``

    :param ModelView: Inherit from the Tryton ModelView class for user interface operations.
    :type ModelView: class: ``trytond.model.ModelView``

    Here's a brief description of each method:
    
    - ``__setup__()``: Sets up the class with additional buttons for deleting a study and selecting a viewer.

    - ``get_gnuhealth_patient()``: Retrieves the GNU patient with the given name.

    - ``get_ohif_viewer_link()``: Generates a URL for the OHIF viewer and study.
   
    - ``stone_viewer_link()``: Generates a URL for the stone viewer and study.

    - ``delete_study()``: Deletes a study record from the Orthanc server.

    - ``update_studies()``: Updates the studies in the GNU Health database by fetching studies from the Orthanc servers and creating new studies if needed.


Study Series
------------

.. class:: health_imaging_orthanc.StudySeries(ModelSQL, ModelView)

    This class definition is for the ``Study Series`` in the ``gnuhealth.imaging_orthanc`` module.

    :param ModelSQL: Inherit from the Tryton ModelSQL class for SQL database operations.
    :type ModelSQL: class: ``trytond.model.ModelSQL``

    :param ModelView: Inherit from the Tryton ModelView class for user interface operations.
    :type ModelView: class: ``trytond.model.ModelView``

    Here's a brief overview of what each class method does:

    - ``__setup__()``: Initializes the class and sets up the buttons.

    - ``get_study_server()``: Retrieves the server for the given study.
    
    - ``get_study_patient()``: Returns the name of the patient associated with the given study.

    - ``get_stone_viewer_link()``: Generates a URL for the stone viewer with study UID and series UID.
    
    - ``delete_series()``: Deletes study series records and handles exceptions.


Series Instances
----------------

.. class:: health_imaging_orthanc.SeriesInstances(ModelSQL, ModelView)
  
  The provided Python code defines a class `SeriesInstances` which is a SQL and view model for a database table. This class represents instances of studies, typically in the context of imaging_orthanc.

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
--------------------

.. class:: health_imaging_orthanc.wizard.update_studies(Wizard)
   
   This class definition is a custom Tryton wizard for update patient image studies stored in Orthanc server. 

   :param Wizard: A finite state machine.
   :type Wizard: class: ``trytond.wizard.Wizard``

   Here's what each class method does:

   - ``transition_update()``: Updates the studies and returns 'end'.

   - ``end()``: Signals the end of the process and returns the string 'reload'.


Upload Image Data
-----------------

.. class:: health_imaging_orthanc.wizard.UploadImageData(Wizard)
    
   This class definition is a custom Tryton wizard for uploading image data. 
   
   :param Wizard: A finite state machine. 
   :type Wizard: class: ``trytond.wizard.Wizard``
    
   Here's what each class method does:

   - ``upload_image_data()``: Uploads the image data to the server and handles exceptions.

   - ``transition_upload()``: Transitions the upload process by uploading the image data and then updating the studies using ``update_studies()``

   - ``end()`` Returns the string 'reload'.

Full Synchronize Studies
------------------------

.. class:: health_imaging_orthanc.wizard.FullSynchronize(Wizard)

   This class definition is a custom Tryton wizard for full synchronizing studies. It updates the studies in the GNU Health database by fetching studies from the Orthanc servers and creating new studies if needed.
   
   :param Wizard: A finite state machine. 
   :type Wizard: class: ``trytond.wizard.Wizard``
    
   Here's what the class method does:

     - ``FullSynchronize()``: Full synchronizes the studies.


Get new studies
---------------

This class defines a Tryton wizard that is responsible for updating studies from an Orthanc server by processing changes to studies, series and instances. It retrieves configuration information, fetches changes from the Orthanc server and updates the studies in the GNU Health database. If there is an error in the process, it throws an exception.

Here's what the class method does:
    - ``GetNewStudies()``: Retrieves new studies from the Orthanc server and updates the studies in the GNU Health database.




About GNU Health HIS: The Libre Hospital Management and Health Information System
##################################################################################
 
The GNU Health HIS provides the following functionality:

 * Hospital Management Information System
 * Electronic Medical Record (EMR)
 * Health Information System
 * Laboratory Information System

The Hospital and Health Information System component (HIS) from GNU Health (GH) 
provides over 50 packages (primary care, obstetrics & gynecology,
pediatrics, surgery, lims, genetics, diagnostic imaging, dentistry, reporting...)
to fit your institution needs. The GH HIS combines the socioeconomic determinants of
health with state-of-the-art technology in bioinformatics and medical genetics. 

The HIS manages the internal processes of a health institution, such as 
financial management, billing, stock management, pharmacies or labs (LIMS). 

The GH HIS is part of the GNU Health project, the **Libre digital health ecosystem**.

The GNU Health project combines the daily medical practice with state-of-the-art 
technology in bioinformatics and genetics. It provides a holistic approach 
to the  person, from the biological and molecular basis of disease to 
the social and environmental determinants of health.

This component is ready to integrate in the **GNU Health Federation**, which
allows to interconnect heterogeneous nodes and build large federated health 
networks across a region, province or country.


Homepage
--------

https://www.gnuhealth.org


Documentation
-------------

https://docs.gnuhealth.org

Support GNU Health 
-------------------

GNU Health is a project of GNU Solidario. GNU Solidario is a 
non-for-profit organization that works globally, focused on **Social Medicine**.

Health and education are the basis for the development and dignity of societies. 
**Advancing Social Medicine is the mission from GNU Solidario.**

You can also **donate** to our project via : 

https://www.gnuhealth.org/donate/

In addition, you can show your long time commitment to GNU Health by 
**becoming a member** of GNU Solidario, so together we can further 
deliver Freedom and Equity in Healthcare around the World.

https://my.gnusolidario.org/join-us/

GNU Solidario hosts IWEEE and GnuHealthCon:

The International Workshop on e-Health in Emerging Economies- a good way to
support GNU Solidario and to get the latest on e-Health is to assist
to the conferences. 


Need help to implement GNU Health ? 
-----------------------------------

We are committed to do our best in helping out projects that can improve
the health of your country or region. We want the project to be a success,
and since our resources are limited, we need to work together to make a great
and sustainable project.

In order to be eligible, we need the following information from you,
your NGO or government:

* An introduction of the current needs
* The project will use free software, both at the server and workstations
* There will be a local designated person that will be in charge of  
  the project and the know-how transfer to the rest of the community. This person 
  must be committed to be from the beginning of the project
  until two years after its completion.
* There must be a commitment of knowledge transfer to the rest of the team.

We will do our best to help you out with the implementation and training
for the local team, to build local capacity and make your project sustainable.

Please contact us and we'll back to you as soon as possible::


 Thank you !
 Dr. Luis Falcón, MD, MSc
 Author and project leader
 falcon@gnuhealth.org


Email
-----
info@gnuhealth.org

Mastodon
--------

https://mastodon.social/@gnuhealth

License
--------

GNU Health is licensed under GPL v3+::

 Copyright (C) 2008-2025 Luis Falcon <falcon@gnuhealth.org>
 Copyright (C) 2011-2025 GNU Solidario <health@gnusolidario.org>

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.

.. rubric:: Footnotes
.. [#f1] https://docs.gnuhealth.org/his/techguide/installation/
.. [#f2] https://docs.gnuhealth.org/his/userguide/demodb.html
.. [#f3] https://foss.heptapod.net/tryton/tryton/-/tree/branch/default/sao
.. [#f4] https://www.youtube.com/watch?v=wL8MbM8iu8A
