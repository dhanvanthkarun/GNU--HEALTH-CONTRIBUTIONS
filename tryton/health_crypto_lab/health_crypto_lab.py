# SPDX-FileCopyrightText: 2008-2025 Luis Falcón <falcon@gnuhealth.org>
# SPDX-FileCopyrightText: 2011-2025 GNU Solidario <health@gnusolidario.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

#########################################################################
#   Hospital Management Information System (HMIS) component of the      #
#                       GNU Health project                              #
#                   https://www.gnuhealth.org                           #
#########################################################################
#                    HEALTH CRYPTO LAB package                          #
#                health_crypto_lab.py: main module                      #
#########################################################################
from datetime import datetime
from trytond.model import ModelView, fields
from trytond.rpc import RPC
from trytond.pool import PoolMeta
from trytond.pyson import Eval, Not, Bool
import hashlib
import json
from trytond.modules.health.core import get_health_professional

__all__ = ['LabTest']


class LabTest(metaclass=PoolMeta):
    __name__ = 'gnuhealth.lab'

    serializer = fields.Text('Doc String', readonly=True)

    document_digest = fields.Char(
        'Digest', readonly=True,
        help="Original Document Digest")

    digest_status = fields.Function(
        fields.Boolean(
            'Altered',
            help="This field will be set whenever parts of"
            " the main original document has been changed."
            " Please note that the verification is done only on selected"
            " fields."),
        'check_digest')

    serializer_current = fields.Function(
        fields.Text(
            'Current Doc',
            states={
                'invisible': Not(Bool(Eval('digest_status'))),
            }),
        'check_digest')

    digest_current = fields.Function(
        fields.Char(
            'Current Hash',
            states={
                'invisible': Not(Bool(Eval('digest_status'))),
            }),
        'check_digest')

    digital_signature = fields.Text('Digital Signature', readonly=True)

    @classmethod
    def __setup__(cls):
        super(LabTest, cls).__setup__()
        ''' Allow calling the set_signature method via RPC '''
        cls.__rpc__.update({
            'set_signature': RPC(readonly=False),
        })

    @classmethod
    @ModelView.button
    def sign_document(cls, documents):
        document = documents[0]

        # Validate / generate digest for the document
        # and write the name of the signing health professional
        hp = get_health_professional()

        serial_doc = cls.get_serial(document)

        cls.write(documents, {
            'serializer': serial_doc,
            'document_digest': HealthCrypto().gen_hash(serial_doc),
            'validated_by': hp,
            'validation_date': datetime.now(),
            'state': 'validated', })

    @classmethod
    def get_serial(cls, document):

        analyte_line = []

        for line in document.critearea:
            line_elements = [
                line.name or '',
                line.result or '',
                line.units and line.units.name or '',
                line.result_text or '',
                line.remarks or '']

            analyte_line.append(line_elements)

        data_to_serialize = {
            'Lab_test': str(document.name) or '',
            'Test': str(document.test.rec_name) or '',
            'Specimen_type': str(document.specimen_type),
            'HP': (document.requestor
                   and str(document.requestor.rec_name)
                   or ''),
            'Source_type': str(document.source_type),
            'Patient': (document.patient
                        and str(document.patient.rec_name)
                        or ''),
            'Other_source': str(document.other_source) or '',
            'Patient_ID': (document.patient
                           and str(document.patient.party.ref)
                           or ''),
            'Analyte_line': str(analyte_line),
        }

        serialized_doc = str(HealthCrypto().serialize(data_to_serialize))

        return serialized_doc

    @classmethod
    def set_signature(cls, data, signature):
        """
        Set the clearsigned signature
        """

        doc_id = data['id']

        cls.write([cls(doc_id)], {
            'digital_signature': signature,
        })

    def check_digest(self, name):
        result = ''
        serial_doc = self.get_serial(self)
        if (name == 'digest_status' and self.document_digest):
            if (HealthCrypto().gen_hash(serial_doc) == self.document_digest):
                result = False
            else:
                ''' Return true if the document has been altered'''
                result = True
        if (name == 'digest_current'):
            result = HealthCrypto().gen_hash(serial_doc)

        if (name == 'serializer_current'):
            result = serial_doc

        return result

    # Hide the group holding validation information when state is
    # not validated

    @classmethod
    def view_attributes(cls):
        return [('//group[@id="document_digest"]', 'states', {
                'invisible': Not(Eval('state') == 'validated'),
                })]


class HealthCrypto:
    """ GNU Health Cryptographic functions
    """

    def serialize(self, data_to_serialize):
        """ Format to JSON """

        json_output = \
            json.dumps(data_to_serialize, ensure_ascii=False)
        return json_output

    def gen_hash(self, serialized_doc):
        return hashlib.sha512(serialized_doc.encode('utf-8')).hexdigest()
