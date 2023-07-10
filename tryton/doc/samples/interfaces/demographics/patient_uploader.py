#!/usr/bin/env python 
# SPDX-FileCopyrightText: 2008-2023 Luis Falcón <falcon@gnuhealth.org>
# SPDX-FileCopyrightText: 2011-2023 GNU Solidario <health@gnusolidario.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

#########################################################################
#   Hospital Management Information System (HMIS) component of the      #
#                       GNU Health project                              #
#                   https://www.gnuhealth.org                           #
#########################################################################
#                       patient_uploader.py                             #
#         Sample script to upload patients and demographics             #
#########################################################################

# Functionality :
# Small SAMPLE proteus script to create the parties and their respective patients 
# from a CSV file

# CSV Format :
# "FIRST NAME","FAMILY NAME", "PUID", "Gender", "DoB", "Phone",
# "Alternative ID","address 1 (eg street)", "addr cont (city..)",
# "activation date"

# Usage: patient_uploader <csv_file> <hostname:port> <user:password> <dbname>

from datetime import datetime
import sys
import csv

from proteus import Model
from proteus import config as pconfig

import pandas as pd


def PartyDemographics(line):
    fed_country = line["fed_country"]
    name        = line["first_name"]
    lastname    = line["family_name"]
    name_repr   = line["name_representation"]
    puid        = line["puid"]
    gender      = line["gender"]
    dob         = line["dob"]
    phone       = line["phone"]
    alt_id      = line["alternative_id"]
    alt_id_cmt  = line["alternative_id_comments"]
    addr_1      = line["addr_1"]
    addr_cont   = line["addr_cont"]
    active_date = line["activation_date"]

    Party = Model.get('party.party')
    PartyAddress = Model.get('party.address')
    PartyAlternativeID = Model.get('gnuhealth.person_alternative_identification')
    ContactMethod = Model.get('party.contact_mechanism')
    Patient = Model.get('gnuhealth.patient')

    parties = []

    if puid:
        parties = Party.find([('ref', '=', puid)])

    if alt_id:
        parties = parties + Party.find([('alternative_ids.code', '=', alt_id)])

    if parties:
        party = parties[0]
    else:
        party = Party()
        
    party.fed_country = fed_country
    party.name = name
    party.lastname = lastname
    party.ref = puid
    party.is_patient = True
    party.is_person = True

    if name_repr and (name_repr in ['pgfs', 'gf', 'fg', 'cjk']):
        party.name_representation = name_repr

    if gender and (gender in ['m','f','u']):
        party.gender = gender

    # Set Date of birth
    try:
        party.dob = datetime.strptime(dob, '%d/%m/%Y')
    except:
        party.dob = None

    # Set telephone number (mobile)
    if phone:
        contactmethod = ContactMethod()
        contactmethod.type = 'mobile'
        contactmethod.value = phone
        
        party.contact_mechanisms.append(contactmethod)
        
    # Set alternative Identification
    if alt_id:
        party.alternative_identification = True
        altid = PartyAlternativeID()
        altid.alternative_id_type = 'other'
        altid.code = alt_id
        altid.comments = alt_id_cmt

        party.alternative_ids.append(altid)


    # Set the party address

    address = PartyAddress()

    if addr_1:
        address.street = addr_1
 
    if addr_cont:
        address.city = addr_cont


    # Use this if one address only, so it won't leave the first record blank
    party.addresses[0] = address

    # For multiple addresses, append . party.addresses.append(address)
    try:
        party.activation_date = datetime.strptime(active_date, '%d/%m/%Y')
    except:
        party.activation_date = None


    party.save()
    
    if not Patient.find([('name.ref', '=', party.ref)]):
        patient = Patient()
        patient.name = party
        patient.save()


if (len(sys.argv) < 4):
    exit ("usage: ./patient_uploader <csv_file> \
        <hostname> <port> <user> <password> <dbname>")

patient_data = pd.read_csv(open(sys.argv[1], 'r'),
                           sep=',',
                           skipinitialspace=True,
                           skip_blank_lines=True,
                           comment='#',
                           dtype='str',
                           keep_default_na=False,
                           index_col=False)

# Set the connection params
hostname = sys.argv[2]
port = sys.argv[3]
user = sys.argv[4]
passwd = sys.argv[5]
dbname = sys.argv[6]

health_server = 'http://'+user+':'+passwd+'@'+hostname+':'+port+'/'+dbname+'/'

print ("Connecting to GNU Health Server ...")
conf = pconfig.set_xmlrpc(health_server)
# Use XML RPC using session
#conf = pconfig.set_xmlrpc_session(health_server, username=user, password=passwd)
print ("Connected !\n")

for index, line in patient_data.iterrows(): 
    print('---------------------------------------------------------')
    print(line)
    PartyDemographics(line)

