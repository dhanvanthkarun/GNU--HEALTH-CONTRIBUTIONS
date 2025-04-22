.. SPDX-FileCopyrightText: 2024 - Wei Zhao <wei.zhao@uclouvain.be>
..
.. SPDX-License-Identifier: CC-BY-SA-4.0

.. _installation:

Integration of the DICOM server Orthanc into the hospital information system GNU health
=======================================================================================

Description
-----------
The document explains how to integrate the DICOM server Orthanc into the hospital information system GNU Health. 
Here is a video showing the new module look like for the end user in the tryton SAO web client: [#f4]_


Installation
------------

1. You need a working GNU Health HIS 5.x server and an Orthanc server. Follow the instructions at [#f1]_ to install and setup the GNU Health server on your test system. In the following, we assume that you have followed the instructions on the website and that your GNU Health server is located in the directory ``/home/gnuhealth/gnuhealth``.

2. Activate the modules for the demo database:
   ::
      trytond-admin -d <db_name> -u health_imaging_orthanc --activate-dependencies


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

10. Restart your GNU Health server.

11. Connect to the demo database with the client and open the module ``Configuration/Imaging Orthanc/Orthanc``. Select ``Add Orthanc Server`` to configure the connection to the Orthanc server.

12. Watch the video [#f4]_ to see how to use the ``Health Imaging Orthanc`` module to fetch DICOM studies from the Orthanc server and open medical images.


.. rubric:: Footnotes
.. [#f1] https://en.wikibooks.org/wiki/GNU_Health/Installation
.. [#f2] https://en.wikibooks.org/wiki/GNU_Health/The_Demo_database
.. [#f3] https://foss.heptapod.net/tryton/tryton/-/tree/branch/default/sao
.. [#f4] https://www.youtube.com/watch?v=wL8MbM8iu8A
