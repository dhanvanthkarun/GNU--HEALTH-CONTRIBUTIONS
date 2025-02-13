.. SPDX-FileCopyrightText:  2024 - Wei Zhao <wei.zhao@uclouvain.be>
..
.. SPDX-License-Identifier: CC-BY-SA-4.0

.. _installation_in_one_system:


Integration of the DICOM server Orthanc into the HIS GNU Health in one system 
==============================================================================


Description
-----------
The document explains how to integrate the DICOM server Orthanc into the GNU Health hospital information system, combining both the GNU Health server and client into a single system [#f1]_.


Installation
------------

1. To begin, follow the steps to install both the GNU Health server and client [#f1]_.
  
   Run GNU Health:
   ::
     gnuheath-client

2. Create the virtual environment:
   ::
        sudo su gnuhealth -s /bin/bash

        cd

        activate

3.  Install 'PyOrthanc':
    ::
        pip install pyorthanc

4.  Clone the last version of HIS GNU Health:
    ::
        git clone -b wip-orthanc-integration https://codeberg.org/gnuhealth/his.git


.. note:: It is the test branch ``wip-orthanc-integration``.

5. Integrate the new modules:
   ::
        ln -s /opt/gnuhealth/his/tryton/health_imaging_orthanc /opt/gnuhealth/venv/lib/python3.11/site-packages/trytond/modules/


6. Update modules dependencies:
   ::
        trytond-admin -d health -c etc/trytond.conf -u health_imaging_orthanc --activate-dependencies


   .. note:: If you are using a different database, you have to replace ```ghdemo44``` by its name.
        
7. Install the local Orthanc server and plugins:
   ::
        sudo apt install orthanc

        sudo apt install orthanc-dicomweb

        sudo apt install orthanc-webviewer

        sudo apt install orthanc-wsi

   Download the OHIF viewer ``libOrthancOHIF.so`` in https://orthanc.uclouvain.be/downloads/linux-standard-base/orthanc-ohif/1.2/index.html and copy it in the plugins directory ``/usr/share/orthanc/plugins/``.

   Download the stone web viewer ``libStoneWebViewer.so`` in https://orthanc.uclouvain.be/downloads/linux-standard-base/stone-web-viewer/2.5/index.html and copy it in the plugins directory ``/usr/share/orthanc/plugins/``.

8. We have created a new widget that allows to select and upload multiple DICOM files in the desktop client and web client. The widget has to be added to the clients.
   
    - For the desktop client: Let's assume that your desktop client is installed in ```/home/gnuhealth/health-hmis-client/```. Copy the widget into the   plugin directory of the client:
      ::
         cp -r /home/health_imaging_orthanc/dicombinary /home/gnuhealth/health-hmis-client/gnuhealth/plugins/
        

    - For the SAO web client: Let's assume you have installed the SAO client in ``/home/gnuhealth/sao`` (see [#f2]_). If there is not already a custom.js file in the web client's directory, you can just copy the widget into the client:
      ::
        cp custom.js /home/gnuhealth/sao

9. If you are using nginx as proxy:
    In file ``/etc/nginx/sites-enabled/GH_HIS_HTTP.conf`` add the following line in the server block:
    ::
        client_max_body_size 500M;

        proxy_send_timeout 300;

        
    Restart nginx (debian, ubuntu,...):
    :: 
        systemctl restart nginx

.. note:: If you are using ansible to install gnuhealth as described in https://docs.gnuhealth.org/ansible/examples/gnuhealth_server_and_client.html. You have to modify the ansible files to make the above changes permanent.

10. Restart your GNU Health server.

11. Connect to the demo database with the client and open the module ``Configuration/Imaging Orthanc/Orthanc``. Select ``Add Orthanc Server`` to configure the connection to the Orthanc server.

12.   Watch the video [#f3]_ to see how to use the ``Imaging Orthanc`` module to fetch DICOM studies from the Orthanc server and open medical images.

.. rubric:: Footnotes
.. [#f1] https://docs.gnuhealth.org/ansible/examples/gnuhealth_server_and_client.html
.. [#f2] https://foss.heptapod.net/tryton/tryton/-/tree/branch/default/sao
.. [#f3] https://www.youtube.com/watch?v=wL8MbM8iu8A
