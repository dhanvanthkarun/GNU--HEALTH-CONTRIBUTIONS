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
#                       gnuhealth_product_uploader.py                   #
#         Sample script to upload products from a CSV file              #
#########################################################################

# Requirements
# Proteus version : 6.0.x
# pip3 install --upgrade --user "proteus>=6.0,<6.1"

# ##### Usage ########
# meds_uploader.py <csv_file> <hostname> <port> <user> <password> <dbname>

# Medicament CSV Format
# Name,List Price,Cost Price,Type,UOM, strength, strength_unit, form, code
# Sample csv content
# "Vitamin B12 - 500ug",30,20,"goods","Unit",500,"ug","TAB", "VITB12-500ug"


from proteus import Model
from proteus import config as pconfig
from decimal import Decimal

import csv
import sys


def input_results():
    csv_file = csv.reader(open(sys.argv[1], "r"))

    ProductTemplate = Model.get('product.template')
    ProductUOM = Model.get('product.uom')
    ProductVariant = Model.get('product.product')
    Medicament = Model.get('gnuhealth.medicament')
    DoseUnit = Model.get('gnuhealth.dose.unit')
    MedForm = Model.get('gnuhealth.drug.form')

    for line in csv_file:
        product = ProductTemplate()
        name = line[0]
        list_price = line[1]
        cost_price = line[2]
        prd_type = line[3]
        uom = line[4]
        strength = line[5]
        dose_uom = line[6]
        med_form = line[7]
        prd_code = line[8]  # Product code - eg, "VITB12-500ug"
        # Update the model with the result values

        # Create template

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
        print(product.name, product.code)

        product.save()
        
        # Create medicament with related product
        print(f"Creating the medicament associated to {name}...")
        med = Medicament()
        med.name, = ProductVariant.find([('code', '=', prd_code)])
        med.strength = int(strength)
        med.unit = dose_unit
        med.form, = MedForm.find([('code', '=', med_form)])

        med.save()


if (len(sys.argv) < 2):
    exit("Usage: meds_uploader.py <csv_file> <hostname> <port> "
         "<user> <password> <dbname>")

# Set the connection params

hostname = sys.argv[2]
port = sys.argv[3]
user = sys.argv[4]
passwd = sys.argv[5]
dbname = sys.argv[6]

health_server = f'http://{user}:{passwd}@{hostname}:{port}/{dbname}/'

print(f"Connecting to GNU Health Server {health_server}")
conf = pconfig.set_xmlrpc(health_server)
print("Connected !")

print("Updating medicaments from batch file ...")
input_results()
print("Done !")
