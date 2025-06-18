VENV = .venv

# Path to the virtual environment's activate script (if the venv exists)
VENV_ACTIVATE = $(shell test -d $(VENV) && find $(VENV) -name "activate")

# Python interpreter path inside the virtual environment (if it exists and can be activated)
VENV_PYTHON = $(shell test -d $(VENV) && . $(VENV)/bin/activate && which python)

# System-wide Python interpreter path
SYSTEM_PYTHON = $(shell which python)

# Use Python from virtualenv if available, else fallback to system Python, else show error
PYTHON = $(or $(VENV_PYTHON), $(SYSTEM_PYTHON), "PYTHONNOTFOUND")

# Package name extracted from pyproject.toml
PACKAGE = $(shell grep "^name" pyproject.toml | awk -F'"' '{print $$2}')

# Build cache directory (egg-info folder)
BUILD_CACHE = $(PACKAGE).egg-info

# Create a Python virtual environment if it doesn't exist
$(VENV):
	$(SYSTEM_PYTHON) -m venv $(VENV)

# Install project dependencies in the virtual environment.
# This target depends on pyproject.toml and the virtual environment existing.
$(BUILD_CACHE): pyproject.toml | $(VENV)
	@echo "Installing dependencies with $(PYTHON)"
	# Upgrade pip to the latest version
	$(PYTHON) -m pip install --upgrade pip
	# Install the current package in editable mode (-e)
	$(PYTHON) -m pip install -e .

# Alias target to create venv and install dependencies for user
user_install: | $(VENV) $(BUILD_CACHE)

# Alias for install target
install: $(BUILD_CACHE)

SRC = src tests

# Declare these targets as phony (not actual files)
.PHONY: format lint test kedro-run

# Format all Python files in SRC using Black
format:
	black $(SRC)

# Lint all Python files in SRC using pylint
lint:
	pylint $(SRC)

# Run tests using pytest
test:
	pytest

# Additional options for kedro run can be set here (empty by default)
ADD_OPTS = # None by default

# Run Kedro pipeline with optional extra arguments
run:
	kedro run $(ADD_OPTS)

.PHONY: kedro-run

# Run the Streamlit web app
web_app:
	streamlit run streamlit_app/app.py
	
.PHONY: web_app
