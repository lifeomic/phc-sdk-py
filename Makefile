PYTHON_MODULES := phc
PYTHONPATH := .
VENV := .venv
NOSE := env PYTHONPATH=$(PYTHONPATH) $(VENV)/bin/nosetests
FLAKE8 := env PYTHONPATH=$(PYTHONPATH) $(VENV)/bin/flake8
PYTHON := env PYTHONPATH=$(PYTHONPATH) $(VENV)/bin/python
BLACK := env PYTHONPATH=$(PYTHONPATH) $(VENV)/bin/black
PIP := $(VENV)/bin/pip

DEFAULT_PYTHON := /usr/bin/python3
VIRTUALENV := virtualenv

REQUIREMENTS := -r requirements-dev.txt

default: clean test

venv:
	test -d $(VENV) || $(VIRTUALENV) -p $(DEFAULT_PYTHON) -q $(VENV)

clean:
	rm -rf build
	rm -rf dist
	rm -rf phc.egg-info

requirements:
	@if [ -d wheelhouse ]; then \
					$(PIP) install -q --no-index --find-links=wheelhouse $(REQUIREMENTS); \
	else \
					$(PIP) install -q $(REQUIREMENTS); \
	fi

bootstrap: venv requirements

lint: bootstrap
	$(FLAKE8) $(PYTHON_MODULES)

format: bootstrap
	$(BLACK) $(PYTHON_MODULES)

test: lint
	$(NOSE) $(PYTHON_MODULES)/tests

package:
	$(PYTHON) setup.py sdist bdist_wheel

deploy:
	$(PYTHON) -m twine upload dist/*


.PHONY: default venv requirements bootstrap lint test check package deploy