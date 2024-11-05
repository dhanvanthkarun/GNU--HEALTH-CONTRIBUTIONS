# SPDX-FileCopyrightText: 2024 Brendan Wills
#
# SPDX-License-Identifier: GPL-3.0-or-later

SHELL := /bin/bash

help:
	@echo "clean - remove all unnessacary artifacts"
	@echo "develop - create a clean venv and install all requirements"
	@echo "test-lint - tests package integrity via ruffs linter"
	@echo "lint - clean up of all linting violations stated in ruff.toml"
	@echo "build - install the package for Gnu Health"
	@echo "worker - start a worker node to listen to calls"

clean: 
	find . -name 'build' -exec rm -rf {} +
	find . -name '*.egg-info' -exec rm -rf {} +
	find . -name '*.egg' -exec rm -f {} +
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -rf {} +
	find . -name '.ruff_cache' -exec rm -rf {} +

develop: clean
	-rm -rf .venv/
	python3 -m venv .venv
	source .venv/bin/activate && \
		pip install -U pip && \
		pip install -U -r requirements.txt

lint:
	ruff check --fix

test-lint:
	ruff check health_dhis2

build: clean
	@echo "Starting build of package."
	@chmod +x configs/build.sh
	@sudo ./configs/build.sh
	@echo "Building package has finished."

worker:
	@echo "Starting worker"
	@chmod +x configs/build_worker.sh
	@sudo ./configs/build_worker.sh
