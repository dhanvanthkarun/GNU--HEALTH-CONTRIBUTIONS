#!/bin/sh

# SPDX-FileCopyrightText: 2023 Florian Liermann
# SPDX-FileContributor: 2024 Modified by Brendan Wills
#
# SPDX-License-Identifier: GPL-3.0-or-later


# You should not use this file directly. Use the Makefile command 'make build'

# Set variable to ensure the same path
HEALTHPATH=/opt/gnuhealth

# Copy data to GNU Health
cp README.md health_dhis2/
cp -r health_dhis2 $HEALTHPATH
cp configs/trytond_worker_log.conf $HEALTHPATH/etc
chown -R gnuhealth $HEALTHPATH/health_dhis2
chown gnuhealth $HEALTHPATH/etc/trytond_worker_log.conf

# Switch to gnuhealth user
exec sudo -u gnuhealth /bin/bash - << eof

# Install module
source ~/venv/bin/activate
python3 -m pip install ~/health_dhis2
trytond-admin -c ~/etc/trytond.conf -d ghdemo44 -u health_dhis2 -v
echo "Installed Module"

# Restart server
echo "Restarting Gnu Health Service"
systemctl restart gnuhealth.service --no-block
exit