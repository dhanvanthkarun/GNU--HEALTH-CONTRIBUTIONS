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
# product_uploader.py <csv_file> <hostname> <port> <user> <password> <dbname>

# Product CSV Format
# Name,List Price,Cost Price,Type,UOM
# Sample csv content
# "Rapid urease test",15,12,"service","Unit"


from proteus import Model
from proteus import config as pconfig

import csv
import sys

from decimal import Decimal


def input_results():
    ProductInfo = Model.get('product.template')
    ProductUOM = Model.get('product.uom')
    csv_file = csv.reader(open(sys.argv[1], "r"))
    for line in csv_file:
        name = line[0]
        list_price = line[1]
        cost_price = line[2]
        prd_type = line[3]
        uom = line[4]
        # Update the model with the result values
        print("Uploading product", line)
        product = ProductInfo()
        product.name = name
        product.list_price = Decimal(list_price)
        product.cost_price = Decimal(cost_price)
        uom_val, = ProductUOM.find([('symbol', '=', uom)])
        product.default_uom = uom_val
        product.type = prd_type

        product.save()


if (len(sys.argv) < 2):
    exit("Usage: product_uploader.py <csv_file> <hostname> <port> "
         "<user> <password> <dbname>")

# Set the connection params
print(sys.argv)

hostname = sys.argv[2]
port = sys.argv[3]
user = sys.argv[4]
passwd = sys.argv[5]
dbname = sys.argv[6]

health_server = f'http://{user}:{passwd}@{hostname}:{port}/{dbname}/'

print(f"Connecting to GNU Health Server {health_server}")
conf = pconfig.set_xmlrpc(health_server)
print("Connected !")

print("Updating products from batch file ...")
input_results()
print("Done !")
