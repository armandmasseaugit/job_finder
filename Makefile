# ==================================================================================
# CONFIGURATION
# ==================================================================================

# Project configuration
VENV = .venv
PACKAGE = job_finder
PYTHON_VERSION = 3.9

# Platform-specific commands
ifeq ($(OS),Windows_NT)
    VENV_BIN = $(VENV)/Scripts
    PYTHON = $(VENV_BIN)/python.exe
    PIP = $(VENV_BIN)/pip.exe
    ACTIVATE = $(VENV_BIN)/activate
else
    VENV_BIN = $(VENV)/bin
    PYTHON = $(VENV_BIN)/python
    PIP = $(VENV_BIN)/pip
    ACTIVATE = $(VENV_BIN)/activate
endif

# Source directories
SRC_DIRS = src tests web_app streamlit_app

# ==================================================================================
# MAIN TARGETS
# ==================================================================================

.DEFAULT_GOAL := help

.PHONY: help
help: ## 📖 Show this help message
	@echo "🚀 Job Finder - Available Commands"
	@echo "=================================="
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# ==================================================================================
# ENVIRONMENT SETUP
# ==================================================================================

.PHONY: install
install: $(VENV) ## 🔧 Install project in development mode
	$(PIP) install --upgrade pip setuptools wheel
	$(PIP) install -e ".[dev]"
	@echo "✅ Development environment ready!"

.PHONY: install-prod
install-prod: $(VENV) ## 🏭 Install project for production
	$(PIP) install --upgrade pip setuptools wheel
	$(PIP) install -e .
	@echo "✅ Production environment ready!"

$(VENV): ## 🐍 Create virtual environment
	python -m venv $(VENV)
	$(PIP) install --upgrade pip
	@echo "✅ Virtual environment created at $(VENV)"

.PHONY: clean-venv
clean-venv: ## 🧹 Remove virtual environment
	rm -rf $(VENV)
	@echo "✅ Virtual environment removed"

# ==================================================================================
# DEVELOPMENT TOOLS
# ==================================================================================

.PHONY: format
format: ## 🎨 Format code with black and isort
	$(PYTHON) -m black $(SRC_DIRS)
	$(PYTHON) -m isort $(SRC_DIRS)
	@echo "✅ Code formatted"

.PHONY: format-check
format-check: ## 🔍 Check code formatting without making changes
	$(PYTHON) -m black --check $(SRC_DIRS)
	$(PYTHON) -m isort --check-only $(SRC_DIRS)

.PHONY: lint
lint: ## 🔬 Run linting with pylint and ruff
	$(PYTHON) -m pylint $(SRC_DIRS)
	$(PYTHON) -m ruff check $(SRC_DIRS)
	@echo "✅ Linting completed"

.PHONY: type-check
type-check: ## 🔍 Run type checking with mypy
	$(PYTHON) -m mypy src/$(PACKAGE)
	@echo "✅ Type checking completed"

.PHONY: security
security: ## 🔒 Run security checks with bandit
	$(PYTHON) -m bandit -r src/$(PACKAGE)
	@echo "✅ Security check completed"

.PHONY: check-all
check-all: format-check lint type-check security ## 🧪 Run all code quality checks
	@echo "✅ All checks passed!"

# ==================================================================================
# TESTING
# ==================================================================================

.PHONY: test
test: ## 🧪 Run tests with pytest
	$(PYTHON) -m pytest tests/ -v --tb=short

.PHONY: test-cov
test-cov: ## 📊 Run tests with coverage report
	$(PYTHON) -m pytest tests/ --cov=src/$(PACKAGE) --cov-report=html --cov-report=term-missing

.PHONY: test-fast
test-fast: ## ⚡ Run tests without coverage (faster)
	$(PYTHON) -m pytest tests/ -x -q

.PHONY: test-watch
test-watch: ## 👀 Run tests in watch mode
	$(PYTHON) -m pytest-watch tests/

# ==================================================================================
# KEDRO PIPELINE
# ==================================================================================

.PHONY: run
run: ## 🏃 Run Kedro pipeline
	$(PYTHON) -m kedro run

.PHONY: run-pipeline
run-pipeline: ## 🏃 Run specific Kedro pipeline (use PIPELINE=name)
	$(PYTHON) -m kedro run --pipeline=$(PIPELINE)

.PHONY: kedro-viz
kedro-viz: ## 📊 Launch Kedro-Viz
	$(PYTHON) -m kedro viz --autoreload

.PHONY: kedro-jupyter
kedro-jupyter: ## 📓 Start Jupyter with Kedro context
	$(PYTHON) -m kedro jupyter notebook

# ==================================================================================
# WEB APPLICATIONS
# ==================================================================================

.PHONY: api
api: ## 🚀 Start FastAPI backend server
	cd web_app/backend && $(PYTHON) -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

.PHONY: web
web: ## 🌐 Start Streamlit frontend
	$(PYTHON) -m streamlit run web_app/frontend/app.py

.PHONY: web-streamlit-app
web-streamlit-app: ## 🌐 Start standalone Streamlit app
	$(PYTHON) -m streamlit run streamlit_app/app.py

# ==================================================================================
# DOCKER
# ==================================================================================

.PHONY: docker-build
docker-build: ## 🐳 Build all Docker images
	docker build -f fastapi.Dockerfile -t job-finder-api .
	docker build -f streamlit.Dockerfile -t job-finder-web .
	docker build -f kedro.Dockerfile -t job-finder-kedro .

.PHONY: docker-run-api
docker-run-api: ## 🐳 Run FastAPI container
	docker run -p 8000:8000 job-finder-api

.PHONY: docker-run-web
docker-run-web: ## 🐳 Run Streamlit container
	docker run -p 8501:8501 job-finder-web

.PHONY: docker-compose-up
docker-compose-up: ## 🐳 Start all services with docker-compose
	docker-compose up -d

.PHONY: docker-compose-down
docker-compose-down: ## 🐳 Stop all services
	docker-compose down

# ==================================================================================
# DATABASE & STORAGE
# ==================================================================================

.PHONY: setup-s3
setup-s3: ## ☁️ Setup S3 buckets (requires AWS CLI)
	@echo "Setting up S3 buckets..."
	# Add your S3 setup commands here

.PHONY: backup-data
backup-data: ## 💾 Backup data to S3
	$(PYTHON) -c "from src.$(PACKAGE).utils import backup_to_s3; backup_to_s3()"

# ==================================================================================
# UTILITIES
# ==================================================================================

.PHONY: clean
clean: ## 🧹 Clean build artifacts and cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ .coverage htmlcov/ .pytest_cache/ .ruff_cache/
	@echo "✅ Cleaned build artifacts"

.PHONY: deps-update
deps-update: ## 📦 Update dependencies
	$(PIP) install --upgrade pip setuptools wheel
	$(PIP) list --outdated

.PHONY: deps-tree
deps-tree: ## 🌳 Show dependency tree
	$(PYTHON) -m pipdeptree

.PHONY: notebook
notebook: ## 📓 Start Jupyter notebook server
	$(PYTHON) -m jupyter notebook

.PHONY: lab
lab: ## 🧪 Start JupyterLab server
	$(PYTHON) -m jupyter lab

# ==================================================================================
# CI/CD
# ==================================================================================

.PHONY: ci
ci: install check-all test-cov ## 🤖 Run full CI pipeline locally
	@echo "✅ CI pipeline completed successfully!"

.PHONY: pre-commit
pre-commit: format lint test-fast ## 🔄 Run pre-commit checks
	@echo "✅ Pre-commit checks passed!"

# ==================================================================================
# DOCUMENTATION
# ==================================================================================

.PHONY: docs
docs: ## 📚 Build documentation
	cd docs && make html

.PHONY: docs-serve
docs-serve: ## 📚 Serve documentation locally
	cd docs && python -m http.server 8080

# ==================================================================================
# ALIASES FOR CONVENIENCE
# ==================================================================================

.PHONY: dev
dev: install ## 🔧 Alias for install

.PHONY: start
start: web ## 🌐 Alias for web

.PHONY: fmt
fmt: format ## 🎨 Alias for format

.PHONY: check
check: check-all ## 🧪 Alias for check-all


