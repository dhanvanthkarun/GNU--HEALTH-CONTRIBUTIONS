#!/usr/bin/env bash

# SPDX-FileCopyrightText: 2008-2024 Luis Falcón <falcon@gnuhealth.org>
# SPDX-FileCopyrightText: 2011-2024 GNU Solidario <health@gnusolidario.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

# This script will link modules in gnuhealth git repo to gnuhealth
# install directory, only applicable for developer testing purposes.

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
