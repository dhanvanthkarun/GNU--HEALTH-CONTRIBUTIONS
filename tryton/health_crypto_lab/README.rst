.. SPDX-FileCopyrightText: 2008-2025 Luis Falcón <falcon@gnuhealth.org>
.. SPDX-FileCopyrightText: 2011-2025 GNU Solidario <health@gnusolidario.org>
..
.. SPDX-License-Identifier: CC-BY-SA-4.0

.. image:: https://www.gnuhealth.org/downloads/artwork/logos/isologo-gnu-health.png

Cryptographic Package for GNU Health HIS - LIMS
###############################################

The package *gnuhealth-crypto-lims* provides cryptographic methods and attributes 
to the laboratory models (LIMS) of GNU Health. It requires the core gnuhealth-crypto package.

The module intends to enhance the concepts of confidentiality, integrity and non-repudiation
in GNU Health.

The health_crypto module will provide the following functionality:

 * Document Serialization
 * Document hashing (MD)
 * Document signing
 * Document verification
 * Document encryption

The module will work on records from models that will need this functionality such as 
prescription, patient evaluations, surgeries or lab tests.

The Serialization process will include the information in a predefined format
(JSON) and encoding (UTF8).

There will be a field that will contain the Message digest of the serialization process,
 and that will check for any changes.

The signing process will be upon that Message Digest field, whereas the encryption
process will work on row or column level.

Public key / asymmetric cryptography will be used for signing the documents.


About GNU Health HIS: The Libre Hospital Management and Health Information System
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 
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
