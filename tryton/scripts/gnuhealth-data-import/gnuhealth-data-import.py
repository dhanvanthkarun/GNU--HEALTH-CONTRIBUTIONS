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

import os
import sys
import csv
import argparse

from datetime import datetime
from decimal import Decimal
from proteus import Model
from proteus import config as pconfig

import pandas as pd

def main():
    options = parse_options()
    filenames = get_filenames(options)
    connect_service(options)
    import_files(filenames, options)
    import_finish()

def parse_options():
    parser = argparse.ArgumentParser()

    parser.add_argument('-f', '--filenames', nargs='+',
                        help="A list of csv or ods files.",
                        default=[])
    parser.add_argument('-D', '--directory',
                        help="A directory which contain csv or ods data files.")
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
    parser.add_argument('-t', '--datatype', required=False,
                        help="Type of imported data, "
                        "its value can be 'patient', 'medicament', "
                        "'produce' or 'labtest' at the moment, "
                        "override by '_type' field of csv or odt file.")

    return parser.parse_args()

def get_filenames(options):
    filenames = []
    if options.directory:
        filenames = os.listdir(options.directory)
    filenames = [os.path.join(options.directory, f) for f in filenames]
    return options.filenames + filenames

def connect_service(options):
    hostname = options.hostname
    port     = options.port
    user     = options.user
    passwd   = options.passwd
    dbname   = options.database

    health_server = 'http://'+user+':'+passwd+'@'+hostname+':'+port+'/'+dbname+'/'
    
    print("## Connecting to GNU Health Server ...")
    conf = pconfig.set_xmlrpc(health_server)
    # Use XML RPC using session
    #conf = pconfig.set_xmlrpc_session(health_server, username=user, password=passwd)
    print("## Connected!\n")

def import_files(filenames, options):
    for filename in filenames:
        data = read_file(filename)
        import_data(data, options)

def read_file(filename):
    if filename.endswith('ods'):
        return pd.read_excel(filename,
                             ## Note: user need install odfpy
                             ## package.
                             engine='odf',
                             dtype='str',
                             keep_default_na=False,
                             index_col=False)    
    elif filename.endswith('csv'):
        return pd.read_csv(filename,
                           sep=',',
                           skipinitialspace=True,
                           skip_blank_lines=True,
                           comment='#',
                           dtype='str',
                           keep_default_na=False,
                           index_col=False)
    else:
        print(f'## Do not support import: {filename}')

def import_data(data, options):
    for index, line in data.iterrows():
        line = dict(line)
        ignore = line.get('_ignore')
        data_type = line.get('_type') or options.datatype or 'default'
        if not ignore == 'yes':
            ## Call function which name is 'import_line_<data_type>'.
            eval('import_line_' + data_type)(line)

def import_line_patient(line):
    fed_country        =  line.get("fed_country")
    name               =  line.get("first_name")
    lastname           =  line.get("family_name")
    name_repr          =  line.get("name_representation")
    puid               =  line.get("puid")
    gender             =  line.get("gender")
    dob                =  line.get("dob")
    phone              =  line.get("phone")
    alt_id             =  line.get("alternative_id")
    other_alt_id_type  =  line.get("other_alternative_id_type")
    alt_id_cmt         =  line.get("alternative_id_comments")
    addr_1             =  line.get("addr_1")
    addr_cont          =  line.get("addr_cont")
    active_date        =  line.get("activation_date")

    print("* Importing patient: '{0}, {1}' ...".format(name, lastname))

    Party = Model.get('party.party')
    PartyAddress = Model.get('party.address')
    PartyAlternativeID = Model.get('gnuhealth.person_alternative_identification')
    ContactMethod = Model.get('party.contact_mechanism')
    Patient = Model.get('gnuhealth.patient')

    party = get_record(Party, 
                       [('ref', '=', puid)],
                       [('alternative_ids.code', '=', alt_id)])
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
        
        if not [x for x in party.contact_mechanisms if x.value == phone]:
            party.contact_mechanisms.append(contactmethod)
        
    # Set alternative Identification
    if alt_id:
        party.alternative_identification = True
        altid = PartyAlternativeID()
        altid.alternative_id_type = 'other'
        altid.other_alternative_id_type = other_alt_id_type
        altid.code = alt_id
        altid.comments = alt_id_cmt

        if not [x for x in party.alternative_ids if x.code == alt_id]:
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
    
    patient = get_record(Patient,
                         [('name.ref', '=', party.ref)])
    patient.name = party
    patient.save()

def get_record(model, *domains):
    records = []

    for domain in domains:
        records = records + model.find(domain)

    if records:
        return records[0]
    else:
        return model()

def import_line_labtest(line):
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
            print("* Importing labtest: '{0}/{1}' ...".format(
                test_id, (analyte_code or analyte_name or "Unknow")))
    else:
        print("! Ignore labtest: '{0}/{1}', it is not found !!!".format(
            test_id, (analyte_code or analyte_name or "Unknow")))

def import_line_medicament(line):
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
    product = get_record(ProductTemplate,
                         [('code', '=', prd_code)])
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
    print("* Importing product: '{0} ({1})'".format(product.name, product.code))

    product.save()
        
    ## Create medicament with related product
    print(f"* Importing medicament: '{name}' ...")
    med = get_record(Medicament,
                     [('name.code', '=', prd_code)])
    med.name, = ProductVariant.find([('code', '=', prd_code)])
    med.strength = int(strength)
    med.unit = dose_unit
    med.form, = MedForm.find([('code', '=', med_form)])

    med.save()

def import_line_product(line):
    name       = line.get('name')
    list_price = line.get('list_price')
    cost_price = line.get('cost_price')
    prd_type   = line.get('type')
    uom        = line.get('uom')
    prd_code   = line.get('code')

    # Update the model with the result values
    print("* Importing product: '{0}' ...".format(name))
    ProductInfo = Model.get('product.template')
    ProductUOM = Model.get('product.uom')
    ProductVariant = Model.get('product.product')

    product = get_record(ProductInfo,
                         [('code', '=', prd_code)])
    product.name = name
    product.code = prd_code
    product.list_price = Decimal(list_price)
    uom_val, = ProductUOM.find([('symbol', '=', uom)])
    product.default_uom = uom_val
    product.type = prd_type

    variant, = product.products
    variant.cost_price = Decimal(cost_price)

    product.save()

def import_line_default(line):
    print("! Importing Error: '_type' value error: {0}!".format(line))

def import_finish():
    print('\n## Import finished!')

if __name__ == '__main__':
    main()
