VENV = .venv
VENV_ACTIVATE = $(shell test -d $(VENV) && find $(VENV) -name "activate")
VENV_PYTHON = $(shell test -d $(VENV) && . $(VENV)/bin/activate && which python)
SYSTEM_PYTHON = $(shell which python)
PYTHON = $(or $(VENV_PYTHON), $(SYSTEM_PYTHON), "PYTHONNOTFOUND")

PACKAGE = $(shell grep "^name" pyproject.toml | awk -F'"' '{print $$2}')
BUILD_CACHE = $(PACKAGE).egg-info

$(VENV):
	$(SYSTEM_PYTHON) -m venv $(VENV)

$(BUILD_CACHE): pyproject.toml | $(VENV)
	@echo "Installing dependencies with $(PYTHON)"
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -e .

user_install: | $(VENV) $(BUILD_CACHE)
install: $(BUILD_CACHE)


SRC = src tests

.PHONY: format lint test kedro-run

format:
	black $(SRC)

lint:
	pylint $(SRC)
test:
	pytest


ADD_OPTS = # None by default
run:
	kedro run $(ADD_OPTS)

.PHONY: kedro-run