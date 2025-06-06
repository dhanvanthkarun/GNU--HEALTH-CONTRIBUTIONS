# Copyright (C) 2008-2025 Luis Falcon <falcon@gnuhealth.org>
# Copyright (C) 2011-2025 GNU Solidario <health@gnusolidario.org>
# Copyright (C) 2013  Sebastian Marro <smarro@gnusolidario.org>
# SPDX-FileCopyrightText: 2008-2025 Luis Falcón <falcon@gnuhealth.org>
# SPDX-FileCopyrightText: 2011-2025 GNU Solidario <health@gnusolidario.org>
# SPDX-FileCopyrightText: 2013 Sebastian Marro <smarro@thymbra.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from trytond.wizard import Wizard, StateView, Button, StateTransition
from trytond.model import ModelView
from trytond.transaction import Transaction
from trytond.pool import Pool
from trytond.i18n import gettext
from trytond.modules.health.core import get_institution_currency

from ..exceptions import (StockMoveExists, NoStockOrigin)

__all__ = ['CreateVaccinationStockMoveInit', 'CreateVaccinationStockMove']


class CreateVaccinationStockMoveInit(ModelView):
    'Create Vaccination Stock Move Init'
    __name__ = 'gnuhealth.vaccination.stock.move.init'


class CreateVaccinationStockMove(Wizard):
    'Create Vaccination Stock Move'
    __name__ = 'gnuhealth.vaccination.stock.move.create'

    start = StateView(
        'gnuhealth.vaccination.stock.move.init',
        'health_stock.view_create_vaccination_stock_move', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Create Stock Move', 'create_stock_move', 'tryton-ok', True)
        ])
    create_stock_move = StateTransition()

    def transition_create_stock_move(self):
        pool = Pool()
        StockMove = pool.get('stock.move')
        Vaccination = pool.get('gnuhealth.vaccination')

        vaccinations = Vaccination.browse(Transaction().context.get(
            'active_ids'))
        for vaccination in vaccinations:

            if vaccination.moves:
                raise StockMoveExists(
                    gettext('health_stock.msg_stock_move_exists')
                )

            if not vaccination.location:
                raise NoStockOrigin(
                    gettext('health_stock.msg_no_location_origin')
                )

            lines = []

            line_data = {}
            line_data['origin'] = str(vaccination)
            line_data['from_location'] = \
                vaccination.location.id
            line_data['to_location'] = \
                vaccination.patient.party.customer_location.id
            line_data['product'] = \
                vaccination.vaccine.product.id
            line_data['unit_price'] = \
                vaccination.vaccine.product.list_price
            line_data['cost_price'] = \
                vaccination.vaccine.product.cost_price
            line_data['quantity'] = 1
            line_data['unit'] = \
                vaccination.vaccine.product.default_uom.id
            # Use the institution currency in the stock move
            line_data['currency'] = get_institution_currency()
            line_data['state'] = 'draft'
            lines.append(line_data)

            moves = StockMove.create(lines)

            StockMove.assign(moves)
            StockMove.do(moves)

        return 'end'
