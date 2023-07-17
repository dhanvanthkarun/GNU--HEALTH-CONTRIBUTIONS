.. SPDX-FileCopyrightText: 2008-2023 Luis Falcón
..
.. SPDX-License-Identifier: CC-BY-SA-4.0

patient_uploader.py

Simple script to upload people demographics from a CSV or Libreoffice ODS formatted file.  

Functionality :
Small SAMPLE proteus script to create the parties and their respective patients
from a CSV or libreoffice ODS file

CSV or ODS Fields :
# "ignore", "fed_country","first_name","family_name","name_representation",
# "puid","gender","dob","phone","alternative_id","alternative_id_comments",
# "addr_1","addr_cont","activation_date"


Requirements :
This version works with the following versions :

- GNU Health : 4.0 
- Proteus library : 6.0 

Installing proteus :
$ pip install --user "proteus>=6.0,<6.1"


Usage :
Invoke the program and pass the csv formatted file as an argument
eg:

$ python3 ./patient_uploader.py -f <file.csv|ods> -H <hostname> -p <port> -u <user> -P <password> -d <database>
 
  "admin" and "init" are the correspond to the specific user and passwd 
  "healthdev39" is the database name

The main steps are :
- Test connection to the GNU Health server.
- Upload the person demographic information.
- Create the patient associated to the person.


This is part of GNU Health Hospital Management component
https://www.gnuhealth.org
