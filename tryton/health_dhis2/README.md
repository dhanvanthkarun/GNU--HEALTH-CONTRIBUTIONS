<!--
SPDX-FileCopyrightText: 2023 Florian Liermann
SPDX-FileContributor: 2024 Modified by Brendan Wills

SPDX-License-Identifier: GPL-3.0-or-later
-->

# GNUHealth DHIS2
This is a module for the hospital information system GNU Health.
It allows GNU Health to connect to DHIS2 and send aggregate data to it.

## Installation
If GNU Health was installed with the Ansible script, just run the Makefile target `make build`. 
It will automatically install the package into the default path `/opt/gnuhealth/`. Otherwise adjust the path in build.sh. <br />
If you use a different path or do not use the demo database, you must adjust the paths and database name in the build.sh script like here:
```bash
trytond-admin -c {install_path}/etc/trytond.conf -d [DATABASE_NAME] -u health_dhis2 -v
```
Otherwise, install the module manually using pip:
```bash
python3 -m pip install ./health_dhis2
```


## Using the Tryton Worker
The worker is not required for this module, but improves synchronization times with DHIS2 and allows it to run in the background.
Before using the worker you need to enable it in the config file `{install_path}/etc/trytond.conf`. <br />
Insert or search for the following lines and set the worker to True.
```
[queue]
worker = True
```

### Starting the Worker via Makefile
After completing the above task you can start the worker via Makefile target `make worker`. 
This will start a node in the current shell as gnuhealth user. <br />
If you are using a different path or database, make sure to adjust them in build_worker.sh.


## Running Tests
Switch to `gnuhealth` user and go to the home directory.
```bash
sudo -u gnuhealth /bin/bash
cd ~
```
Next activate the python virtual environment.
```bash
source venv/bin/activate
```
The tests require the `responses` package to be installed.
It should already be installed in the virtual environment, but if not you need to install it.
```bash
pip install responses
```

Next we need to set the name of the database to be used for testing.
The [tyton documentation](https://docs.tryton.org/projects/server/en/latest/topics/testing.html#testing-options) says this step isn't needed and that it will automatically choose a random name, but it throws an error for me without it.
It is possible this is fixed in a newer version of tryton.
```bash
export DB_NAME=test_health_dhis2
```
Now we can run the tests:
```bash
python -m unittest discover -s trytond.modules.health_dhis2.tests
```
