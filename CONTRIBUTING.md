# Contributing to Job Finder

Thank you for your interest in contributing to Job Finder! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- [uv](https://docs.astral.sh/uv/) package manager
- Git
- Redis (for caching, not mandatory)

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/armandmasseaugit/job_finder.git
   cd job_finder
   ```

2. **Install the project with development dependencies**
   ```bash
   make install
   ```


3. **Set up environment variables**

    If you want to run the project on **Azure** (remote ChromaDB, Azure Storage, etc.):

    - Copy the example environment file and fill in your credentials:
       ```bash
       cp .env.example .env
       # Then edit .env and fill in your Azure Storage, email, and ChromaDB info
       ```
    - This is only required for Azure/production deployments. If you are running everything locally, you can ignore `.env.example`.

    - To run the Kedro pipeline locally (with local files and local ChromaDB):
       - Open `conf/local/catalog.yml`,
       - Copy the relevant (uncommented) dataset definitions,
       - Paste them into `conf/base/catalog.yml` to replace the Azure-based configuration.
       - This will make the pipeline use local files and local ChromaDB instead of Azure resources.

    **Note:** Never commit your real `.env` file to version control.

4. **Start Redis (required for caching)**
   ```bash
   make redis-start
   ```

### Running the Application

All commands are available through the Makefile. Use `make help` to see all available commands.

#### Main Development Commands

```bash
# Install dependencies
make install

# Start the backend API (port 8000)
make backend

# Start the modern frontend (port 8080)
make frontend

# Run all the Kedro pipelines
make run
# Or run a specific one
make run ADD_OPTS="--pipeline=wttj_scraping"
make run ADD_OPTS="--pipeline=job_embedding"

# Run tests
make test
make test-cov  # with coverage report

# Code quality
make format    # Format code with black and isort
make lint      # Run linting with ruff

# Launch Kedro visualization
make kedro-viz

# Start Jupyter notebook
make notebook
```

#### Utility Commands

```bash
# Clean build artifacts
make clean

# Add dependencies
make deps-add DEP=package_name
make deps-add-dev DEP=package_name

# Remove virtual environment
make clean-venv
```

## 🏗️ Project Structure

```
job_finder/
├── src/job_finder/           # Main application code
│   ├── pipelines/           # Kedro data pipelines
│   │   ├── wttj_scraping/   # Web scraping pipeline
│   │   ├── job_embedding/   # ML embedding pipeline
│   │   └── score_relevance/ # Relevance scoring
│   └── utils.py             # Utility functions
├── web_app/                 # Web application
│   ├── backend/             # FastAPI backend
│   ├── frontend/            # Streamlit frontend
│   └── modern_frontend/     # Modern web frontend
├── conf/                    # Configuration files
├── data/                    # Data storage
└── tests/                   # Test suite
```

## 🔄 Development Workflow

### Branch Strategy

We follow a feature branch workflow:

1. **Create a feature branch** from `main`
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the coding standards below

3. **Test your changes**
   ```bash
   make test
   ```

4. **Commit your changes** using conventional commits
   ```bash
   git commit -m "feat: add new job matching algorithm"
   ```

5. **Push and create a Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```

### Branch Naming Convention

| Type      | Purpose                                     | Example                    |
|-----------|---------------------------------------------|----------------------------|
| `feature` | New features or enhancements               | `feature/cv-matching`      |
| `fix`     | Bug fixes                                  | `fix/broken-scraping`      |
| `hotfix`  | Urgent production fixes                    | `hotfix/critical-security` |
| `chore`   | Maintenance tasks                          | `chore/update-deps`        |
| `refactor`| Code restructuring                         | `refactor/pipeline-cleanup`|

### Commit Message Convention

We use [Conventional Commits](https://www.conventionalcommits.org/):

| Type       | Purpose                          | Example                              |
|------------|----------------------------------|--------------------------------------|
| `feat`     | New feature                      | `feat: add CV upload functionality`  |
| `fix`      | Bug fix                          | `fix: correct job scoring algorithm` |
| `docs`     | Documentation changes            | `docs: update API documentation`     |
| `style`    | Code formatting                  | `style: format Python files`        |
| `refactor` | Code restructuring               | `refactor: simplify scraping logic`  |
| `test`     | Test additions/updates           | `test: add CV matching tests`        |
| `chore`    | Maintenance tasks                | `chore: update dependencies`         |
| `perf`     | Performance improvements         | `perf: optimize embedding pipeline`  |

## 🧪 Testing

### Running Tests

```bash
# Run all tests
make test

# Run specific test files
python -m pytest tests/test_specific_module.py

# Run tests with coverage
python -m pytest --cov=src/job_finder tests/
```

### Writing Tests

- Place tests in the `tests/` directory
- Mirror the source structure: `tests/src/job_finder/`
- Use descriptive test names: `test_cv_matching_returns_top_jobs()`
- Include both unit and integration tests
- Run tests with `make test` or `make test-cov` for coverage

## 📝 Code Standards

### Python Code Style

- Follow [PEP 8](https://pep8.org/)
- Use type hints where possible
- Maximum line length: 88 characters (Black default)
- Use meaningful variable and function names
- Format code with `make format` before committing
- Check linting with `make lint`

### Frontend Code Style

- Use modern JavaScript (ES6+)
- Follow consistent naming conventions
- Comment complex logic
- Use semantic HTML

### Documentation

- Document all public functions and classes
- Include docstrings for modules, classes, and functions
- Update README when adding new features
- Include inline comments for complex logic


## 🚀 Local Development

The application runs on multiple ports:
- **Backend API**: http://localhost:8000 (`make backend`)
- **Modern Frontend**: http://localhost:3000 (`make frontend`)



## 📞 Getting Help

Feel free to contact me at : armand.masseau@gmail.com

- **Questions**: Open a discussion on GitHub
- **Bugs**: Create an issue with the bug template
- **Features**: Create an issue with the feature request template

---

Thank you for contributing to Job Finder! 🚀
