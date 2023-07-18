.. SPDX-FileCopyrightText: 2008-2023 Luis Falcón
..
.. SPDX-License-Identifier: CC-BY-SA-4.0

gnuhealth-data-import.py

Simple script to import data to gnuhealth from a CSV or Libreoffice ODS formatted file.

Functionality : 

Simple script to import patients, labtests, medicaments, products or
other type data from a CSV or Libreoffice ODS formatted file.

Requirements :
This version works with the following versions :

- GNU Health : 4.0 
- Proteus library : 6.0 

Installing proteus :
$ pip install --user "proteus>=6.0,<6.1"

Usage :
Invoke the program and pass the csv formatted file as an argument
eg:

$ python3 ./gnuhealth-data-import.py -f <file.csv|ods> -H <hostname> -p <port> -u <user> -P <password> -d <database>

Data file examples can be found in '<PKG>/data/' directory, for example:
1. labtests.csv
2. labtests.ods
3. medicaments.csv
4. medicaments.ods
5. patients.csv
6. patients.ods
7. products.csv
8. products.ods

This is part of GNU Health Hospital Management component
https://www.gnuhealth.org
