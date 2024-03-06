# SPDX-FileCopyrightText: 2008-2023 Luis Falcón <falcon@gnuhealth.org>
# SPDX-FileCopyrightText: 2011-2023 GNU Solidario <health@gnusolidario.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later
from trytond.model.exceptions import ValidationError


class PatientAlreadyInICU(ValidationError):
    pass


class PatientAlreadyOnMV(ValidationError):
    pass
