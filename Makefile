# ==================================================================================
# CONFIGURATION
# ==================================================================================

# Project configuration
VENV = .venv
PACKAGE = job_finder
PYTHON_VERSION = 3.9

# uv-based commands
PYTHON = uv run python
UV_SYNC = uv sync

# Source directories
SRC_DIRS = src tests web_app

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
install: ## 🔧 Install project with dev dependencies
	$(UV_SYNC) --extra dev
	@echo "✅ Development environment ready!"

.PHONY: install-prod
install-prod: ## 🏭 Install project for production
	$(UV_SYNC)
	@echo "✅ Production environment ready!"

.PHONY: clean-venv
clean-venv: ## 🧹 Remove virtual environment
	rm -rf $(VENV)
	rm -f uv.lock
	@echo "✅ Virtual environment and lock file removed"

# ==================================================================================
# CODE QUALITY
# ==================================================================================

.PHONY: format
format: ## 🎨 Format code with black and isort
	$(PYTHON) -m black $(SRC_DIRS)
	$(PYTHON) -m isort $(SRC_DIRS)
	@echo "✅ Code formatted"

.PHONY: lint
lint: ## 🔬 Run linting with ruff
	$(PYTHON) -m ruff check $(SRC_DIRS)
	@echo "✅ Linting completed"

.PHONY: test
test: ## 🧪 Run tests with pytest
	$(PYTHON) -m pytest tests/ -v

.PHONY: test-cov
test-cov: ## 📊 Run tests with coverage report
	$(PYTHON) -m pytest tests/ --cov=src/$(PACKAGE) --cov-report=html --cov-report=term-missing

# ==================================================================================
# KEDRO PIPELINE
# ==================================================================================
ADD_OPTS =
.PHONY: run
run: ## 🏃 Run Kedro pipeline
	$(PYTHON) -m kedro run $(ADD_OPTS)

.PHONY: kedro-viz
kedro-viz: ## 📊 Launch Kedro-Viz
	$(PYTHON) -m kedro viz --autoreload

# ==================================================================================
# WEB APPLICATIONS
# ==================================================================================

.PHONY: api
api: ## 🚀 Start FastAPI backend server
	cd web_app/backend && PYTHONPATH=../../:$$PYTHONPATH uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

.PHONY: web
web: ## 🌐 Start modern HTMX frontend
	cd web_app/modern_frontend && uv run python server.py


# ==================================================================================
# REDIS CACHE
# ==================================================================================

.PHONY: redis-start
redis-start: ## 🟥 Start Redis server
	sudo systemctl start redis-server
	@echo "✅ Redis server started"

# ==================================================================================
# DOCKER
# ==================================================================================

.PHONY: docker-build
docker-build: ## 🐳 Build all Docker images
	docker build -f fastapi.Dockerfile -t job-finder-api .
	docker build -f streamlit.Dockerfile -t job-finder-web .
	docker build -f kedro.Dockerfile -t job-finder-kedro .

.PHONY: docker-up
docker-up: ## 🐳 Start all services with docker-compose
	docker-compose up -d

.PHONY: docker-down
docker-down: ## 🐳 Stop all services
	docker-compose down

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

.PHONY: deps-add
deps-add: ## 📦 Add a new dependency (use DEP=package_name)
	uv add $(DEP)

.PHONY: deps-add-dev
deps-add-dev: ## 📦 Add a new dev dependency (use DEP=package_name)
	uv add --dev $(DEP)

.PHONY: notebook
notebook: ## 📓 Start Jupyter notebook server
	$(PYTHON) -m jupyter notebook

# ==================================================================================
# SHORTCUTS
# ==================================================================================

.PHONY: dev
dev: install ## 🔧 Alias for install

.PHONY: start
start: web ## 🌐 Alias for web

.PHONY: fmt
fmt: format ## 🎨 Alias for format
