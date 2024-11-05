#!/bin/sh

# SPDX-FileCopyrightText: 2024 Brendan Wills
#
# SPDX-License-Identifier: GPL-3.0-or-later


# You should not use this file directly. Use the Makefile command 'make worker'

# Before you use the worker you need to ensure that the worker is turned on.
# Check the {path_to_gnu_health}/etc/trytond.conf file. Otherwise read the README.md


# Restart trytond worker service
systemctl restart tryton-server-worker.service

# Switch to gnuhealth user and start the worker node
exec sudo -u gnuhealth /bin/bash - << eof
source ~/venv/bin/activate

echo "Tryton Worker ist listening to synchronizaton calls..."
trytond-worker -c ~/etc/trytond.conf -d ghdemo44 --logconf ~/etc/trytond_worker_log.conf