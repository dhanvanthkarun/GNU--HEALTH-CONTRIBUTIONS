.. SPDX-FileCopyrightText: 2008-2025 Luis Falcón <falcon@gnuhealth.org>
.. SPDX-FileCopyrightText: 2011-2025 GNU Solidario <health@gnusolidario.org>
..
.. SPDX-License-Identifier: CC-BY-SA-4.0

.. image:: https://www.gnuhealth.org/downloads/artwork/logos/isologo-gnu-health.png


GNU Health Intensive Care Unit package for GNU Health HIS
#########################################################

Health ICU includes functionality in a Intensive Care Unit.

It incorporates scoring systems, such :

- GSC : Glasgow Coma Scale
- APACHE II : Acute Physiology and Chronic Health Evaluation II

The functionality is divided into two major sections :

- Patient ICU Information
- Patient Roundings

1) Patient ICU Information : Health -> Hospitalization -> Intensive Care -> Patient ICU Info
All the information is linked to the Inpatient record. This form allows you to have an idea of the patient status, days since admission at ICU and use of mechanical ventilation, among other functionalities.
From this form, you can directly create and evaluate :

- Electrocardiograms
- APACHE II Scoring
- Glasgow Coma Scale scoring

This is the preferred method to create new tests and evaluations on the patient, since it automatically takes the Inpatient Registration number and the patient information associated to it. This eliminates the error of assigning another inpatient record.

2) Patient Rounding : Health -> Nursing -> Roundings
All the ICU related information is on the new "ICU" tab. The assessment is divided in different systems :

- Neurological
- Respiratory
- Cardiovascular
- Blood and Skin
- Digestive

In this assesment (that can have different frequencies, depending on the center policies ), you should enter the information starting at the left tab (Main) and once you are done with this section, switch to the ICU tab.

The information in for the Glasgow Coma Scale and Electrocardiogram can be entered at that very same moment (if the EKG is done at bed side at evaluation time), or can be selected from the list. Please ask to put a short interpretation on the EKG.
For each EKG, in addition to fill in as much information as possible, please take a picture or scan the ECG strip, since it can provide valuable information for further evaluations ! The information related to the ECG in the rounding will be the Interpretation, so please be clear.
Of course, you can access to the rest of the information related to the ECG by opening the resource.

Xray picture : The ICU rounding allows to place an Xray (or other imaging diagnosis image). Unlike attachments related to the object, that you can also use, this image is even more contextual and graphic. Of course, this image should be very recent to the evaluation itself.

Drainages : Chest drainages are input  from a One2Many widget. This permits to have as many as in the patient, and with their own characteristics.



GNU Health HIS: The Libre Hospital Information System
=====================================================
 
Welcome to the Hospital Information System (HIS) of GNU Health!

The main areas of the HIS are:

* **Demographics and Community**: Individuals, domiciliary
  units, families, socioeconomics, demographic & administrative information
* **Patient Management**: Health encounters and evaluations,
  hospitalizations, clinical history and other information that makes up the
  electronic medical records (EMR)
* **Health Center**: Finances & billing, stock &
  pharmacy, staff, suppliers, beds, operating rooms and other relevant tasks
  to manage the health center
* **Laboratory and Medical Imaging**: Management of complementary orders such as
  lab tests, medical and diagnostic imaging requests and workflows
* **Health Information System**: Statistics, analytical reporting on collected
  data from the community and participating health institutions, e.g. demographics
  and epidemiology

Functionalities of specific modules are briefly summarized over here:

https://docs.gnuhealth.org/his/features.html#packages

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

GNU Solidario hosts IWEEE and GNU Health Con:

The International Workshop on e-Health in Emerging Economies - a good way to
support GNU Solidario and to get the latest on e-Health is to assist
to the conferences. 


Need help to implement GNU Health ? 
-----------------------------------

We are committed to do our best in helping out projects that can improve
the health of your country or region. We want the project to be a success,
and since our resources are limited, we need to work together to make a great
and sustainable project.

First place to ask for support are the mailing lists & matrix chat:

https://docs.gnuhealth.org/his/support.html#online-resources

Feel free to contact us directly if this does not suffice or if you need custom support.
In order to be elegible, we need the following information from you,
your NGO or government:

* An introduction of the current needs
* The project will use free software, both at the server and workstations
* There will be a local designated person that will be in charge of  
  the project and the know-how transfer to the rest of the community.This person 
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

Mastodon: https://mastodon.social/@gnuhealth

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

License of the Human Natural variants Database
------------------------------------------------

 Copyrighted by the UniProt Consortium, see https://www.uniprot.org/terms
 Distributed under the Creative Commons Attribution (CC BY 4.0) License
