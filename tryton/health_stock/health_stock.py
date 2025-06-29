# SPDX-FileCopyrightText: 2008-2025 Luis Falcón <falcon@gnuhealth.org>
# SPDX-FileCopyrightText: 2013 Sebastian Marro <smarro@thymbra.com>
# SPDX-FileCopyrightText: 2011-2025 GNU Solidario <health@gnusolidario.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#########################################################################
#   Hospital Management Information System (HMIS) component of the      #
#                       GNU Health project                              #
#                   https://www.gnuhealth.org                           #
#########################################################################
#                         HEALTH REPORTING package                      #
#                       health_stock.py: main module                    #
#########################################################################
from datetime import datetime
from trytond.model import fields
from trytond.pyson import Eval, Not, Bool
from trytond.pool import Pool, PoolMeta
from trytond.i18n import gettext

from .exceptions import (ExpiredVaccine)

__all__ = ['Party', 'Lot', 'Move',
           'PatientPrescriptionOrder', 'PatientVaccination']

_STATES = {
    'readonly': Eval('state') == 'done',
}
_DEPENDS = ['state']


class Party(metaclass=PoolMeta):
    __name__ = 'party.party'
    warehouse = fields.Many2One(
        'stock.location', 'Warehouse',
        domain=[('type', 'in', ['warehouse', 'storage'])],
        states={
            'invisible': Not(Bool(Eval('is_pharmacy'))),
            'required': Bool(Eval('is_pharmacy')),
        },
        depends=['is_pharmacy'])

    @classmethod
    def default_warehouse(cls):
        Location = Pool().get('stock.location')
        locations = Location.search(cls.warehouse.domain)
        if len(locations) == 1:
            return locations[0].id


class Lot(metaclass=PoolMeta):
    __name__ = 'stock.lot'
    expiration_date = fields.Date('Expiration Date')


class Move(metaclass=PoolMeta):
    __name__ = 'stock.move'

    @classmethod
    def _get_origin(cls):
        return super(Move, cls)._get_origin() + [
            'gnuhealth.prescription.order',
            'gnuhealth.vaccination',
        ]


class PatientPrescriptionOrder(metaclass=PoolMeta):
    __name__ = 'gnuhealth.prescription.order'
    moves = fields.One2Many('stock.move', 'origin', 'Moves', readonly=True)

    @classmethod
    def __setup__(cls):
        super(PatientPrescriptionOrder, cls).__setup__()
        cls.pharmacy.states['readonly'] &= Bool(Eval('moves'))

    @classmethod
    def copy(cls, prescriptions, default=None):
        if default is None:
            default = {}
        default = default.copy()
        default['moves'] = None
        return super(PatientPrescriptionOrder, cls).copy(
            prescriptions, default=default)


class PatientVaccination(metaclass=PoolMeta):
    __name__ = 'gnuhealth.vaccination'
    moves = fields.One2Many('stock.move', 'origin', 'Moves', readonly=True)
    location = fields.Many2One(
        'stock.location',
        'Stock Location', domain=[('type', '=', 'storage')])

    product = fields.Many2One('product.product', 'Product')

    lot = fields.Many2One(
        'stock.lot', 'Lot', depends=['product'],
        domain=[('product', '=', Eval('product'))],
        help="This field includes the lot number and expiration date")

    @fields.depends('lot', 'date')
    def on_change_lot(self):
        # Check expiration date on the vaccine lot
        if self.lot and self.date:
            if self.lot.expiration_date < datetime.date(self.date):
                raise ExpiredVaccine(
                    gettext('health_stock.msg_expired_vaccine')
                )

    @classmethod
    def copy(cls, vaccinations, default=None):
        if default is None:
            default = {}
        default = default.copy()
        default['moves'] = None
        return super(PatientVaccination, cls).copy(
            vaccinations, default=default)

    @fields.depends('vaccine')
    def on_change_vaccine(self):
        if self.vaccine:
            self.product = self.vaccine.product.id
        else:
            self.product = None
