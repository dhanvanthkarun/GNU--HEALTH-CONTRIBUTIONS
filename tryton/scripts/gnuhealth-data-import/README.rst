.. SPDX-FileCopyrightText: 2008-2024 Luis Falcón
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
gnuhealth-data-import.py [-h] -f FILENAMES [-H HOSTNAME] [-p PORT]
                         [-u USER] -P PASSWD -d DATABASE

the following arguments are required: -f/--filenames, -P/--passwd, -d/--database

eg:

$ python3 ./gnuhealth-data-import.py -f <data-file1.csv|ods> <data-file2.csv|ods> \
                                     -H <hostname> -p <port> -u <user> \
                                     -P <password> -d <database>

Data file examples can be found in '<PKG>/data/' directory, for example:
- data/1-patients.csv
- data/1-patients.ods
- data/2-products.csv
- data/2-products.ods
- data/3-medicaments.csv
- data/3-medicaments.ods
- data/4-labtests.csv
- data/4-labtests.ods

This is part of GNU Health Hospital Management component
https://www.gnuhealth.org
