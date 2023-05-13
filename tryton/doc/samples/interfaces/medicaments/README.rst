.. SPDX-FileCopyrightText: 2008-2023 Luis Falcón 
..
.. SPDX-License-Identifier: CC-BY-SA-4.0

meds_uploader.py

Simple script to show ways to interface with GNU Health in a
non-interactive way.
This program reads a CSV formatted file with that contains the meds

Included in this directory a sample med_sample.csv, that contains 
some meds (services)


Requirements :
This version works with the following versions :

- GNU Health : 4.2 
- Proteus library : 6.0 

Installing proteus :
$ pip install --upgrade --user "proteus>=6.0,<6.1" 


Usage :
Invoke the program and pass the csv formatted file as an argument
eg:

$ ./meds_uploader.py meds_sample.csv <host> <port> <user> <passwd> <dbname>

The format and fields of the CSV file are:
 Medicament CSV Format
 Name,List Price,Cost Price,Type,UOM, strength, strength_unit, form, code

 Sample csv content
 "Vitamin B12 - 500ug",30,20,"goods","Unit",500,"ug","TAB", "VITB12-500ug"

The main steps are :
- Test connection to the GNU Health server
- Check the csv file
- Upload the results.


This is part of GNU Health, the Free Hospital and Health Information System
https://www.gnuhealth.org
