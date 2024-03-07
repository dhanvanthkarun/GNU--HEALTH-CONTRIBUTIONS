# SPDX-FileCopyrightText: 2008-2023 Luis Falcón <falcon@gnuhealth.org>
# SPDX-FileCopyrightText: 2011-2014 Sebastian Marro <smarro@thymbra.com>
# SPDX-FileCopyrightText: 2011-2023 GNU Solidario <health@gnusolidario.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from . import wizard_top_diseases
from . import wizard_evaluations
from . import wizard_summary_report
from . import wizard_epidemics_report


__all__ = ['wizard_top_diseases', 'wizard_evaluations',
           'wizard_summary_report', 'wizard_epidemics_report']
