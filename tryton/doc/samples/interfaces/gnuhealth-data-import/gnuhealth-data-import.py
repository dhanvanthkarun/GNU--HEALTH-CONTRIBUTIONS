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
#                       gnuhealth-data-import.py                        #
#               Sample script to import data to gnuhealth               #
#########################################################################

from datetime import datetime
import sys
import csv
import argparse
import attr

from decimal import Decimal
from proteus import Model
from proteus import config as pconfig

import pandas as pd

def main():
    options = parse_options()
    filename = options.filename
    data = read_file(filename)
    connect_service(options)
    import_data(data)

def parse_options():
    parser = argparse.ArgumentParser()

    parser.add_argument('-f', '--filename', required=True,
                        help="A csv or ods file.")
    parser.add_argument('-H', '--hostname', default='localhost',
                        help="Hostname of GNU Health Service, default=localhost.")
    parser.add_argument('-p', '--port', default='8000',
                        help="Port of GNU Health Service, default=8000.")
    parser.add_argument('-u', '--user', default='admin',
                        help="User name of GNU Health, default=admin.")
    parser.add_argument('-P', '--passwd', required=True,
                        help="Password of GNU Health.")
    parser.add_argument('-d', '--database', required=True,
                        help="Database name of GNU Health.")

    return parser.parse_args()

def connect_service(options):
    hostname = options.hostname
    port     = options.port
    user     = options.user
    passwd   = options.passwd
    dbname   = options.database

    health_server = 'http://'+user+':'+passwd+'@'+hostname+':'+port+'/'+dbname+'/'
    
    print("Connecting to GNU Health Server ...")
    conf = pconfig.set_xmlrpc(health_server)
    # Use XML RPC using session
    #conf = pconfig.set_xmlrpc_session(health_server, username=user, password=passwd)
    print("Connected!")

def read_file(filename):
    if filename.endswith('ods'):
        return pd.read_excel(filename,
                             ## Note: user need install odfpy
                             ## package.
                             engine='odf',
                             dtype='str',
                             keep_default_na=False,
                             index_col=False)    
    else:
        return pd.read_csv(filename,
                           sep=',',
                           skipinitialspace=True,
                           skip_blank_lines=True,
                           comment='#',
                           dtype='str',
                           keep_default_na=False,
                           index_col=False)

def import_data(data):
    print('-----------------------------------------------')

    for index, line in data.iterrows():
        line = dict(line)
        ignore = line.get('_ignore')
        data_type = line.get('_type') or 'default'
        if not ignore == 'yes':
            ## Call function which name is 'import_<data_type>'.
            eval('import_' + data_type)(line)
            
    print('-----------------------------------------------')
    print('Import finished!')

def import_patient(line):
    fed_country = line.get("fed_country")
    name        = line.get("first_name")
    lastname    = line.get("family_name")
    name_repr   = line.get("name_representation")
    puid        = line.get("puid")
    gender      = line.get("gender")
    dob         = line.get("dob")
    phone       = line.get("phone")
    alt_id      = line.get("alternative_id")
    alt_id_cmt  = line.get("alternative_id_comments")
    addr_1      = line.get("addr_1")
    addr_cont   = line.get("addr_cont")
    active_date = line.get("activation_date")

    print("* Importing '{0}, {1}' to GNU health ...".format(name, lastname))

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

def import_labtest(line):
    test_id      = line.get('test_id')
    analyte_code = line.get('analyte_code')
    analyte_name = line.get('analyte_name')
    result       = line.get('result')
    result_text  = line.get('result_text')

    LabTestLine = Model.get('gnuhealth.lab.test.critearea')
    ## NOTE: We prefer 'analyte_code' to 'analyte_name', for
    ## 'analyte_name' will change when user use different languages.
    domain = [['OR', 
               ('code','=',analyte_code),
               ('name','=',analyte_name)],
              ('gnuhealth_lab_id','=',test_id)]
    test_lines = LabTestLine.find(domain)
    
    ## Update the model with the result values
    if test_lines:
        for result_line in test_lines:
            try:
                result_line.result = float(result)
            except:
                result_line.result = None
            result_line.result_text = result_text
            result_line.save()
            print("NOTE: '{0}/{1}' import success!".format(test_id, analyte_code))
    else:
        print("WARN: '{0}/{1}' is not found, ignore ...".format(test_id, analyte_code))

def import_medicament(line):
    name       = line.get('name')
    list_price = line.get('list_price')
    cost_price = line.get('cost_price')
    prd_type   = line.get('type')
    uom        = line.get('uom')
    strength   = line.get('strength')
    dose_uom   = line.get('strength_unit')
    med_form   = line.get('form')
    ## Product code - eg, "VITB12-500ug"
    prd_code   = line.get('code')

    ## Update the model with the result values
    ProductTemplate = Model.get('product.template')
    ProductUOM = Model.get('product.uom')
    ProductVariant = Model.get('product.product')
    Medicament = Model.get('gnuhealth.medicament')
    DoseUnit = Model.get('gnuhealth.dose.unit')
    MedForm = Model.get('gnuhealth.drug.form')

    ## Create template
    product = ProductTemplate()
    product.name = name
    product.code = prd_code
    product.consumable = True
    product.purchasable = True
    product.list_price = Decimal(list_price)
    uom_val, = ProductUOM.find([('symbol', '=', uom)])
    dose_unit, = DoseUnit.find([('name', '=', dose_uom)])
    product.default_uom = uom_val
    product.type = prd_type

    variant, = product.products
    variant.is_medicament = True
    variant.cost_price = Decimal(cost_price)
    print("Importing product: '{0} ({1})'".format(product.name, product.code))

    product.save()
        
    ## Create medicament with related product
    print(f"Importing medicament: '{name}' ...")
    med = Medicament()
    med.name, = ProductVariant.find([('code', '=', prd_code)])
    med.strength = int(strength)
    med.unit = dose_unit
    med.form, = MedForm.find([('code', '=', med_form)])

    med.save()

def import_product(line):
    name       = line.get('name')
    list_price = line.get('list_price')
    cost_price = line.get('cost_price')
    prd_type   = line.get('type')
    uom        = line.get('uom')

    # Update the model with the result values
    print("Importing product: '{0}' ...".format(name))
    ProductInfo = Model.get('product.template')
    ProductUOM = Model.get('product.uom')
    product = ProductInfo()
    product.name = name
    product.list_price = Decimal(list_price)
    product.cost_price = Decimal(cost_price)
    uom_val, = ProductUOM.find([('symbol', '=', uom)])
    product.default_uom = uom_val
    product.type = prd_type

    product.save()

def import_default(line):
    print("Error: '_type' value error: {0}!".format(line))


if __name__ == '__main__':
    main()
