#!/usr/bin/env bash

# SPDX-FileCopyrightText: 2008-2024 Luis Falcón <falcon@gnuhealth.org>
# SPDX-FileCopyrightText: 2011-2024 GNU Solidario <health@gnusolidario.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

# Some tools, such as: po-export, require developers to install the
# latest code from gnuhealth-git, it is a frequent and cumbersome
# operation.

# This script will link modules in gnuhealth git repo to the
# installation directory of gnuhealth, avoiding frequent
# installations.

# WARN: Only used for development environment.

source $HOME/.gnuhealthrc

DIR=$(dirname "$(realpath "${BASH_SOURCE[0]}")")
MODULES_DIR=$(realpath "${DIR}/../..")
INSTALL_DIR=${GNUHEALTH_DIR}/tryton/server/modules/

for module in $(ls ${MODULES_DIR} | grep ^health)
do
    rm -rf ${INSTALL_DIR}/${module}
    echo "# ln -s ${MODULES_DIR}/${module} ${INSTALL_DIR}"
    ln -s ${MODULES_DIR}/${module} ${INSTALL_DIR}
done
