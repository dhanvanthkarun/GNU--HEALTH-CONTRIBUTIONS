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
from trytond.model import Workflow, ModelView, ModelSQL, fields
from trytond.pyson import If, Or, Eval, Bool
from trytond.exceptions import UserError
from trytond.pool import Pool, PoolMeta
from trytond.modules.health.core import get_health_professional, \
    get_institution_currency


__all__ = ['Move',
           'PatientAmbulatoryCare', 'PatientAmbulatoryCareMedicament',
           'PatientAmbulatoryCareMedicalSupply'
           ]

_STATES = {
    'readonly': Eval('state') == 'done',
}
_DEPENDS = ['state']


class Move(metaclass=PoolMeta):
    __name__ = 'stock.move'

    @classmethod
    def _get_origin(cls):
        return super(Move, cls)._get_origin() + [
            'gnuhealth.patient.ambulatory_care',
        ]


class PatientAmbulatoryCare(Workflow, metaclass=PoolMeta):
    'Patient Ambulatory Care'
    __name__ = 'gnuhealth.patient.ambulatory_care'

    care_location = fields.Many2One(
        'stock.location', 'Care Location',
        domain=[('type', '=', 'storage')],
        states={
            'required': If(
                Or(Bool(Eval('medicaments')),
                    Bool(Eval('medical_supplies'))), True, False),
            'readonly': Eval('state') == 'done',
        }, depends=['state', 'medicaments'])
    medicaments = fields.One2Many(
        'gnuhealth.patient.ambulatory_care.medicament', 'ambcare',
        'Medicaments', states=_STATES, depends=_DEPENDS)
    medical_supplies = fields.One2Many(
        'gnuhealth.patient.ambulatory_care.medical_supply', 'ambcare',
        'Medical Supplies', states=_STATES, depends=_DEPENDS)

    moves = fields.One2Many(
        'stock.move', 'origin', 'Stock Moves',
        readonly=True)

    @classmethod
    def __setup__(cls):
        super(PatientAmbulatoryCare, cls).__setup__()
        cls._transitions |= set((
            ('draft', 'done'),
        ))
        cls._buttons.update({
            'done': {
                'invisible': ~Eval('state').in_(['draft']),
            }})

    @classmethod
    def copy(cls, ambulatory_cares, default=None):
        if default is None:
            default = {}
        default = default.copy()
        default['moves'] = None
        return super(PatientAmbulatoryCare, cls).copy(
            ambulatory_cares, default=default)

    @classmethod
    @ModelView.button
    @Workflow.transition('done')
    def done(cls, ambulatory_cares):
        lines_to_ship = {}
        medicaments_to_ship = []
        supplies_to_ship = []

        signing_hp = get_health_professional()

        for ambulatory in ambulatory_cares:
            for medicament in ambulatory.medicaments:
                medicaments_to_ship.append(medicament)

            for medical_supply in ambulatory.medical_supplies:
                supplies_to_ship.append(medical_supply)

        lines_to_ship['medicaments'] = medicaments_to_ship
        lines_to_ship['supplies'] = supplies_to_ship

        cls.create_stock_moves(ambulatory_cares, lines_to_ship)

        cls.write(ambulatory_cares, {
            'signed_by': signing_hp,
            'session_end': datetime.now()
        })

    @classmethod
    def create_stock_moves(cls, ambulatory_cares, lines):
        pool = Pool()
        Move = pool.get('stock.move')
        Date = pool.get('ir.date')
        moves = []
        for ambulatory in ambulatory_cares:
            for medicament in lines['medicaments']:
                move_info = {}
                move_info['origin'] = str(ambulatory)
                move_info['product'] = medicament.medicament.product.id
                move_info['unit'] = \
                    medicament.medicament.product.default_uom.id
                move_info['currency'] = get_institution_currency()
                move_info['quantity'] = medicament.quantity
                move_info['from_location'] = ambulatory.care_location.id
                move_info['to_location'] = \
                    ambulatory.patient.party.customer_location.id
                move_info['unit_price'] = \
                    medicament.medicament.product.list_price
                move_info['cost_price'] = \
                    medicament.medicament.product.cost_price
                if medicament.lot:
                    if medicament.lot.expiration_date and \
                            medicament.lot.expiration_date < Date.today():
                        raise UserError('Expired medicaments')
                    move_info['lot'] = medicament.lot.id
                moves.append(move_info)

            for medical_supply in lines['supplies']:
                move_info = {}
                move_info['origin'] = str(ambulatory)
                move_info['product'] = medical_supply.product.id
                move_info['unit'] = medical_supply.product.default_uom.id
                move_info['currency'] = get_institution_currency()
                move_info['quantity'] = medical_supply.quantity
                move_info['from_location'] = ambulatory.care_location.id
                move_info['to_location'] = \
                    ambulatory.patient.party.customer_location.id
                move_info['unit_price'] = medical_supply.product.list_price
                if medical_supply.lot:
                    if medical_supply.lot.expiration_date \
                            and medical_supply.lot.expiration_date \
                            < Date.today():
                        raise UserError('Expired supplies')
                    move_info['lot'] = medical_supply.lot.id
                moves.append(move_info)

        new_moves = Move.create(moves)
        Move.write(new_moves, {
            'state': 'done',
            'effective_date': Date.today(),
        })

        return True


class PatientAmbulatoryCareMedicament(ModelSQL, ModelView):
    'Patient Ambulatory Care Medicament'
    __name__ = 'gnuhealth.patient.ambulatory_care.medicament'

    ambcare = fields.Many2One(
        'gnuhealth.patient.ambulatory_care',
        'Ambulatory ID')
    medicament = fields.Many2One(
        'gnuhealth.medicament', 'Medicament',
        required=True)
    product = fields.Many2One('product.product', 'Product')
    quantity = fields.Integer('Quantity')
    short_comment = fields.Char(
        'Comment',
        help='Short comment on the specific drug')
    lot = fields.Many2One(
        'stock.lot', 'Lot', depends=['product'],
        domain=[('product', '=', Eval('product'))])

    @staticmethod
    def default_quantity():
        return 1

    @fields.depends('medicament')
    def on_change_medicament(self):
        if self.medicament:
            self.product = self.medicament.product.id

        else:
            self.product = None


class PatientAmbulatoryCareMedicalSupply(ModelSQL, ModelView):
    'Patient Ambulatory Care Medical Supply'
    __name__ = 'gnuhealth.patient.ambulatory_care.medical_supply'

    ambcare = fields.Many2One(
        'gnuhealth.patient.ambulatory_care',
        'Ambulatory ID')
    product = fields.Many2One(
        'product.product', 'Medical Supply',
        domain=[('is_medical_supply', '=', True)], required=True)
    quantity = fields.Integer('Quantity')
    short_comment = fields.Char(
        'Comment',
        help='Short comment on the specific drug')
    lot = fields.Many2One(
        'stock.lot', 'Lot', depends=['product'],
        domain=[
            ('product', '=', Eval('product')),
        ])

    @staticmethod
    def default_quantity():
        return 1
